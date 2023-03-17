from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By

class Tweet:
    """ Class for methods relating to tweets """

    def __init__(self, headless=False):
        options = Options()
        options.add_experimental_option("detach", True)
        if headless:
            options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
    
    def close(self):
        self.driver.close()