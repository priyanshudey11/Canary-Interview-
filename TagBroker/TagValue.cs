namespace TagBroker;

public enum Quality
{
    Good,
    Bad,
    Uncertain
}

public sealed record TagValue
{
    public required string TagName { get; init; }
    public required DateTime Timestamp { get; init; }
    public required double Value { get; init; }
    public required Quality Quality { get; init; }
}
