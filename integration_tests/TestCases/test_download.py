from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By
from odex import settings


class DownloadTest(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_successful_download(self):
        '''--------------------------- login ---------------------------'''
        self.driver.get(self.live_server_url + "/login/")
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.ID, "btnLogin")

        username_input.send_keys("tester1")
        password_input.send_keys("123")
        login_button.click()
        '''--------------------------- login ---------------------------'''

        wait = WebDriverWait(self.driver, 20)
        '''--------------------------- create experiment ---------------------------'''

        # runname_input = self.driver.find_element(By.NAME, 'run_name')
        # file_input = self.driver.find_element(By.NAME, 'main_file')
        # add_button = self.driver.find_element(By.ID, "btnAdd")
        # subit_button = self.driver.find_element(By.ID, "btnSave")
        #
        # add_button.click()
        # runname_input.send_keys("test_exp1")
        # file_input.send_keys(f"{settings.BASE_DIR}/integration_tests/Test_File/testcsv.csv")
        # subit_button.click()
        #
        self.driver.find_element(By.ID, 'btnAdd').click()

        self.driver.implicitly_wait(10)

        self.driver.find_element(By.NAME, 'run_name').send_keys('test_exp')

        self.driver.find_element(By.NAME, 'main_file').send_keys(
            f"{settings.BASE_DIR}/integration_tests/Test_File/testcsv.csv")

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

        '''--------------------------- show details ---------------------------'''
        add_button = wait.until(EC.element_to_be_clickable((By.CLASS_NAME, 'btn-details')))

        add_button.click()

        # to the result page
       #assert self.driver.current_url == self.live_server_url + "/result/"

        self.driver.find_element(By.ID, "download1").click()

        '''--------------------------- show details ---------------------------'''
