def call(*args, **kwargs):
    def decorator(callable):
        return callable(*args, **kwargs)
    return decorator


magic = call()


def combine(*funcs):
    def multifunc(*args, **kwargs):
        return [func(*args, **kwargs) for func in funcs]
    return multifunc
