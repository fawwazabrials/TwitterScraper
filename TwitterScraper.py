from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
import traceback
import time
from dateutil import parser
import json

"""
Class representing a tweet or post from Twitter with their relating field
"""
class Tweet:
    tweetURL = ""
    username = ""
    userID = ""
    timePosted = ""
    content = ""
    replies = ""
    likes = ""
    retweets = ""

    def __init__(self, tweetURL=None, username=None, userID=None, timePosted=None, 
                        content=None, replies=None, likes=None, retweets=None):
        self.tweetURL = tweetURL
        self.username = username
        self.userID = userID
        self.timePosted = timePosted
        self.content = content
        self.replies = replies
        self.likes = likes
        self.retweets = retweets

"""
Class representing a user in Twitter with their relating field
"""
class User:
    userID = ""
    username = ""
    biography = ""
    tweets = ""
    following = ""
    followers = ""
    birthDate = ""
    joinDate = ""
    userLocation = ""
    profession = ""
    userURL = ""

    def __init__(self, userID="", username="", biography="", tweets="", following="", birthDate="",
                        followers="", joinDate="", userLocation="", profession="", userURL=""):
        self.userID = userID
        self.username = username
        self.biography = biography
        self.tweets = tweets
        self.following = following
        self.followers = followers
        self.birthDate = birthDate
        self.joinDate = joinDate
        self.userLocation = userLocation
        self.profession = profession
        self.userURL = userURL

    def get_dict(self):
        return vars(self)
        
"""
Scraper for scraping Twitter
"""
class TwitterScraper:
    def __init__(self, headless=False):
        options = Options()
        options.add_experimental_option("detach", True)
        options.add_experimental_option('excludeSwitches', ['enable-logging'])
        if headless:
            options.add_argument("--headless")

        self.driver = webdriver.Chrome(options=options)
        self.driver.maximize_window()
    
    def close(self):
        self.driver.close()

    def _find_page_doesnt_exist(self):
        try:
            self.driver.find_element(By.XPATH, "//*[contains(text(), 'Hmm...this page doesn’t exist. Try searching for something else.')]")
            return True
        except:
            return False

    """ 
    Get text from a HTML element
    Text + Emoji + Link to image (if exist)
    """
    def _extract_text(self, card):
        result = ""
        for content in card.find_elements(By.XPATH, ".//*"):
            if content.tag_name == "span":
                result += content.text
            if content.tag_name == "img":
                result += content.get_attribute("alt")
                
        return result

    """
    Scraping a user for their information
    """
    def scrape_user_info(self, userID):
        self.driver.get(f'https://twitter.com/{userID}')

        username = ""
        biography = ""
        tweets = ""
        following = ""
        followers = ""
        birthDate = ""
        joinDate = ""
        userLocation = ""
        profession = ""
        userURL = ""
        
        # print("doenst exsist:", self._find_page_doesnt_exist())

        
        try: # Wait until following/followers count and username are displayed
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, "//div[@aria-label='Home timeline' and @tabindex='0']")))
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, f'//a[@href="/{userID}/following"]')))
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, f'//a[@href="/{userID}/followers"]')))
            WebDriverWait(self.driver, 60).until(EC.presence_of_element_located((By.XPATH, '//div[@data-testid="UserName"]')))
        except:
            traceback.print_exc()
        homeTimeline = self.driver.find_element(By.XPATH, "//div[@aria-label='Home timeline' and @tabindex='0']")


        # top row for tweet count
        tweets = homeTimeline.find_elements(By.XPATH, "*")[0].text.split("\n")[1].replace(" Tweets", '')

        # 1st block - username & userid
        userBlock = homeTimeline.find_element(By.XPATH, '//div[@data-testid="UserName"]').text.split('\n')
        username = userBlock[0]


        # 2nd block - bio
        if len(homeTimeline.find_elements(By.XPATH, "//div[@data-testid='UserDescription']")) > 0:
            biography = self._extract_text(homeTimeline.find_element(By.XPATH, "//div[@data-testid='UserDescription']"))


        # 3rd block - other info (link, create_date, location, profession)
        if len(homeTimeline.find_elements(By.XPATH, '//span[@data-testid="UserLocation"]')) > 0:
            userLocation = homeTimeline.find_element(By.XPATH, '//span[@data-testid="UserLocation"]').text
        
        if len(homeTimeline.find_elements(By.XPATH, '//a[@data-testid="UserUrl"]')) > 0:
            userURL = homeTimeline.find_element(By.XPATH, '//a[@data-testid="UserUrl"]').text

        if len(homeTimeline.find_elements(By.XPATH, '//span[@data-testid="UserProfessionalCategory"]')) > 0:
            profession = homeTimeline.find_element(By.XPATH, '//span[@data-testid="UserProfessionalCategory"]').text

        if len(homeTimeline.find_elements(By.XPATH, '//span[@data-testid="UserBirthdate"]')) > 0:
            birthDate = homeTimeline.find_element(By.XPATH, '//span[@data-testid="UserBirthdate"]').text.replace("Born ", '')
        
        if len(homeTimeline.find_elements(By.XPATH, '//span[@data-testid="UserJoinDate"]')) > 0:
            joinDate = homeTimeline.find_element(By.XPATH, '//span[@data-testid="UserJoinDate"]').text.replace("Joined ", '')


        # 4th block - following/followers
        following = homeTimeline.find_element(By.XPATH, f'//a[@href="/{userID}/following"]').text.replace(" Following", '')
        followers = homeTimeline.find_element(By.XPATH, f'//a[@href="/{userID}/followers"]').text.replace(" Followers", '')


        # print(userID)
        # print(username)
        # print(biography)
        # # print(tweets)
        # print(following)
        # print(followers)
        # print(birthDate)
        # print(joinDate)
        # print(userLocation)
        # print(profession)
        # print(userURL)

        return User(userID=userID, username=username, biography=biography, tweets=tweets, following=following, followers=followers,
                        birthDate=birthDate, joinDate=joinDate, userLocation=userLocation, profession=profession, userURL=userURL)
    
    def scrape_user_tweets(self, userID):
        self.driver.get(f'https://twitter.com/{userID}')

        