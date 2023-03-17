from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By


class Test_change_username_valid(SeleniumTestCase):

    fixtures = ['user_tests.json']

    def valid_username(self):

        '''--------------------------- login ---------------------------'''
        login_url = self.live_server_url + "/login/"

        self.driver.get(login_url)

        valid_username = 'tester1'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        '''--------------------------- login ---------------------------'''


        self.driver.find_element(By.CLASS_NAME, 'dropdown-toggle').click()

        changename_url = login_url = self.live_server_url + "/changename/"
        self.driver.get(changename_url)

        valid_username = 'tester3'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)
        self.driver.find_element(By.ID, 'create').click()

        # successful login
        assert self.driver.current_url == self.live_server_url + "/main/"

class Test_change_username_invalid(SeleniumTestCase):

    fixtures = ['user_tests.json']

    def invalid_name(self):

        '''--------------------------- login ---------------------------'''
        login_url = self.live_server_url + "/login/"

        self.driver.get(login_url)

        valid_username = 'tester1'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        '''--------------------------- login ---------------------------'''


        self.driver.find_element(By.CLASS_NAME, 'dropdown-toggle').click()

        changename_url = login_url = self.live_server_url + "/changename/"
        self.driver.get(changename_url)

        invalid_username = ' '

        self.driver.find_element(By.NAME, 'username').send_keys(invalid_username)
        self.driver.find_element(By.ID, 'create').click()

        # stay on the same page
        assert self.driver.current_url == self.live_server_url + "/changename/"
