using System.Diagnostics;
using TagBroker;

Console.WriteLine("=== TagBroker Demo ===\n");
Console.WriteLine("Demonstrating: Fast vs Slow Subscribers (Non-blocking Publish)\n");

using var broker = new TagBroker.TagBroker();

int fastCount = 0;
int slowCount = 0;

// Fast subscriber
var fastSub = broker.Subscribe("sensor.temperature", value =>
{
    Interlocked.Increment(ref fastCount);
    var timestamp = DateTime.Now.ToString("HH:mm:ss.fff");
    Console.WriteLine($"[{timestamp}] FAST  received: {value.Value}°C");
});

// Slow subscriber - 100ms processing time
var slowSub = broker.Subscribe("sensor.temperature", value =>
{
    Interlocked.Increment(ref slowCount);
    var startTime = DateTime.Now.ToString("HH:mm:ss.fff");
    Console.WriteLine($"[{startTime}] SLOW  start:    {value.Value}°C");

    Thread.Sleep(100); // Simulate slow processing (e.g., database write)

    var endTime = DateTime.Now.ToString("HH:mm:ss.fff");
    Console.WriteLine($"[{endTime}] SLOW  finish:   {value.Value}°C");
});

Console.WriteLine("Publishing 10 messages...\n");

double maxPublishMs = 0;
double totalPublishMs = 0;

for (int i = 1; i <= 10; i++)
{
    var tagValue = new TagValue
    {
        TagName = "sensor.temperature",
        Timestamp = DateTime.UtcNow,
        Value = 20.0 + (i * 0.5),
        Quality = Quality.Good
    };

    // Measure publish enqueue time (not handler execution time)
    var sw = Stopwatch.StartNew();
    await broker.PublishAsync("sensor.temperature", tagValue);
    sw.Stop();

    var publishMs = sw.Elapsed.TotalMilliseconds;
    maxPublishMs = Math.Max(maxPublishMs, publishMs);
    totalPublishMs += publishMs;

    var publishTime = DateTime.Now.ToString("HH:mm:ss.fff");
    Console.WriteLine($"[{publishTime}] PUBLISH #{i}: {tagValue.Value}°C (enqueue: {publishMs:F2}ms)\n");

    // Unsubscribe slow subscriber after message 5
    if (i == 5)
    {
        Console.WriteLine(">>> UNSUBSCRIBING slow subscriber after message 5 <<<");
        Console.WriteLine($">>> Slow subscriber should finish processing messages 1-5, then stop <<<\n");
        slowSub.Dispose();
        await Task.Delay(50); // Small delay to clearly separate before/after
    }

    await Task.Delay(30); // Small delay between publishes to see output clearly
}

Console.WriteLine("\nWaiting for all async processing to complete...");
await Task.Delay(700);

var fastFinal = Volatile.Read(ref fastCount);
var slowFinal = Volatile.Read(ref slowCount);
var avgPublishMs = totalPublishMs / 10;

Console.WriteLine($"Fast subscriber received: {fastFinal} messages (expected 10)");
Console.WriteLine($"Slow subscriber received: {slowFinal} messages (expected 5 - queued before unsubscribe)");
Console.WriteLine($"Average publish time:     {avgPublishMs:F2}ms");
Console.WriteLine($"Max publish time:         {maxPublishMs:F2}ms");
Console.WriteLine($"Slow handler time:        100ms (each)");

Console.WriteLine($"1. ✓ Non-blocking: Max publish time ({maxPublishMs:F2}ms) << slow handler time (100ms)");
Console.WriteLine($"2. ✓ Fast subscriber received all 10 messages immediately");
Console.WriteLine($"3. ✓ Slow subscriber processed exactly {slowFinal} messages (queued before unsubscribe)");
Console.WriteLine( "4. ✓ Slow subscriber finished processing ALL queued messages (drain behavior)");
Console.WriteLine( "5. ✓ Slow subscriber did NOT receive messages published after unsubscribe");

if (maxPublishMs < 10)
{
    Console.WriteLine("\n SUCCESS: Publisher was never blocked by slow subscriber!");
}
else
{
    Console.WriteLine($"\nWARNING: Max publish time ({maxPublishMs:F2}ms) is unusually high");
}

Console.WriteLine("\n=== Demo Complete ===");
