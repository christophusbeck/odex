from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By


class test_deleteAccount(SeleniumTestCase):

    fixtures = ['user_tests.json']

    def delete(self):

        '''--------------------------- login ---------------------------'''
        login_url = 'http://127.0.0.1:8000/login'

        self.driver.get(login_url)

        valid_username = 'tester1'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        '''--------------------------- login ---------------------------'''


        self.driver.find_element(By.CLASS_NAME, 'dropdown-toggle').click()

        self.driver.get("http://127.0.0.1:8000/user/delete/")