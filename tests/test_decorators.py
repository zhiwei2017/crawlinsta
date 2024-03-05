from crawlinsta.decorators import driver_implicit_wait
from unittest import mock


def test_driver_implicit_wait():
    driver = mock.Mock()
    driver.implicitly_wait = mock.Mock()
    seconds = 10

    @driver_implicit_wait(seconds)
    def test_function(driver):
        pass

    test_function(driver)
    driver.implicitly_wait.assert_called_once_with(seconds)
