import scrapy
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.exceptions import CloseSpider
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

class GpxSpider(scrapy.Spider):
    name = 'gpxcopy'
    start_urls = ['https://auctions.royaltyexchange.com/orderbook/past-deals/']

    def __init__(self):
        super(GpxSpider, self).__init__()
        self.service = Service('C:/Users/Envy/Documents/chromedriver-win64/chromedriver.exe')
        self.service.start()
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')  # Run Chrome in headless mode
        self.driver = webdriver.Remote(self.service.service_url, options=options)

    def closed(self, reason):
        self.driver.quit()

    def parse(self, response):
        self.driver.get(response.url)
        try:
            # Wait for the titles to be present
            WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.MuiPaper-root h2')))
            
            # Extract titles
            titles = self.driver.find_elements(By.CSS_SELECTOR, 'div.MuiPaper-root h2')
            for title_element in titles:
                title = title_element.text
                self.logger.info(f"Extracted title: {title}")
                yield {'title': title}
            
            # Example of handling pagination
            # next_button = self.driver.find_element(By.CSS_SELECTOR, 'a#NextLink')
            # next_button.click()
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            raise CloseSpider(reason='Page structure changed or element not found')
