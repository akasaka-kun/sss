def flatten(t: list):
    return [item for sublist in t for item in sublist]


def become(obj, obj2):
    obj.__dict__.update(obj2.__dict__)
