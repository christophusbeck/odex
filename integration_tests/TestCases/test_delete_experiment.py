from torchgen.selective_build import selector

from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By

from odex import settings


class test_successful_delete_experiment(SeleniumTestCase):

    fixtures = ['user_tests.json']

    def test_successful_delete(self):

        '''--------------------------- login ---------------------------'''
        login_url = 'http://127.0.0.1:8000/login'

        self.driver.get(login_url)

        valid_username = 'tester2'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        '''--------------------------- login ---------------------------'''

        '''--------------------------- create experiment ---------------------------'''
        self.driver.find_element(By.ID, 'btnAdd').click()

        self.driver.implicitly_wait(10)

        self.driver.find_element(By.NAME, 'run_name').send_keys('test_exp')

        self.driver.find_element(By.NAME, 'main_file').send_keys(f"{settings.BASE_DIR}/integration_tests/Test_File/userinput.csv")

        self.driver.find_element(By.ID, 'btnSave').click()

        # now in the conf page

        # roll down the seit
        roll_down = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.execute_script(roll_down)
        # no other options, just use default setting
        self.driver.find_element(By.ID, "btnSave").click()
        '''--------------------------- create experiment ---------------------------'''

        '''--------------------------- delete experiment ---------------------------'''

        # TODO: