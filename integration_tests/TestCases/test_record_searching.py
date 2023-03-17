from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By
import time
from odex import settings


class test_searching(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_searching(self):
        '''--------------------------- login ---------------------------'''

        self.driver.get(self.live_server_url + "/login/")

        valid_username = 'tester2'
        valid_password = '123'

        self.driver.find_element(By.NAME, 'username').send_keys(valid_username)

        self.driver.find_element(By.NAME, 'password').send_keys(valid_password)

        self.driver.find_element(By.ID, 'btnLogin').click()
        '''--------------------------- login ---------------------------'''
        '''--------------------------- create experiment1 ---------------------------'''
        self.driver.find_element(By.ID, 'btnAdd').click()
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.NAME, 'run_name').send_keys('test_exp1')
        self.driver.find_element(By.NAME, 'main_file').send_keys(
            f"{settings.BASE_DIR}/integration_tests/Test_File/testcsv.csv")
        self.driver.find_element(By.ID, 'btnSave').click()
        time.sleep(2)
        # now in the conf page
        #assert self.driver.current_url == self.live_server_url + "/configuration/"
        # roll down the seit
        roll_down = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.execute_script(roll_down)
        self.driver.implicitly_wait(10)
        self.driver.implicitly_wait(10)
        # no other options, just use default setting
        self.driver.find_element(By.ID, "btnSave").click()
        time.sleep(2)
        assert self.driver.current_url == self.live_server_url + "/main/"
        '''--------------------------- create experiment1 ---------------------------'''
        '''--------------------------- successful searching ---------------------------'''
        # self.driver.find_element(By.CLASS_NAME, 'form-control.search-input').send_keys("test_exp1")
        # searched_exp = self.driver.find_element_by_css_selector('tr[data-index="0"]')
        # assert searched_exp.text == 'test_exp1'
        # self.driver.refresh()
        '''--------------------------- successful searching ---------------------------'''

        '''--------------------------- failed searching ---------------------------'''
        self.driver.find_element(By.CLASS_NAME, 'form-control.search-input').send_keys("test_exp2")
        error_message = self.driver.find_element(By.CLASS_NAME, "no-records-found")
        assert error_message.text == "No matching records found"
        '''--------------------------- failed searching ---------------------------'''


