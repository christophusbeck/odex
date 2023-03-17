from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By


class test_deleteAccount(SeleniumTestCase):

    fixtures = ['user_tests.json']

    def delete(self):

        '''--------------------------- login ---------------------------'''
        login_url = self.live_server_url + "/login/"

        self.driver.get(login_url)

        valid_username = 'tester1'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        '''--------------------------- delete ---------------------------'''

        self.driver.find_element(By.CLASS_NAME, 'dropdown-toggle').click()

        delete_url = self.live_server_url + "/user/delete/"

        self.driver.get(delete_url)
        '''--------------------------- check:invalid login ---------------------------'''
        login_url = self.live_server_url + "/login/"

        self.driver.get(login_url)

        valid_username = 'tester1'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        
        error_info = "password error"
        # password error
        assert self.driver.find_element(By.ID, 'hint_info').text == error_info
        assert self.driver.current_url == login_url