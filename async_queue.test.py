from test_suite import test, expect
from async_queue import AsyncQueue
import uasyncio

async def collect_items(queue):
  items = []
  async for item in queue:
    items.append(item)
    # Break in test so as to not consume from the queue forever.
    if (queue.is_empty()):
     break
  return items

async def it_should_put_and_consume_items_in_the_queue():
  queue = AsyncQueue(10)
  queue.put('hello 1')
  queue.put(1)
  queue.put({'a': 1})
  queue.put(('tuple', 'test'))

  items = await collect_items(queue)

  expect(items).to_be(['hello 1', 1, {'a': 1}, ('tuple', 'test')])

async def it_should_discard_overflowed_items():
  queue = AsyncQueue(4)
  queue.put(1)
  queue.put(2)
  queue.put(3)
  queue.put(4)
  queue.put(5)
  queue.put(6)

  items = await collect_items(queue)

  # The oldest items, 1, 2 were discarded.
  expect(items).to_be([3, 4, 5, 6])
  expect(queue.discard_count).to_be(2)

async def it_should_enforce_a_min_capacity_of_3():
  queue = AsyncQueue(1)
  queue.put(1)
  queue.put(2)
  queue.put(3)
  queue.put(4)

  items = await collect_items(queue)

  expect(items).to_be([2, 3, 4])

uasyncio.run(
  test(
    it_should_put_and_consume_items_in_the_queue,
    it_should_discard_overflowed_items,
    it_should_enforce_a_min_capacity_of_3
  )
)