namespace TagBroker;

public interface ITagBroker : IDisposable
{
    IDisposable Subscribe(string tagName, Action<TagValue> handler);
    IDisposable SubscribeToMany(IEnumerable<string> tagNames, Action<TagValue> handler);
    Task PublishAsync(string tagName, TagValue value, CancellationToken cancellationToken = default);
}
