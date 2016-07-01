class ItemAttrs:
    """Access an object's items using attribute syntax.

    Example usage: `env = ItemAttrs(os.environ)`
    """

    def __init__(self, items):
        super().__setattr__('_items', items)

    def __getattr__(self, name):
        return self._items[name]

    def __setattr__(self, name, value):
        self._items[name] = value

    def __delattr__(self, name):
        del self._items[name]
