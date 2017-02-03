class cached_property:
    """Convert a method into a cached property."""

    def __init__(self, method):
        self.__wrapped__ = method

    def __get__(self, instance, cls):
        if instance is None:
            return self
        attrs = instance.__dict__
        try:
            return attrs[self.__wrapped__.__name__]
        except KeyError:
            result = self.__wrapped__(instance)
            attrs[self.__wrapped__.__name__] = result
            return result

    def __set__(self, instance, value):
        if instance is None:
            raise NotImplementedError
        instance.__dict__[self.__wrapped__.__name__] = value

    def __delete__(self, instance):
        if instance is None:
            raise NotImplementedError
        del instance.__dict__[self.__wrapped__.__name__]
