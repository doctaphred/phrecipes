class lazyattr:
    """Non-data descriptor which replaces itself with an instance attribute.

    >>> class LazyBoy:
    ...    @lazyattr
    ...    def ayy(self):
    ...        print('ayy')
    ...        return 'lmao'
    >>> boy = LazyBoy()
    >>> vars(boy)
    {}
    >>> boy.ayy
    ayy
    'lmao'
    >>> vars(boy)
    {'ayy': 'lmao'}
    >>> boy.ayy
    'lmao'
    >>> del boy.ayy
    >>> boy.ayy
    ayy
    'lmao'
    """
    def __init__(self, method):
        self.method = method

    def __set_name__(self, owner, name):
        # Called when `self` is set on `owner`.
        self.name = name

    def __get__(self, instance, owner):
        result = self.method(instance)
        setattr(instance, self.name, result)
        return result
