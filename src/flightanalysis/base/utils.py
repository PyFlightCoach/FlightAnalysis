



def combine_args(names: list[str], *args, **kwargs) -> dict:
    """Combine the args and kwargs into a dict with the names as keys"""
    _kwargs = {}
    for i, n in enumerate(names):
        if i < len(args):
            _kwargs[n] = args[i]
        if n in kwargs:
            _kwargs[n] = kwargs[n]
    return _kwargs


