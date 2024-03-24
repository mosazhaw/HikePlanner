import scrapy
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
                #price = priceDiv.find_element(By.CSS_SELECTOR, 'span:nth-child(1)').text
                yield {'title': title,
                       'price': price,
                       'last12MonthEarnings': last12Mo,
                       'dollarAge': dollarAge}
                

                # Click the button inside the current item
                #button = item.find_element(By.TAG_NAME, 'button')
                #button.click()

                # Wait for the next page to load
                #WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.CSS_SELECTOR, 'div.new-page-element')))
                
                # Extract additional information from the new page
                #elements  = self.driver.find_element(By.CSS_SELECTOR, 'div.MuiPaper-root.jss1254.jss1249.jss1252').text
                #for element in elements:
                #    text = element.text.strip()  # Strip any leading or trailing whitespace
                #    self.logger.info(f"Extracted text: {text}")
                #    yield {'text': text}
            
            # Example of handling pagination
            # next_button = self.driver.find_element(By.CSS_SELECTOR, 'a#NextLink')
            # next_button.click()
        except Exception as e:
            self.logger.error(f"An error occurred: {e}")
            raise CloseSpider(reason='Page structure changed or element not found')
