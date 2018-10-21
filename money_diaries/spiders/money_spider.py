import os
import time
import scrapy
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys

chrome_options = Options()
chrome_options.add_argument("--disable-logging")

chromedriver = '/Applications/chromedriver'
os.environ['webdriver.chrome.driver'] = chromedriver
driver = webdriver.Chrome(chromedriver, chrome_options=chrome_options)

slideshow_diary_log = '/Users/davidoxnard/Documents/ds/python_work/misc/money_diaries/diary_slideshow_urls.txt'

discards = ['r29.co/mdfaqs',
            'Money Diaries',
            'Money Diaries Facebook Group',
            'Your Spending In Your State',
            'Your Spending In Your State:',
            'Keep the Receipts here',
            'Hamlet',
            'here',
            'This week:',
            'It',
            'The Lion King',
            'This week: A biomedical research analyst who makes $56,000 per year and spends it on bike accessories and a sleeping bag.',
            'Monthly Loan Payments',
            'Monthly Expenses',
            'Annual Expenses',
            'Additional Expenses',
            'Additional Expenses:',
            'Every month I withdraw $600 and divide it into physical envelopes for various expenses, including food ($200) and the following:',
            'Monthly Subscriptions/ Donations',
            'our guide to managing your money every day',
            'Monthly Revenue In Addition to Salary:',
            'Monthly expenses',
            'Yearly Expenses:',
            'All Other Expenses',
            'Shared My boyfriend and I have a joint account and each contribute $500/month to cover the following expenses (plus groceries, gas, and pet supplies):',
            ', for the inspiration.)',
            'Split Expenses With My Boyfriend From Our Joint account',
            'Hamilton',
            "Editor's Note:",
            'All Other I put all expenses (below) on my credit card, which I pay in full every month. I have no credit card debt.',
            ]


class MoneySpider(scrapy.Spider):

    name = 'money_spider'

    custom_settings = {
        "DOWNLOAD_DELAY": 3,
        "CONCURRENT_REQUESTS_PER_DOMAIN": 3,
        "HTTPCACHE_ENABLED": False
    }

    start_urls = [
        'https://www.refinery29.com/money-diary',
    ]

    def parse(self, response):

        current_url = response.request.url
        driver.get(current_url)
        driver.execute_script("window.scrollTo(0, 1080)")
        time.sleep(2)
        driver.execute_script("window.scrollTo(0, 1080)")

        xpath = '//div[contains(@class, "card")]//a'
        els = driver.find_elements_by_xpath(xpath)
        hrefs = [el.get_attribute('href') for el in els if 'money-diary-' in el.get_attribute('href')]

        for href in hrefs:

            yield scrapy.Request(
                url=href,
                callback=self.parse_diary_onepage,
                meta={'url': href}
            )


        next_url = 'https://www.refinery29.com' + response.xpath('//a[@id="more-stories"]/@href').extract_first()

        yield scrapy.Request(
            url=next_url,
            callback=self.parse
        )

    def parse_diary_onepage(self, response):

        url = response.request.meta['url']

        title = response.xpath('//h1/text()').extract_first()

        raw_text_xpath = '//div[contains(@class, "section-outer-container")]/div[contains(@class, "section-container")]/div/div[contains(@class, "section-text")]//text()[not(parent::em)]'
        raw_text_segments = response.xpath(raw_text_xpath).extract()
        raw_text = "\n".join([r.strip() for r in raw_text_segments if r not in discards])

        breakpoints = ['Day One' ,'Day Two', 'Day Three',
                        'Day Four', 'Day Five', 'Day Six', 'Day Seven',]


        if "Day One" not in raw_text:
            with open(slideshow_diary_log, 'a') as f_obj:
                f_obj.write(url+'\n')


        intro = raw_text.split(breakpoints[0])[0].strip().replace('\n', '|')
        day_one = raw_text.split(breakpoints[0])[1].split(breakpoints[1])[0].strip().replace('\n', ' ')
        day_two = raw_text.split(breakpoints[1])[1].split(breakpoints[2])[0].strip().replace('\n', ' ')
        day_three = raw_text.split(breakpoints[2])[1].split(breakpoints[3])[0].strip().replace('\n', ' ')
        day_four = raw_text.split(breakpoints[3])[1].split(breakpoints[4])[0].strip().replace('\n', ' ')
        day_five = raw_text.split(breakpoints[4])[1].split(breakpoints[5])[0].strip().replace('\n', ' ')
        day_six = raw_text.split(breakpoints[5])[1].split(breakpoints[6])[0].strip().replace('\n', ' ')
        day_seven = raw_text.split(breakpoints[6])[1].strip().replace('\n', ' ')


        yield {
            'title': title,
            'intro': intro,
            'day_one': day_one,
            'day_two': day_two,
            'day_three': day_three,
            'day_four': day_four,
            'day_five': day_five,
            'day_six': day_six,
            'day_seven': day_seven,
            'url': url,
            }