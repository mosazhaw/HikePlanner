import scrapy
from scrapy import Request
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scrapy.exceptions import CloseSpider
from selenium.webdriver.chrome.service import Service
from selenium import webdriver

class GpxSpider(scrapy.Spider):
    name = 'gpx'
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
            

            # Extract titles and buttons
            listings = self.driver.find_elements(By.CSS_SELECTOR, 'div.MuiCard-root')
            for listing in listings:
                title = listing.find_element(By.CSS_SELECTOR, 'div.MuiPaper-root h2').text
                table = listing.find_element(By.CSS_SELECTOR, 'table')
                priceRow = table.find_element(By.CSS_SELECTOR, 'tr:nth-child(2)')
                price = priceRow.find_element(By.CSS_SELECTOR, 'span:nth-child(1)').text
                last12MoRow = table.find_element(By.CSS_SELECTOR, 'tr:nth-child(3)')
                last12Mo = last12MoRow.find_element(By.CSS_SELECTOR, 'div > div:nth-child(2)').text
                dollarAgeRow = table.find_element(By.CSS_SELECTOR, 'tr:nth-child(4)')
                dollarAge = dollarAgeRow.find_element(By.CSS_SELECTOR, 'div > div:nth-child(2)').text

                yield {
                    'title': title,
                    'price': price,
                    'last12MonthEarnings': last12Mo,
                    'dollarAge': dollarAge,
                }

            # follow pagination links
            # Find and click the next button
            nav = self.driver.find_element(By.CSS_SELECTOR, 'nav.MuiPagination-root')
            ul = nav.find_element(By.CSS_SELECTOR, 'ul.MuiPagination-ul')
            li = ul.find_element(By.CSS_SELECTOR, 'li:nth-child(9)')
            next_button = li.find_element(By.CSS_SELECTOR, 'button')
            next_button.click()

            # Extract data from the next page
            yield Request(self.driver.current_url, callback=self.parse)
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            raise CloseSpider(reason='Page structure changed or element not found')
