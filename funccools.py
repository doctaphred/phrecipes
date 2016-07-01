def combine(*funcs):
    def multifunc(*args, **kwargs):
        return [func(*args, **kwargs) for func in funcs]
    return multifunc
