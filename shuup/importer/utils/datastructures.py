

def copy_update(orig, **kwargs):
    copied = orig.copy()
    copied.update(kwargs)
    return copied
