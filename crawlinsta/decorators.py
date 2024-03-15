from functools import wraps


def driver_implicit_wait(seconds: int = 10):
    """Decorator to set the implicit wait of the driver before executing the function.

    Args:
        seconds (int, optional): The number of seconds to wait. Defaults to 10.

    Returns:
        function: The wrapped function

    Examples:
        >>> # Set the implicit wait of the driver to 10 seconds before executing the function
        >>> @driver_implicit_wait(10)
        ... def test_function(chrome_driver):
        ...     pass
    """
    def driver_implicit_wait_decorator(func):
        @wraps(func)
        def wrapped_function(driver, *args, **kwargs):
            driver.implicitly_wait(seconds)
            return func(driver, *args, **kwargs)
        return wrapped_function
    return driver_implicit_wait_decorator
