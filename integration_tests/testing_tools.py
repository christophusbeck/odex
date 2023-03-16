import platform

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
        
        # Automatically select the appropriate driver according to the system
        os = platform.system().lower()
        if "windows" in os:
            service = Service(f"./driver/chromedriver_win32/chromedriver")
        elif "linux" in os:
            service = Service(f"./driver/chromedriver_linux64/chromedriver")
        elif "darwin" in os:
            if "x86" in platform.platform():
                service = Service(f"./driver/chromedriver_mac64/chromedriver")
            else:
                service = Service(f"./driver/chromedriver_mac_arm64/chromedriver")
        else:
            return
                
        cls.driver = webdriver.Chrome(service=service, options=options)
        cls.driver.implicitly_wait(10)
        
    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()
        super().tearDownClass()
