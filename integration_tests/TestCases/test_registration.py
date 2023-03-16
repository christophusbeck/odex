import time

from selenium.webdriver.support.ui import Select

from integration_tests.testing_tools import SeleniumTestCase
from selenium.webdriver.common.by import By


class RegistrationSuccessfulTest(SeleniumTestCase):
    """
    This is a sample for Selenium testing.

    All Selenium test cases inherit from the SeleniumTestCase class.
    SeleniumTestCase has the basic setUpClass and tearDownClass.

    [Using]
        self.driver
    can perform browser-related operations.

    [Using]
        self.driver.find_element(By.NAME, "name")
    to create an instance for html label.
    For more information on find_element() function
    see: https://stackoverflow.com/questions/69875125/find-element-by-commands-are-deprecated-in-selenium

    [Using]
        time.sleep(2)
    to wait a response from server.
    """

    # Load fixtures to use default data
    fixtures = ['user_tests.json']

    def test_successful_registration(self):
        """
        A basic and successful registration action with checking existed username.

        Because username in our application must be unique, and real-time ajax request
        for checking the username improves user experience
        """

        self.driver.get(self.live_server_url + "/register/")

        # the instances of html label
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        repeat_password_input = self.driver.find_element(By.NAME, "repeat_password")
        question_select = Select(self.driver.find_element(By.ID, "id_question"))
        answer_input = self.driver.find_element(By.NAME, "answer")
        tan_input = self.driver.find_element(By.NAME, "tan")
        create_button = self.driver.find_element(By.ID, "create")

        # enter an existed username
        username_input.send_keys("tester1")
        password_input.click()
        time.sleep(0.5)

        # reenter a not-existed username
        username_input.clear()
        username_input.send_keys("test")
        password_input.send_keys("123")
        repeat_password_input.send_keys("123")
        question_select.select_by_value("2")
        answer_input.send_keys("cat")
        tan_input.send_keys("124")

        create_button.click()

        time.sleep(2)


class RegistrationWithEmptyEntries(SeleniumTestCase):

    def test_registration_with_empty_entries(self):
        self.driver.get(self.live_server_url + "/register/")
        create_button = self.driver.find_element(By.ID, "create")

        create_button.click()
        time.sleep(2)


class RegistrationWithEmptyUsername(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_registration_with_empty_username(self):
        self.driver.get(self.live_server_url + "/register/")

        password_input = self.driver.find_element(By.NAME, "password")
        repeat_password_input = self.driver.find_element(By.NAME, "repeat_password")
        question_select = Select(self.driver.find_element(By.ID, "id_question"))
        answer_input = self.driver.find_element(By.NAME, "answer")
        tan_input = self.driver.find_element(By.NAME, "tan")
        create_button = self.driver.find_element(By.ID, "create")

        password_input.send_keys("123")
        repeat_password_input.send_keys("123")
        question_select.select_by_value("2")
        answer_input.send_keys("cat")
        tan_input.send_keys("124")
        create_button.click()
        time.sleep(2)


class RegistrationWithEmptyPassword(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_registration_with_empty_password(self):
        self.driver.get(self.live_server_url + "/register/")

        username_input = self.driver.find_element(By.NAME, "username")
        repeat_password_input = self.driver.find_element(By.NAME, "repeat_password")
        question_select = Select(self.driver.find_element(By.ID, "id_question"))
        answer_input = self.driver.find_element(By.NAME, "answer")
        tan_input = self.driver.find_element(By.NAME, "tan")
        create_button = self.driver.find_element(By.ID, "create")

        username_input.send_keys("test")
        repeat_password_input.send_keys("123")
        question_select.select_by_value("2")
        answer_input.send_keys("cat")
        tan_input.send_keys("124")
        create_button.click()
        time.sleep(2)


class RegistrationWithEmptyRepeatPassword(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_registration_with_empty_repeat_password(self):
        self.driver.get(self.live_server_url + "/register/")

        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        question_select = Select(self.driver.find_element(By.ID, "id_question"))
        answer_input = self.driver.find_element(By.NAME, "answer")
        tan_input = self.driver.find_element(By.NAME, "tan")
        create_button = self.driver.find_element(By.ID, "create")

        username_input.send_keys("test")
        password_input.send_keys("123")
        question_select.select_by_value("2")
        answer_input.send_keys("cat")
        tan_input.send_keys("124")
        create_button.click()
        time.sleep(2)


class RegistrationWithEmptyQuestion(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_registration_with_empty_question(self):
        self.driver.get(self.live_server_url + "/register/")

        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        repeat_password_input = self.driver.find_element(By.NAME, "repeat_password")
        answer_input = self.driver.find_element(By.NAME, "answer")
        tan_input = self.driver.find_element(By.NAME, "tan")
        create_button = self.driver.find_element(By.ID, "create")

        username_input.send_keys("test")
        password_input.send_keys("123")
        repeat_password_input.send_keys("123")
        answer_input.send_keys("cat")
        tan_input.send_keys("124")
        create_button.click()
        time.sleep(2)


class RegistrationWithEmptyAnswer(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_registration_with_empty_answer(self):
        self.driver.get(self.live_server_url + "/register/")

        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        repeat_password_input = self.driver.find_element(By.NAME, "repeat_password")
        question_select = Select(self.driver.find_element(By.ID, "id_question"))
        tan_input = self.driver.find_element(By.NAME, "tan")
        create_button = self.driver.find_element(By.ID, "create")

        username_input.send_keys("test")
        password_input.send_keys("123")
        repeat_password_input.send_keys("123")
        question_select.select_by_value("2")
        tan_input.send_keys("124")
        create_button.click()
        time.sleep(2)


class RegistrationWithEmptyTAN(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_registration_with_empty_tan(self):
        self.driver.get(self.live_server_url + "/register/")

        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        repeat_password_input = self.driver.find_element(By.NAME, "repeat_password")
        question_select = Select(self.driver.find_element(By.ID, "id_question"))
        answer_input = self.driver.find_element(By.NAME, "answer")
        create_button = self.driver.find_element(By.ID, "create")

        username_input.send_keys("test")
        password_input.send_keys("123")
        repeat_password_input.send_keys("123")
        question_select.select_by_value("2")
        answer_input.send_keys("cat")
        create_button.click()
        time.sleep(2)


class RegistrationWithAuthenticatedTAN(SeleniumTestCase):
    fixtures = ['user_tests.json']

    def test_registration_with_authenticated_tan(self):
        self.driver.get(self.live_server_url + "/register/")

        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        repeat_password_input = self.driver.find_element(By.NAME, "repeat_password")
        question_select = Select(self.driver.find_element(By.ID, "id_question"))
        answer_input = self.driver.find_element(By.NAME, "answer")
        tan_input = self.driver.find_element(By.NAME, "tan")
        create_button = self.driver.find_element(By.ID, "create")

        username_input.send_keys("test")
        password_input.send_keys("123")
        repeat_password_input.send_keys("123")
        question_select.select_by_value("2")
        answer_input.send_keys("cat")
        tan_input.send_keys("123")
        create_button.click()
        time.sleep(2)