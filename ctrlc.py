import signal
import sys
from contextlib import contextmanager
from textwrap import dedent


_original_sigint = signal.getsignal(signal.SIGINT)


@contextmanager
def original_sigint():
    """Set SIGINT to its original value, then back to whatever it was set to.

    "original value" is the value defined when this module is loaded.
    """
    prev_sigint = signal.getsignal(signal.SIGINT)
    signal.signal(signal.SIGINT, _original_sigint)
    try:
        yield
    finally:
        signal.signal(signal.SIGINT, prev_sigint)


def register_cleanup_prompt(cleanup_function):
    """Give the user a decision prompt when ctrl+C is pressed."""
    def cleanup_prompt(signum, frame):
        # Allow the user to exit immediately by
        # pressing ctrl+C again while in this block.
        with original_sigint():
            try:
                choice = input(dedent("""
                    You pressed ctrl+C. What would you like to do?
                        - to exit immediately, press ctrl+C again
                        - to clean up and exit gracefully, enter 'c' or 'cleanup'
                        - to resume operation, press enter
                    (cleanup?): """
                    ))
                if choice and 'cleanup'.casefold().startswith(choice.casefold()):
                    print('Cleaning up...')
                    cleanup_function()
                    print('Done cleaning up; exiting.')
                    sys.exit(1)
            except KeyboardInterrupt:
                print("\nExiting immediately. Please remember to clean up after yourself!")
                sys.exit(1)
        print('Continuing...')

    signal.signal(signal.SIGINT, cleanup_prompt)


if __name__ == '__main__':
    import time

    def cleanup():
        print('....................')

    register_cleanup_prompt(cleanup)

    while True:
        print('.')
        time.sleep(1)
