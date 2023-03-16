from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By

from odex import settings


class test_successful_new_run(SeleniumTestCase):

    fixtures = ['user_tests.json']

    def test_successful_new_run(self):

        '''--------------------------- login ---------------------------'''
        login_url = self.live_server_url + "/login/"

        self.driver.get(login_url)

        valid_username = 'tester2'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        '''--------------------------- login ---------------------------'''

        self.driver.find_element(By.ID, 'btnAdd').click()

        self.driver.implicitly_wait(10)

        self.driver.find_element(By.NAME, 'run_name').send_keys('test_exp')

        self.driver.find_element(By.NAME, 'main_file').send_keys(f"{settings.BASE_DIR}/integration_tests/Test_File/testcsv.csv")

        self.driver.find_element(By.ID, 'btnSave').click()

        # now in the conf page

        self.driver.implicitly_wait(10)
        # roll down the seit
        roll_down = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.execute_script(roll_down)
        # no other options, just use default setting
        self.driver.find_element(By.ID, "btnSave").click()

        # redirect to the main page
        assert self.driver.current_url == self.live_server_url + "/main/"


class test_failed_new_run(SeleniumTestCase):

    fixtures = ['user_tests.json']

    def test_fail_with_not_csv_file(self):
        '''--------------------------- login ---------------------------'''
        login_url = self.live_server_url + "/login/"

        self.driver.get(login_url)

        valid_username = 'tester2'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        '''--------------------------- login ---------------------------'''

        self.driver.find_element(By.ID, 'btnAdd').click()

        self.driver.implicitly_wait(10)

        self.driver.find_element(By.NAME, 'run_name').send_keys('test_exp')

        self.driver.find_element(By.NAME, 'main_file').send_keys(f"{settings.BASE_DIR}/integration_tests/Test_File/scenarios.doc")

        self.driver.find_element(By.ID, 'btnSave').click()

        # stay on the main page
        assert self.driver.current_url == self.live_server_url + "/main/"

        error_info = "Unsupported file extension."

        hint_info =  self.driver.find_element(By.ID, 'main_file').text

        assert hint_info == error_info

        input()