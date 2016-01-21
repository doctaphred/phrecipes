import signal
import sys
from contextlib import contextmanager
from textwrap import dedent


@contextmanager
def handle(signalnum, temp_handler=signal.SIG_DFL):
    """Temporarily set the signal's handler function."""
    prev_handler = signal.getsignal(signalnum)
    signal.signal(signalnum, temp_handler)
    try:
        yield
    finally:
        signal.signal(signalnum, prev_handler)


def sysexit(signum, frame):
    print("\nExiting immediately. Please remember to clean up after yourself!")
    sys.exit(1)


def prompt(cleanup_function):
    """Give the user a decision prompt when ctrl+C is pressed."""
    def cleanup_prompt(signum, frame):
        # Allow the user to exit immediately by
        # pressing ctrl+C again while in this block.
        with handle(signal.SIGINT, sysexit):
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
        print('Continuing...')

    return cleanup_prompt


def handle_ctrlc(cleanup_function):
    return handle(signal.SIGINT, prompt(cleanup_function))


if __name__ == '__main__':
    import time

    def main():
        while True:
            print('.')
            time.sleep(1)

    def cleanup():
        print('....................')

    with handle_ctrlc(cleanup):
        main()
