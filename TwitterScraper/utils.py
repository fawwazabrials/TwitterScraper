from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import time
from dateutil import parser
import json

def extract_text(card):
        """ 
        Get text from a HTML element
        Text + Emoji + Link to image (if exist)
        """
        
        result = ""
        for content in card.find_elements(By.XPATH, ".//*"):
            if content.tag_name == "span":
                result += content.text
            if content.tag_name == "img":
                result += content.get_attribute("alt")
                
        return result