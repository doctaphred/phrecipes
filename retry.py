import logging
from functools import partial


log = logging.getLogger(__name__)


class TryAgain(Exception):
    """A function encountered an error, and should be called again."""


class GaveUp(Exception):
    """A function encountered multiple errors, and will not be retried."""


def call_with_retries(func=None, expect=TryAgain, fail=GaveUp, max_attempts=3):
    """Call a function until it succeeds.

    If the function returns a value, the value is returned.

    If it raises an exception of type ``expect``, the exception is
    caught and the call is retried.

    If it raises a different exception, the exception is not caught.

    If the function is called ``max_attempts`` times without returning
    a value, ``fail`` is called and the result is raised.

    This function may be used as a decorator, in order to specify a
    block of code which should be retried. In that case, the decorated
    function's name will be bound to its return value in the defining
    scope, and the function object will be destroyed. (Consider naming
    the decorated function ``_`` if its return value is not used.)

    Parameters
    ----------
    func : callable, optional
        A function to call, which may raise an exception of type
        ``expect`` if the call should be retried.
    expect : type or Tuple[type], optional
        Exception type (or types) which should be caught, and indicate
        that the function should be called again.
    max_attempts : int, optional
        The number of times to call ``func`` before giving up.
    fail : callable, optional
        Called and raised if the function repeatedly fails.
    """
    if max_attempts < 1:
        raise ValueError(max_attempts)

    # Allow this function to be used as a decorator.
    if func is None:
        return partial(
            call_with_retries,
            expect=expect,
            max_attempts=max_attempts,
        )

    for attempt in range(1, max_attempts + 1):
        log.info("Beginning attempt %s of %s", attempt, max_attempts)
        try:
            result = func()
        except expect:
            if attempt == max_attempts:
                retry_status = "giving up"
            else:
                retry_status = "will try again"
            log.info(
                "Encountered expected exception; %s", retry_status,
                exc_info=True,
            )
            continue
        except Exception:
            log.exception("Encountered unexpected exception; halting retries")
            raise
        else:
            log.info("Attempt %s succeeded", attempt)
            return result

    log.error("Gave up after %s attempt(s)", max_attempts)
    raise fail()


if __name__ == '__main__':
    import sys

    _, max_attempts, *instructions = sys.argv
    max_attempts = int(max_attempts)
    instructions = iter(instructions)

    logging.basicConfig(
        format=' '.join([
            # '[%(asctime)s]',
            '%(levelname)s',
            '%(pathname)s:%(lineno)d',
            '(%(funcName)s)',
            '%(message)s',
        ]),
        datefmt='%Y-%m-%dT%H:%M:%S',
        level='DEBUG',
    )

    try:
        @print
        @call_with_retries(max_attempts=max_attempts)
        def process_next_instruction():
            instruction = next(instructions)
            log.info("Processing instruction %r", instruction)
            if instruction == 'retry':
                raise TryAgain
            elif instruction == 'crash':
                raise Exception("oh no")
            else:
                return instruction
    except Exception:
        print("RIP")
