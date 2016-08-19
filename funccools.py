def nop(*args, **kwargs):
    pass


def passthrough(x):
    return x


def generate(x):
    yield x


def call(*args, **kwargs):
    def decorator(callable):
        return callable(*args, **kwargs)
    return decorator


magic = call()


def combine(*funcs):
    def multifunc(*args, **kwargs):
        return [func(*args, **kwargs) for func in funcs]
    return multifunc


def only_when(condition):
    """Only apply a decorator if the condition is met.

    This function is designed as a decorator for other decorators
    ("re-decorator", perhaps?). If the given condition evaluates True,
    the decorated function is evaluated as usual, wrapping or replacing
    whatever functions it in turn decorates. If the condition evaluates
    False, though, it replaces the decorated function with a direct call
    to the function it wraps, bypassing evaluation of the decorated
    function altogether.

    This evaluation is only performed once, when the decorated function
    is first created (usually when the module is loaded); afterward, it
    adds zero overhead to the actual evaluation of the function.
    """
    def conditional(decorator):
        def redecorator(function):
            if condition:
                return decorator(function)
            else:
                return function
        return redecorator
    return conditional


only_when.csvoss_edition = lambda condition: (
    (lambda decorator: lambda function: decorator(function))
    if condition else
    (lambda decorator: lambda function: function)
)
