import time

from integration_tests.testing_tools import SeleniumTestCase


class RegistrationTest(SeleniumTestCase):
    def test_registration(self):
        self.driver.get(self.live_server_url + "/register/")

        # username_input = self.driver.find_element_by_name("username")

        # username_input.send_keys("tester1")

        time.sleep(10)