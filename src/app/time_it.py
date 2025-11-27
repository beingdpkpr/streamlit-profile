import time
import functools


def timeit(fn):
    @functools.wraps(fn)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        print(f"{fn.__name__} → {(time.perf_counter() - start):.6f}s")
        return result

    return wrapper
