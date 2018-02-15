import logging
import sys
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.webdriver.support import expected_conditions as EC


class Plugin:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        logging.info('Web screenshot plugin inited')

    """
    Requires body params:
    web:
        page:
        xpath: (optional - will be used '/html')
        width: (optional - will be used 1024)
        height: (optional - will be used 768)
        wait: (optional - will be used 10)
    """
    async def process(self, body):
        logging.info('Web screenshot plugin process called')

        # Old method
        #driver = webdriver.PhantomJS()

        # New with headless ff
        # https://intoli.com/blog/running-selenium-with-headless-firefox/
        os.environ['MOZ_HEADLESS'] = '1'
        binary = FirefoxBinary('/usr/bin/firefox', log_file=sys.stdout)
        binary.add_command_line_options('-headless')
        driver = webdriver.Firefox(
                firefox_binary=binary
            )

        driver.set_window_size(body.get('width', 1024), body.get('height', 768))
        driver.get(body['page'])

        try:
            WebDriverWait(driver, body['wait']).until(
                EC.presence_of_element_located((By.XPATH, body.get('xpath', '/html')))
            )
        except Exception as e:
            logging.error(e)
            logging.error("Couldn't wait for element")

        screen = driver.get_screenshot_as_base64()

        # .close() with headless leaves geckodriver
        driver.quit()

        logging.debug('Processing finished')

        return {
                "head": '### {} <a href="{}">clickable</a>'.format(body['page'], body['page']),
                "body": '<img src="data:image/png;base64, {}" alt="Screenshot" />'.format(screen)
                }
