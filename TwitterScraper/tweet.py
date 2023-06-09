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

    def scrape_profile(self, user_id):
        self.driver.get(f"https://twitter.com/{user_id}")
        try: 
            try:
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[@class="css-901oao css-1hf3ou5 r-14j79pv r-37j5jr r-n6v787 r-16dba41 r-1cwl3u0 r-bcqeeo r-qvutc0"]'))) # Wait for tweet count
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//a[@class="css-4rbku5 css-18t94o4 css-901oao r-18jsvk2 r-1loqt21 r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0"]'))) # Wait for follower and following
                WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//span[@data-testid="UserJoinDate"]'))) # Wait for user joined date
            except: # Account must be clicked first before viewing
                self.driver.find_element(By.XPATH, "//span[contains(text(), 'Yes, view profile')]").click()
        except: # Account is deleted / not found
            return (
                {
                    "biography": "ACCOUNT NOT FOUND!",
                    "tweetCount": "ACCOUNT NOT FOUND!",
                    "folllowing": "ACCOUNT NOT FOUND!",
                    "followers": "ACCOUNT NOT FOUND!",
                    "joinedDate": "ACCOUNT NOT FOUND!",
                    "userLocation": "ACCOUNT NOT FOUND!",
                    "profession": "ACCOUNT NOT FOUND!",
                }
            )

        tweet_count = self.driver.find_element(By.XPATH, ".//div[@class='css-901oao css-1hf3ou5 r-14j79pv r-37j5jr r-n6v787 r-16dba41 r-1cwl3u0 r-bcqeeo r-qvutc0']").text.replace(" Tweets", '')

        foll = self.driver.find_elements(By.XPATH, '//a[@class="css-4rbku5 css-18t94o4 css-901oao r-18jsvk2 r-1loqt21 r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-qvutc0"]')
        following = foll[0].text.replace(" Following", '')
        followers = foll[1].text.replace(" Followers", '')

        joined_date = self.driver.find_element(By.XPATH, '//span[@data-testid="UserJoinDate"]').text
        try:
            user_location = self.driver.find_element(By.XPATH, '//span[@data-testid="UserLocation"]').text.replace("Joined ", '')
        except:
            user_location = ""
        try:
            profession = self.driver.find_element(By.XPATH, '//span[@data-testid="UserProfessionalCategory"]').text
        except:
            profession = ""
        try:
            bio = self._extract_text(self.driver.find_element(By.XPATH, "//div[@data-testid='UserDescription']"))
        except:
            bio = ""

        return (
            {
                "biography": bio,
                "tweetCount": tweet_count,
                "folllowing": following,
                "followers": followers,
                "joinedDate": joined_date,
                "userLocation": user_location,
                "profession": profession,
            }
        )

    def scrape_replies(self, url):
        self.driver.get(url)
        time.sleep(3)

        try:
            self.driver.find_element(By.XPATH, "//*[contains(text(), 'Hmm...this page doesn’t exist. Try searching for something else.')]")
            return None
        except:
            pass

        data = []
        data = self._scroll(data)

        return data

    def _scroll(self, data):
        curr_pos = self.driver.execute_script("return document.body.scrollHeight")

        while True:
            for i in range(10): self._click_additionals()
            cards = self.driver.find_elements(By.XPATH, ".//article[@data-testid='tweet' and @tabindex='0']")
            if len(cards) > 0:
                now = cards[0]
                for card in cards:
                    tweet = self._get_card_data(card)

                    if tweet not in data:
                        print(tweet)
                        data.append(tweet)
                        now = card
                    

                self.driver.execute_script("arguments[0].scrollIntoView();", now)
                time.sleep(2)
                last_pos = curr_pos
                curr_pos = self.driver.execute_script("return document.body.scrollHeight")

                if last_pos == curr_pos:
                    break
            else: break

        return data

    def _get_card_data(self, card):
        self._click_notif()

        try:
            username_row = card.find_element(By.XPATH, ".//div[@data-testid='User-Name']").find_elements(By.TAG_NAME, 'a')
        except Exception as e:
            return
        
        username = username_row[0].text
        user_id = username_row[1].text
        time = parser.parse(username_row[2].find_element(By.TAG_NAME, 'time').get_attribute("datetime")).strftime("%d/%m/%Y, %H:%M:%S")

        content = self._get_card_content(card)

        try:
            replies = card.find_element(By.XPATH, ".//div[@data-testid='reply']").text
        except:
            replies = '0'

        try:
            retweets = card.find_element(By.XPATH, ".//div[@data-testid='retweet']").text
        except:
            retweets = '0'

        try:
            likes = card.find_element(By.XPATH, ".//div[@data-testid='like']").text
        except:
            likes = '0'

        return {
            "username": username,
            "userId": user_id,
            "time": time,
            "content": content,
            "replies": replies,
            "retweets": retweets,
            "likes": likes,
    }

    def _extract_text(self, card):
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
    
    def _get_card_content(self, card):
        content = ""

        try:
            el = card.find_elements(By.XPATH, ".//div[@data-testid='tweetText']")
            if type(el) != list: el = [el] 

            if len(el) > 0:
                if len(el) > 1:
                    content += self._extract_text(el[0])
                else:
                    content += self._extract_text(el[0])

        except Exception as e:
            pass

        try:
            for media in card.find_elements(By.XPATH, ".//div[@data-testid='tweetPhoto']"):
                if not self.is_from_qrt(card, media):
                    try:
                        content += "\nimage: ".format(media.find_element(By.XPATH, ".//img").get_attribute("src"))
                    except:
                        pass

                    try:
                        content += "\nvideo: ".format(media.find_element(By.XPATH, ".//video").get_attribute("src"))
                    except:
                        pass
        except:
            pass

        try:
            content += "\nqrt: {}".format(
                card.find_element(By.XPATH, ".//div[contains(@class, 'css-1dbjc4n r-1ssbvtb r-1s2bzr4')]//a[contains(@role, 'link')]").get_attribute("href"))
        except:
            pass

        return content
    
    def _click_notif(self):
        try:
            self.driver.find_element(By.XPATH, ".//*[@class='css-18t94o4 css-1dbjc4n r-1niwhzg r-1ets6dv r-sdzlij r-1phboty r-rs99b7 r-1wzrnnt r-19yznuf r-64el8z r-1ny4l3l r-1dye5f7 r-o7ynqc r-6416eg r-lrvibr']").click()
        except:
            pass

    def _click_additionals(self):
        try: # Click kalo ada "show more tweets"
            el = self.driver.find_element(By.XPATH, '//div[@class="css-18t94o4 css-1dbjc4n r-1777fci r-1pl7oy7 r-1ny4l3l r-o7ynqc r-6416eg r-13qz1uu"]')
            el.click()
            time.sleep(0.5)
            return self.driver.find_element(el)
        except:
            pass

        try: # Click kalo ada "show replies"
            el = self.driver.find_element(By.XPATH, '//div[@class="css-901oao r-1cvl2hr r-37j5jr r-a023e6 r-16dba41 r-rjixqe r-bcqeeo r-5njf8e r-qvutc0"]')
            el.click()
            time.sleep(0.5)
            return self.driver.find_element(el)
        except:
            pass

        try: # Click kalo ada "show additional replies, may have offensive content"
            el = self.driver.find_element(By.XPATH, '//div[@class="css-18t94o4 css-1dbjc4n r-1niwhzg r-42olwf r-sdzlij r-1phboty r-rs99b7 r-15ysp7h r-4wgw6l r-1ny4l3l r-ymttw5 r-f727ji r-j2kj52 r-o7ynqc r-6416eg r-lrvibr"]')
            el.click()
            time.sleep(0.5)

            return el
        except:
            pass
        
        return None