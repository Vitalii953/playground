def wrap_equal(func):
    """
    ====
    text
    ====
    """
    def wrapper(*args, **kwargs):
        print(f'\n{"="*40}')
        res = func(*args, **kwargs)
        print(f'{"="*40}\n')
        return res

    return wrapper


def wrap_hyphen(func):
    """
    ----
    text
    ----
    """
    def wrapper(*args, **kwargs):
        print(f'\n{"-"*40}')
        res = func(*args, **kwargs)
        print(f'{"-"*40}\n')
        return res

    return wrapper


def slow_print(text: str, delay: float = 0.05, hold: float = 1.5):
    import sys
    import time

    for char in text:
        sys.stdout.write(char)
        sys.stdout.flush()
        time.sleep(delay)
    print()
    
