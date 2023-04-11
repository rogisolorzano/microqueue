## Microqueue

An async circular queue using uasyncio, built for using with micropython.

## Usage
Just copy `async_queue.py` over to wherever you're using it.

There's a minifed version in `/release` if you'd prefer. The main `async_queue.py` is intentionally verbose.

Import the queue and initialize it with your desired capacity:
```
from async_queue import AsyncQueue

publish_queue = AsyncQueue(30)
```

Define the async function that will continuously process the queue:
```
async def process_publish_queue():
    global publish_queue

    async for message in publish_queue:
        print('Publishing message to MQTT broker', message)
```

Start it with uasyncio:
```
uasyncio.create_task(process_publish_queue())
```

Internally, `AsyncQueue` uses `uasyncio.Event` to wait until an item becomes available
in the queue. This yields to the scheduler, allowing us to consume from the queue
continuously without blocking the event loop.

When an item is put into queue, the scheduler will jump back to `process_publish_queue`
and it will start working through all the messages. Tip: you can always run
`await uasyncio.sleep(0)` to manually yield to the scheduler during queue processing.

## Full example
```
import uasyncio
from async_queue import AsyncQueue

publish_queue = AsyncQueue(30)

# Will continously process the queue.
async def process_publish_queue():
    global publish_queue

    async for message in publish_queue:
        print('Publishing message to MQTT broker', message)

# Simulating sensor readings.
async def handle_sensor_reading():
    global publish_queue

    while True:
        print('Received sensor reading, adding to publish queue')
        publish_queue.put('{"reading": 0.13342}')
        publish_queue.put('{"reading": 0.4342}')
        publish_queue.put('{"reading": 0.2334}')
        await uasyncio.sleep(2)

async def main():
    uasyncio.create_task(process_publish_queue())
    uasyncio.create_task(handle_sensor_reading())

    while True:
        await uasyncio.sleep(10000)

uasyncio.run(main())
```

## Near term roadmap
- Adding the ability to pause and resume the queue (useful for situations like pausing on WiFi disconnect then resuming on re-connection)
