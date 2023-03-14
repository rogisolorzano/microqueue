import uasyncio

class AsyncQueue:
  def __init__(self, capacity):
    # Size is capacity + 1. One item is allocated to the write pointer,
    # which points to the next item that will be overwritten.
    self._size = max(capacity + 1, 4)
    self._queue = [0 for _ in range(self._size)]
    self._item_added_event = uasyncio.Event()
    self._write_pointer = 0
    self._read_pointer = 0
    self.discard_count = 0

  def put(self, value):
    self._queue[self._write_pointer] = value
    self._item_added_event.set()
    self._move_write_pointer()
    will_overflow = self._write_pointer == self._read_pointer

    # If the next write index is equal to the next read index, this
    # indicates that an overflow will occur. We move the read index
    # forward one to "discard" the oldest item.
    if will_overflow:
      self._move_read_pointer()
      self.discard_count += 1

  # Increment write pointer, wrapping back around if necessary.
  def _move_write_pointer(self):
    self._write_pointer = (self._write_pointer + 1) % self._size

  # Increment read pointer, wrapping back around if necessary.
  def _move_read_pointer(self):
    self._read_pointer = (self._read_pointer + 1) % self._size

  # Whether the queue is empty.
  def is_empty(self):
    return self._write_pointer == self._read_pointer

  # Returns self as the async iterator.
  def __aiter__(self):
      return self

  # Gets the next async item. If the queue is empty, it will await until
  # another item is put into the queue. This allows us to consume the queue
  # continuously, without blocking the event loop.
  async def __anext__(self):
      if self.is_empty():
        self._item_added_event.clear()
        await self._item_added_event.wait()

      current = self._queue[self._read_pointer]
      self._move_read_pointer()

      return current