def coroutine(func):
    def start(*args, **kwargs):
        gen = func(*args, **kwargs)
        next(gen)
        return gen
    return start
