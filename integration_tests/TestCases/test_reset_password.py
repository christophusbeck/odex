from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By


class test_reset_password(SeleniumTestCase):

    fixtures = ['user_tests.json']

    def valid_username(self):

        '''--------------------------- login ---------------------------'''
        login_url = 'http://127.0.0.1:8000/login'

        self.driver.get(login_url)

        valid_username = 'tester2'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        '''--------------------------- login ---------------------------'''


        self.driver.find_element(By.CLASS_NAME, 'dropdown-toggle').click()

        # cann't click a tag
        self.driver.get("http://127.0.0.1:8000/changepassword/")

        old_password = valid_password

        self.driver.find_element(By.NAME, 'old_password').send_keys(old_password)
        self.driver.find_element(By.ID, 'authenticate').click()

        # now in the secondary page of reset password

        new_password = '456'

        self.driver.find_element(By.NAME, 'new_password').send_keys(new_password)
        self.driver.find_element(By.NAME, 'repeat_password').send_keys(new_password)

        self.driver.find_element(By.ID, 'create').click()

        '''--------------------------- retry login ---------------------------'''
        #
        login_url = 'http://127.0.0.1:8000/login'

        self.driver.get(login_url)

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(new_password)

        self.driver.find_element(By.ID, 'btnLogin').click()

        # now should on the main page

        '''--------------------------- tear down ---------------------------'''
        self.driver.find_element(By.CLASS_NAME, 'dropdown-toggle').click()

        # cann't click a tag
        self.driver.get("http://127.0.0.1:8000/changepassword/")

        old_password = new_password

        self.driver.find_element(By.NAME, 'old_password').send_keys(old_password)
        self.driver.find_element(By.ID, 'authenticate').click()

        # now in the secondary page of reset password

        new_password = '123'

        self.driver.find_element(By.NAME, 'new_password').send_keys(new_password)
        self.driver.find_element(By.NAME, 'repeat_password').send_keys(new_password)

        self.driver.find_element(By.ID, 'create').click()
