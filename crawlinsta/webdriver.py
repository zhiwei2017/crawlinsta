from seleniumwire.webdriver import Chrome  # noqa
from seleniumwire.webdriver import Edge  # noqa
from seleniumwire.webdriver import Firefox  # noqa
from seleniumwire.webdriver import Remote  # noqa
from seleniumwire.webdriver import Safari  # noqa

from selenium.webdriver.chrome.options import Options as ChromeOptions  # noqa
from selenium.webdriver.chrome.service import Service as ChromeService  # noqa
from selenium.webdriver.common.action_chains import ActionChains  # noqa
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities  # noqa
from selenium.webdriver.common.keys import Keys  # noqa
from selenium.webdriver.common.proxy import Proxy  # noqa
from selenium.webdriver.edge.options import Options as EdgeOptions  # noqa
from selenium.webdriver.edge.service import Service as EdgeService  # noqa
from selenium.webdriver.edge.webdriver import WebDriver as ChromiumEdge  # noqa
from selenium.webdriver.firefox.firefox_profile import FirefoxProfile  # noqa
from selenium.webdriver.firefox.options import Options as FirefoxOptions  # noqa
from selenium.webdriver.firefox.service import Service as FirefoxService  # noqa
from selenium.webdriver.safari.options import Options as SafariOptions  # noqa
from selenium.webdriver.safari.service import Service as SafariService  # noqa
from selenium.webdriver.webkitgtk.options import Options as WebKitGTKOptions  # noqa
from selenium.webdriver.webkitgtk.service import Service as WebKitGTKService  # noqa
from selenium.webdriver.webkitgtk.webdriver import WebDriver as WebKitGTK  # noqa
from selenium.webdriver.wpewebkit.options import Options as WPEWebKitOptions  # noqa
from selenium.webdriver.wpewebkit.service import Service as WPEWebKitService  # noqa
from selenium.webdriver.wpewebkit.webdriver import WebDriver as WPEWebKit  # noqa
from selenium.webdriver import __version__  # noqa

# We need an explicit __all__ because the above won't otherwise be exported.
__all__ = [
    "Firefox",
    "FirefoxProfile",
    "FirefoxOptions",
    "FirefoxService",
    "Chrome",
    "ChromeOptions",
    "ChromeService",
    "Edge",
    "ChromiumEdge",
    "EdgeOptions",
    "EdgeService",
    "Safari",
    "SafariOptions",
    "SafariService",
    "WebKitGTK",
    "WebKitGTKOptions",
    "WebKitGTKService",
    "WPEWebKit",
    "WPEWebKitOptions",
    "WPEWebKitService",
    "Remote",
    "DesiredCapabilities",
    "ActionChains",
    "Proxy",
    "Keys",
]
