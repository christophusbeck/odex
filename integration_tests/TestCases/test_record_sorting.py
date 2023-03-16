from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By

from odex import settings


class test_sorting(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_successful_new_run(self):
        '''--------------------------- login ---------------------------'''
        login_url = 'http://127.0.0.1:8000/login'

        self.driver.get(login_url)

        valid_username = 'tester2'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        '''--------------------------- login ---------------------------'''

        table = self.driver.find_elements(By.XPATH, "//*[@id= 'record_table']/tbody")

        for row in table:
            print(row.text)

        print(table)