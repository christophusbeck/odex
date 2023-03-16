import platform
import sys

from django.conf import settings
from selenium.webdriver.chrome.service import Service
from django.contrib.staticfiles.testing import StaticLiveServerTestCase
from selenium import webdriver


class SeleniumTestCase(StaticLiveServerTestCase):
    """
    All Selenium test cases inherit from the SeleniumTestCase class.
    SeleniumTestCase has the basic setUpClass and tearDownClass.
    """
    driver = None

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        options = webdriver.ChromeOptions()
        options.add_argument("--start-maximized")
        options.add_argument('--headless')

        # Automatically select the appropriate driver according to the system
        os = platform.system().lower()
        if "windows" in os:
            service = Service(f"{settings.BASE_DIR}/integration_tests/WebDrivers/chromedriver_win32/chromedriver")
        elif "linux" in os:
            service = Service(f"{settings.BASE_DIR}/integration_tests/WebDrivers/chromedriver_linux64/chromedriver")
        elif "darwin" in os:
            if "x86" in platform.platform():
                service = Service(f"{settings.BASE_DIR}/integration_tests/WebDrivers/chromedriver_mac64/chromedriver")
            else:
                service = Service(f"{settings.BASE_DIR}/integration_tests/WebDrivers/chromedriver_mac_arm64/chromedriver")
        else:
            return

        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()

    def tearDown(self):
        if sys.exc_info()[0]:
            test_method_name = self._testMethodName
            self.driver.save_screenshot("selenium-error-%s.png" % test_method_name)
        super().tearDown()
