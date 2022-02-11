def flatten(t: list):
    return [item for sublist in t for item in sublist]


def become(obj, obj2):
    obj.__dict__.update(obj2.__dict__)


from numpy import array_equal


def is_arr_in_list(arr, list_arrays, ret_all=False):
    # noinspection SpellCheckingInspection
    allr = (True for elem in list_arrays if array_equal(elem, arr))
    return next(allr, False) if not ret_all else allr
