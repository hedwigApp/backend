from functools import wraps


def autosave(fn):
    """
    Automatically run save() after the method exist
    """
    @wraps(fn)
    def decorated(self, *args, **kwargs):
        result = fn(self, *args, **kwargs)
        self.save()
        return result

    return decorated


class classproperty(property):
    def __get__(self, cls, owner):
        return self.fget.__get__(None, owner)()
