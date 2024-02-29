from functools import wraps


def driver_implicit_wait(seconds: int = 10):
    def driver_implicit_wait_decorator(func):
        @wraps(func)
        def wrapped_function(driver, *args, **kwargs):
            driver.implicitly_wait(seconds)
            return func(driver, *args, **kwargs)
        return wrapped_function
    return driver_implicit_wait_decorator


def non_negative_collect_number(func):
    @wraps(func)
    def wrapped_function(driver, param, n):
        if n < 0:
            raise ValueError("Parameter 'n' must be bigger than or equal to 0.")
        return func(driver, param, n)
    return wrapped_function
