import uasyncio as asyncio

class Expect:
  def __init__(self, value):
    self.value = value

  def to_be(self, expected):
    if (self.value != expected):
      raise Exception('Expected: {}\nReceived: {}'.format(expected, self.value))

  def to_have_been_called(self):
    if (len(self.value.calls) == 0):
      raise Exception('Spy has not been called.')

  def to_have_been_called_times(self, expected):
    count = len(self.value.calls)
    if (count != expected):
      raise Exception('Spy has been called {} times instead of the expected {}.'.format(count, expected))

class Spy:
  def __init__(self):
    self.return_value = None
    self.calls = []

  def returns(self, value):
    self.return_value = value
    return self

  def __call__(self, value):
    self.calls.append(value)
    return self.return_value

def spy():
  return Spy()

def expect(value):
    return Expect(value)

async def test(*functions):
    print('------------------------------------------------')

    for test_function in functions:
      name = test_function.__name__.replace("_", " ")

      try:
        await test_function()
        print('PASS', name)
      except Exception as e:
        print('FAIL', name)
        print(e)
    
    print('------------------------------------------------')