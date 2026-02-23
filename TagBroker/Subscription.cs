using System.Threading.Channels;

namespace TagBroker;

internal sealed class Subscription : IDisposable
{
    private readonly Action<TagValue> _handler;
    private readonly Channel<TagValue> _channel;
    private readonly Task _processingTask;
    private int _disposed;

    public Subscription(Action<TagValue> handler)
    {
        _handler = handler;
        _channel = Channel.CreateUnbounded<TagValue>();
        _processingTask = ProcessMessagesAsync();
    }

    public async ValueTask EnqueueAsync(TagValue value, CancellationToken cancellationToken)
    {
        try
        {
            // Fast path: try synchronous write first (avoids Task allocation)
            if (_channel.Writer.TryWrite(value))
                return;

            // Slow path: channel buffer full, use async write
            await _channel.Writer.WriteAsync(value, cancellationToken);
        }
        catch (ChannelClosedException)
        {
            // Subscription is disposed, silently ignore
        }
    }

    private async Task ProcessMessagesAsync()
    {
        // Read all messages from channel until it's completed
        // No cancellation token - we want to finish processing queued messages
        await foreach (var value in _channel.Reader.ReadAllAsync())
        {
            try
            {
                _handler(value);
            }
            catch
            {
                // Swallow handler exceptions to prevent one bad subscriber from crashing the broker
            }
        }
    }

    public void Dispose()
    {
        // Ensure idempotent disposal
        if (Interlocked.Exchange(ref _disposed, 1) == 1)
            return;

        // Complete the channel (no more writes)
        // ProcessMessagesAsync will finish draining queued messages
        _channel.Writer.Complete();

        // Best-effort wait for task to complete (finishes processing queue)
        try
        {
            _processingTask.Wait(TimeSpan.FromSeconds(1));
        }
        catch
        {
            // Ignore timeout or other errors during disposal
        }
    }
}
