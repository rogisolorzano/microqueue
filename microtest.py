import uasyncio
from sys import modules

class Expect:
  def __init__(self, value):
    self.value = value
    self._not = False

  @property
  def it_not(self):
    self._not = True
    return self

  def to_be(self, expected):
    if self._fails(self.value != expected):
      raise Exception(self._format('Expected: {n}{}\nReceived: {}', expected, self.value))

  def to_have_been_called(self):
    if self._fails(len(self.value.calls) == 0):
      raise Exception(self._format('Expected spy to {n}be called.'))

  def to_have_been_called_with(self, *expected_args, **expected_kwargs):
    has_expected = False
    call_tuple = (expected_args, expected_kwargs)

    for call in self.value.calls:
      has_expected = call == call_tuple
      if has_expected:
        break

    if self._fails(not has_expected):
      message = self._format('Expected spy to {n}have been called with: {}', self._format_call(call_tuple))
      if len(self.value.calls) == 0:
        message += '\nReceived 0 calls'
      else:
        message += '\nReceived calls:\n' + '\n'.join(self._format_calls(self.value.calls))
      raise Exception(message)

  def to_have_been_called_times(self, expected):
    count = len(self.value.calls)
    if self._fails(count != expected):
      raise Exception(self._format('Expected spy to {n}be called {} times. It was called {} times.', expected, count))

  def to_have_been_triggered(self):
    if self._fails(not self.value.triggered):
      raise Exception(self._format('Expected event to {n}be triggered.'))

  async def to_throw(self, exception = Exception):
    threw_expected = False

    try:
      await self.value()
    except Exception as caught_exception:
      threw_expected = exception.__name__ == type(caught_exception).__name__
      pass

    if self._fails(not threw_expected):
      raise Exception(self._format('Expected method to {n}throw a {}.', exception.__name__))

  def _fails(self, value):
    return not value if self._not else value

  def _format(self, str, *args):
    not_text = 'not ' if self._not else ''
    return str.format(*args, n = not_text)

  def _format_call(self, call):
    args_string = ', '.join(['{}'.format(value) for value in call[0]])
    kwargs_string = ', '.join('{}={}'.format(key, value) for key, value in call[1].items())
    return ', '.join(filter(lambda s : s != '', [args_string, kwargs_string]))
  
  def _format_calls(self, calls):
    return ['{}: {}'.format(i, self._format_call(c)) for i, c in enumerate(calls)]


class Spy:
  def __init__(self):
    self._return_value = None
    self._returns = []
    self.calls = []

  def returns(self, value):
    self._return_value = value
    return self

  def define_returns(self, *args):
    self._returns += list(args)
    return self

  def __call__(self, *args, **kwargs):
    self.calls.append((args, kwargs))
    return self._return_value if len(self._returns) == 0 else self._returns.pop(0)

class AsyncSpy(Spy):
  async def __call__(self, *args, **kwargs):
    self.calls.append((args, kwargs))
    return self._return_value if len(self._returns) == 0 else self._returns.pop(0)

class EventObserver:
  def __init__(self, event):
    self._event = event
    self._task = uasyncio.create_task(self._observer())
    self.triggered = False

  async def _observer(self):
    while not self.triggered:
      await self._event.wait()
      self._event.clear()
      self.triggered = True

  async def wait(self, timeout = 3):
    try:
      await uasyncio.wait_for(self._task, timeout)
    except:
      pass

def spy():
  return Spy()

def async_spy():
  return AsyncSpy()

def expect(value):
    return Expect(value)

def observe(event):
    return EventObserver(event)

original_modules = {}

def mock_module(module_name, mock):
  original_modules[module_name] = modules.get(module_name)
  modules[module_name] = mock

def restore_modules():
  for name, original in original_modules.items():
    modules[name] = original

async def test_runner(functions):
  print('\n------------------------------------------------')
  passed = 0
  failed = 0

  for test_function in functions:
    name = test_function.__name__.replace("_", " ")

    try:
      await test_function()
      print('> PASS', name)
      passed += 1
    except Exception as e:
      print('> FAIL', name)
      print(e)
      failed += 1
  
  print('\nSummary')
  print('-----------')
  print('Passed: {}'.format(passed))
  print('Failed: {}\n'.format(failed))

test_functions = []
only_function = []

def test(fn):
  global test_functions
  test_functions.append(fn)

# Convenience method during development to run only "this" test. Use in the same way as @test
def only(fn):
  global only_function
  only_function.append(fn)

def run():
  uasyncio.run(test_runner(test_functions if len(only_function) == 0 else only_function))
  restore_modules()