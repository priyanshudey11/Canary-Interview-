using Xunit;

namespace TagBroker.Tests;

public class TagBrokerTests
{
    [Fact]
    public async Task Publish_DeliversToSubscriber()
    {
        // Arrange
        using var broker = new global::TagBroker.TagBroker();
        TagValue? received = null;

        broker.Subscribe("test.tag", value => received = value);

        var publishedValue = new TagValue
        {
            TagName = "test.tag",
            Timestamp = DateTime.UtcNow,
            Value = 42.5,
            Quality = Quality.Good
        };

        // Act
        await broker.PublishAsync("test.tag", publishedValue);
        await Task.Delay(50); // Give async processing time to complete

        // Assert
        Assert.NotNull(received);
        Assert.Equal(publishedValue.TagName, received.TagName);
        Assert.Equal(publishedValue.Value, received.Value);
        Assert.Equal(publishedValue.Quality, received.Quality);
    }

    [Fact]
    public async Task Publish_DeliversToMultipleSubscribers()
    {
        // Arrange
        using var broker = new global::TagBroker.TagBroker();
        var received1 = new List<TagValue>();
        var received2 = new List<TagValue>();
        var received3 = new List<TagValue>();

        broker.Subscribe("sensor.temp", value => received1.Add(value));
        broker.Subscribe("sensor.temp", value => received2.Add(value));
        broker.Subscribe("sensor.temp", value => received3.Add(value));

        // Act - publish 5 messages
        for (int i = 0; i < 5; i++)
        {
            await broker.PublishAsync("sensor.temp", new TagValue
            {
                TagName = "sensor.temp",
                Timestamp = DateTime.UtcNow,
                Value = 20.0 + i,
                Quality = Quality.Good
            });
        }

        await Task.Delay(100); // Give async processing time

        // Assert - all subscribers received all messages
        Assert.Equal(5, received1.Count);
        Assert.Equal(5, received2.Count);
        Assert.Equal(5, received3.Count);

        // Verify values are correct
        for (int i = 0; i < 5; i++)
        {
            Assert.Equal(20.0 + i, received1[i].Value);
            Assert.Equal(20.0 + i, received2[i].Value);
            Assert.Equal(20.0 + i, received3[i].Value);
        }
    }

    [Fact]
    public async Task Unsubscribe_StopsReceiving_AndPublishDoesNotThrow()
    {
        // Arrange
        using var broker = new global::TagBroker.TagBroker();
        var receivedCount = 0;

        var subscription = broker.Subscribe("test.tag", value => Interlocked.Increment(ref receivedCount));

        // Act - publish first message
        await broker.PublishAsync("test.tag", CreateTagValue("test.tag", 1));
        await Task.Delay(50);

        var countAfterFirst = receivedCount;

        // Unsubscribe
        subscription.Dispose();
        await Task.Delay(50);

        // Publish more messages after unsubscribe
        await broker.PublishAsync("test.tag", CreateTagValue("test.tag", 2));
        await broker.PublishAsync("test.tag", CreateTagValue("test.tag", 3));
        await Task.Delay(50);

        var finalCount = receivedCount;

        // Assert
        Assert.Equal(1, countAfterFirst); // Received first message
        Assert.Equal(1, finalCount); // Did not receive messages 2 and 3
        // No exception was thrown from PublishAsync ✓
    }

    private static TagValue CreateTagValue(string tagName, double value)
    {
        return new TagValue
        {
            TagName = tagName,
            Timestamp = DateTime.UtcNow,
            Value = value,
            Quality = Quality.Good
        };
    }
}
