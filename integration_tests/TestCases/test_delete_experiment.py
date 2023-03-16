
from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By

from odex import settings


class test_successful_delete_experiment(SeleniumTestCase):

    fixtures = ['user_tests.json']

    def test_successful_delete(self):

        '''--------------------------- login ---------------------------'''
        login_url = self.live_server_url + "/login/"

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

        self.driver.find_element(By.NAME, 'main_file').send_keys(f"{settings.BASE_DIR}/integration_tests/Test_File/testcsv.csv")


        self.driver.find_element(By.ID, 'btnSave').click()

        # now in the conf page

        # roll down the seit
        roll_down = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.execute_script(roll_down)

        self.driver.implicitly_wait(10)
        self.driver.implicitly_wait(10)

        # no other options, just use default setting
        self.driver.find_element(By.ID, "btnSave").click()
        '''--------------------------- create experiment ---------------------------'''

        # '''--------------------------- delete experiment ---------------------------'''
        self.driver.find_element(By.CLASS_NAME, 'btn-delete').click()

        self.driver.find_element(By.ID, 'btnConfirmDelete').click()

        # stay on the main page
        assert self.driver.current_url == self.live_server_url + "/main/"

        empty_info = "No matching records found"
        assert self.driver.find_element(By.CLASS_NAME, "no-records-found").text == empty_info

class test_interrupt_delete(SeleniumTestCase):

    fixtures = ['user_tests.json']

    def test_successful_delete(self):

        '''--------------------------- login ---------------------------'''
        login_url = self.live_server_url + "/login/"

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

        self.driver.find_element(By.NAME, 'main_file').send_keys(f"{settings.BASE_DIR}/integration_tests/Test_File/testcsv.csv")


        self.driver.find_element(By.ID, 'btnSave').click()

        # now in the conf page

        # roll down the seit
        roll_down = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.execute_script(roll_down)

        self.driver.implicitly_wait(10)
        self.driver.implicitly_wait(10)

        # no other options, just use default setting
        self.driver.find_element(By.ID, "btnSave").click()
        '''--------------------------- create experiment ---------------------------'''

        # '''--------------------------- delete experiment ---------------------------'''
        self.driver.find_element(By.CLASS_NAME, 'btn-delete').click()

        self.driver.find_element(By.ID, 'cancel').click()

        # # stay on the main page
        assert self.driver.current_url == self.live_server_url + "/main/"

        # which means the experiment is not deleted
        paging_info = "Showing 1 to 1 of 1 rows"
        assert self.driver.find_element(By.CLASS_NAME, 'pagination-info').text == paging_info