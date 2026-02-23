# TagBroker - Real-Time In-Memory Publisher/Subscriber


## Quick Start

```bash
# Prerequisites: .NET 8 SDK
brew install dotnet@8

# Clone and run
git clone https://github.com/priyanshudey11/Canary-Interview-.git
cd TagBroker

# Run tests 
cd TagBroker.Tests
dotnet test

# Run demo (proves non-blocking behavior)
cd ../TagBroker.Demo
dotnet run
```

## Expected Demo Output

```
Metrics 
Fast subscriber received: 10 messages (expected 10)
Slow subscriber received: 5 messages (expected 5)
Average publish time:     0.20ms
Max publish time:         0.98ms
Slow handler time:        100ms (each)

SUCCESS: Publisher was never blocked by slow subscriber!
```

**Key proof**: Publish takes **<1ms** while slow subscriber takes **100ms** → 100x non-blocking margin


## Project Structure

```
TagBroker/                  (Core Library - 216 lines)
├── ITagBroker.cs           8 lines  - Public interface
├── TagValue.cs            16 lines - Data model
├── Subscription.cs        73 lines - Per-subscriber channel + processing
└── TagBroker.cs          119 lines - Core broker logic

TagBroker.Demo/            (Console Demo)
└── Program.cs             Quantitative proof of non-blocking behavior

TagBroker.Tests/           (Unit Tests)
└── TagBrokerTests.cs      3 tests (100% passing)
```

## API Example

```csharp
using var broker = new TagBroker.TagBroker();

// Subscribe to a tag
var subscription = broker.Subscribe("sensor.temperature", value =>
{
    Console.WriteLine($"Temperature: {value.Value}°C");
});

// Publish a value (returns when enqueued, not when processed)
await broker.PublishAsync("sensor.temperature", new TagValue
{
    TagName = "sensor.temperature",
    Timestamp = DateTime.UtcNow,
    Value = 25.5,
    Quality = Quality.Good
});

// Unsubscribe (finishes processing queued messages)
subscription.Dispose();
```

## How It Works

### Architecture

```
Publisher
    ↓ PublishAsync() - writes to all channels concurrently
    ├─→ [Channel 1] → Background Task → Fast Handler   (1ms)
    └─→ [Channel 2] → Background Task → Slow Handler   (100ms)
        ↑ Publisher returns immediately (<1ms)
```

Each subscriber has:
- Unbounded `Channel<TagValue>` for message queuing
- Dedicated background `Task` for processing
- Independent execution (slow doesn't block fast)

### Key Design Decisions

**1. Channels over Events**
- Traditional events block caller until all handlers complete
- Channels decouple publish from handler execution
- Background tasks process at their own pace

**2. Unbounded Channels**
- Never block publisher (satisfies non-blocking requirement)
- Trade-off: memory growth if subscriber can't keep up
- Production: add monitoring and bounded channels with drop policies

**3. Queue Draining on Unsubscribe**
- Complete channel writer (no more writes)
- Background task finishes processing queued messages
- Clean shutdown, no data loss

## Running Tests

```bash
cd TagBroker.Tests
dotnet test
```

Expected: `Passed! - Failed: 0, Passed: 3, Skipped: 0, Total: 3`






# Canary-Interview-
