def flatten(t: list):
    return [item for sublist in t for item in sublist]


def become(obj, obj2):
    for k, v in obj.__dict__.items():
        obj2.__dict__[k] = v
