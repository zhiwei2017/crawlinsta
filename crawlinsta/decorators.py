from functools import wraps


def driver_implicit_wait(seconds: int = 10):
    def driver_implicit_wait_decorator(func):
        @wraps(func)
        def wrapped_function(driver, *args, **kwargs):
            driver.implicitly_wait(seconds)
            return func(driver, *args, **kwargs)
        return wrapped_function
    return driver_implicit_wait_decorator
