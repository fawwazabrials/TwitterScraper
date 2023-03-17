from requests_html import HTMLSession, HTML
from lxml.etree import ParserError

session = HTMLSession()

class Profile:
    def __init__(self, user_id):
        page = session.get(f"https://twitter.com/{user_id}")
        self.user_id = user_id
        
        self._scrape_profile(page)

    def _scrape_profile(self, page):
        html = page.html
        username = html.find(".//div[@data-testid='UserName']").text
        print(username)
        
        # return (
        #     {
        #         "username": username,
        #         "userId": self.user_id,
        #         "tweetCount": tweet_count,
        #         "following": following,
        #         "followers": followers,
        #         "biography": biography,
        #     }
        # )

    