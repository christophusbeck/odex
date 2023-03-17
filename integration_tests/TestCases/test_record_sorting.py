from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By
import time
from odex import settings


class test_sorting(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_sorting(self):
        '''--------------------------- login ---------------------------'''
        login_url = 'http://127.0.0.1:8000/login'

        self.driver.get(login_url)

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
        # roll down the seit
        roll_down = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.execute_script(roll_down)
        self.driver.implicitly_wait(10)
        self.driver.implicitly_wait(10)
        # no other options, just use default setting
        self.driver.find_element(By.ID, "btnSave").click()
        time.sleep(2)
        '''--------------------------- create experiment1 ---------------------------'''
        '''--------------------------- create experiment2 ---------------------------'''
        self.driver.find_element(By.ID, 'btnAdd').click()
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.NAME, 'run_name').send_keys('test_exp2')
        self.driver.find_element(By.NAME, 'main_file').send_keys(
            f"{settings.BASE_DIR}/integration_tests/Test_File/testcsv.csv")
        self.driver.find_element(By.ID, 'btnSave').click()
        time.sleep(2)
        # now in the conf page
        # roll down the seit
        roll_down = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.execute_script(roll_down)
        self.driver.implicitly_wait(10)
        self.driver.implicitly_wait(10)
        # no other options, just use default setting
        self.driver.find_element(By.ID, "btnSave").click()
        time.sleep(2)
        '''--------------------------- create experiment2 ---------------------------'''
        '''--------------------------- create experiment3 ---------------------------'''
        self.driver.find_element(By.ID, 'btnAdd').click()
        self.driver.implicitly_wait(10)
        self.driver.find_element(By.NAME, 'run_name').send_keys('test_exp3')
        self.driver.find_element(By.NAME, 'main_file').send_keys(
            f"{settings.BASE_DIR}/integration_tests/Test_File/testcsv.csv")
        self.driver.find_element(By.ID, 'btnSave').click()
        time.sleep(2)
        # now in the conf page
        # roll down the seit
        roll_down = "window.scrollTo(0, document.body.scrollHeight)"
        self.driver.execute_script(roll_down)
        self.driver.implicitly_wait(10)
        self.driver.implicitly_wait(10)
        # no other options, just use default setting
        self.driver.find_element(By.ID, "btnSave").click()
        time.sleep(2)
        '''--------------------------- create experiment3 ---------------------------'''
        '''--------------------------- Sorting ---------------------------'''
        self.driver.find_element(By.XPATH, "/html/body/div[2]/div[1]/div[2]/div[2]/div[2]/table/thead/tr/th[2]/div[1]").click()
        time.sleep(2)
        '''--------------------------- Sorting ---------------------------'''