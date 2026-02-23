using System.Collections.Concurrent;

namespace TagBroker;

public sealed class TagBroker : ITagBroker
{
    // Map tag names to their subscribers
    private readonly ConcurrentDictionary<string, ConcurrentBag<Subscription>> _subscriptions = new();
    private bool _disposed;

    public IDisposable Subscribe(string tagName, Action<TagValue> handler)
    {
        ArgumentNullException.ThrowIfNull(tagName);
        ArgumentNullException.ThrowIfNull(handler);
        ObjectDisposedException.ThrowIf(_disposed, this);

        return SubscribeToMany(new[] { tagName }, handler);
    }

    public IDisposable SubscribeToMany(IEnumerable<string> tagNames, Action<TagValue> handler)
    {
        ArgumentNullException.ThrowIfNull(tagNames);
        ArgumentNullException.ThrowIfNull(handler);
        ObjectDisposedException.ThrowIf(_disposed, this);

        var subscription = new Subscription(handler);
        var tagList = tagNames.ToList();

        // Add subscription to all specified tags
        foreach (var tagName in tagList)
        {
            var subscribers = _subscriptions.GetOrAdd(tagName, _ => new ConcurrentBag<Subscription>());
            subscribers.Add(subscription);
        }

        // Return unsubscriber that disposes the subscription
        return new Unsubscriber(subscription);
    }

    public async Task PublishAsync(string tagName, TagValue value, CancellationToken cancellationToken = default)
    {
        ArgumentNullException.ThrowIfNull(tagName);
        ArgumentNullException.ThrowIfNull(value);
        ObjectDisposedException.ThrowIf(_disposed, this);

        // Try to get subscribers for this tag
        if (!_subscriptions.TryGetValue(tagName, out var subscribers))
        {
            return; // No subscribers, nothing to do
        }

        // Fan-out: enqueue message to all subscriber channels
        // Only allocate List if we have async operations (most writes are sync via TryWrite)
        List<Task>? tasks = null;

        foreach (var subscription in subscribers)
        {
            var valueTask = subscription.EnqueueAsync(value, cancellationToken);

            // Only track tasks that didn't complete synchronously
            if (!valueTask.IsCompletedSuccessfully)
            {
                (tasks ??= new List<Task>()).Add(valueTask.AsTask());
            }
        }

        // Wait for any async enqueue operations to complete
        if (tasks is not null)
        {
            await Task.WhenAll(tasks);
        }
    }

    public void Dispose()
    {
        if (_disposed) return;
        _disposed = true;

        // Track unique subscriptions to avoid double-dispose
        // (SubscribeToMany adds same subscription to multiple tags)
        var uniqueSubscriptions = new HashSet<Subscription>();

        foreach (var subscribers in _subscriptions.Values)
        {
            foreach (var subscription in subscribers)
            {
                uniqueSubscriptions.Add(subscription);
            }
        }

        // Dispose each subscription once
        foreach (var subscription in uniqueSubscriptions)
        {
            subscription.Dispose();
        }

        _subscriptions.Clear();
    }

    // Simple unsubscriber that just disposes the subscription
    private sealed class Unsubscriber : IDisposable
    {
        private readonly Subscription _subscription;
        private int _disposed;

        public Unsubscriber(Subscription subscription)
        {
            _subscription = subscription;
        }

        public void Dispose()
        {
            if (Interlocked.Exchange(ref _disposed, 1) == 0)
            {
                _subscription.Dispose();
            }
        }
    }
}
