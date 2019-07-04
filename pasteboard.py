from subprocess import run


@type.__call__
class copy:
    def __call__(self, obj):
        run(['pbcopy'], input=str(obj), text=True)

    __ror__ = __call__  # Pipe!


def paste():
    return run(['pbpaste'], capture_output=True, text=True).stdout
