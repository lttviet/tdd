from .base import FunctionalTest
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

class NewVisitorTest(FunctionalTest):

    def test_can_start_a_list_for_one_user(self):
        self.browser.get(self.live_server_url)

        self.assertIn('To-Do', self.browser.title)
        header_text = self.browser.find_element_by_tag_name("h1").text
        self.assertIn("To-Do", header_text)

        inputbox = self.get_item_input_box()
        self.assertEqual(
                inputbox.get_attribute("placeholder"),
                "Enter a to-do item"
                )

        inputbox.send_keys("Buy peacock feather")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy peacock feather")

        inputbox = self.get_item_input_box()
        inputbox.send_keys("Use peacock feathers to make a fly")
        inputbox.send_keys(Keys.ENTER)

        self.wait_for_row_in_list_table("1: Buy peacock feather")
        self.wait_for_row_in_list_table("2: Use peacock feathers to make a fly")

    def test_multiple_users_can_start_lists_at_different_urls(self):
        self.browser.get(self.live_server_url)
        inputbox = self.get_item_input_box()
        inputbox.send_keys("Buy peacock feather")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy peacock feather")

        edith_list_url = self.browser.current_url
        self.assertRegex(edith_list_url, r"/lists/.+")

        ## We use a new browser session to make sure no info
        ## of Edith's is coming through from cookies etc
        self.browser.quit()
        self.browser = webdriver.Firefox()

        self.browser.get(self.live_server_url)
        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertNotIn("Buy peacock feather", page_text)
        self.assertNotIn("make a fly", page_text)

        inputbox = self.get_item_input_box()
        inputbox.send_keys("Buy milk")
        inputbox.send_keys(Keys.ENTER)
        self.wait_for_row_in_list_table("1: Buy milk")

        francis_list_url = self.browser.current_url
        self.assertRegex(francis_list_url, r"/lists/.+")
        self.assertNotEqual(edith_list_url, francis_list_url)

        page_text = self.browser.find_element_by_tag_name("body").text
        self.assertNotIn("Buy peacock feather", page_text)
        self.assertIn("Buy milk", page_text)
