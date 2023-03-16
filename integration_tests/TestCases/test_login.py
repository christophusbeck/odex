import time

from selenium.webdriver.support.ui import Select

from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By


class Valid_login(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_valid_login(self):
        login_url = 'http://127.0.0.1:8000/login'

        self.driver.get(login_url)

        valid_username = 'tester1'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()

        return valid_username


class Invalid_login(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_invalid_login(self):
        login_url = 'http://127.0.0.1:8000/login'

        self.driver.get(login_url)

        valid_username = 'tester1'
        valid_password = '123'

        invalid_username = 'false'
        invalid_password = 'false'

        '''--------------------------- valid username with invalid password ---------------------------'''
        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(invalid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()

        self.driver.implicitly_wait(10)

        # password error
        print(self.driver.find_element(By.ID, 'hint_invalid_password').text)

        '''--------------------------- invalid username with valid password ---------------------------'''
        self.driver.find_element(By.ID, 'username').send_keys(invalid_username)

        self.driver.find_element(By.ID, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()

        self.driver.implicitly_wait(10)

        # password error
        print(self.driver.find_element(By.ID, 'hint_invalid_password').text)

