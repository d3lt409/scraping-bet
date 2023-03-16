import gc
import time
import os
import sys

from selenium import webdriver
from selenium.webdriver.chrome.webdriver import WebDriver
from selenium.common.exceptions import WebDriverException,NoSuchElementException, TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.common.action_chains import ActionChains

from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options

from utils.util import internet_on


class Scraper():

    def __init__(self, page_url:str, headless:bool = False) -> None:
        self.headless = headless
        self._driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()) 
                              ,options=self.get_options(self.headless))                     # Define the driver we are using
        self._current_url = page_url
        self.init_page()

    
    def _get_driver(self):
        return self._driver

    def _get_current_url(self):
        return self._current_url

    def _set_current_url(self, url):
        self._current_url = url
    
    current_url = property(fget=_get_current_url, fset=_set_current_url)
    driver:WebDriver = property(fget=_get_driver)

    def get_options(self, headless:bool):
        chrome_options = Options()
        if headless:
            chrome_options.add_argument('--headless')
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument("--disable-extensions")
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        prefs = {'profile.default_content_setting_values': {'images': 2, 'plugins': 2, 'popups': 2, 'geolocation': 2, 'notifications': 2, 'auto_select_certificate': 2, 'fullscreen': 2,
                                                            'mouselock': 2, 'mixed_script': 2, 'media_stream': 2, 'media_stream_mic': 2, 'media_stream_camera': 2, 'protocol_handlers': 2, 'ppapi_broker': 2,
                                                            'automatic_downloads': 2, 'midi_sysex': 2, 'push_messaging': 2, 'ssl_cert_decisions': 2, 'metro_switch_to_desktop': 2,
                                                            'protected_media_identifier': 2, 'app_banner': 2, 'site_engagement': 2, 'durable_storage': 2}}
        chrome_options.add_experimental_option("prefs", prefs)
        chrome_options.add_argument("--log-level=3")

    def init_page(self):
        while not internet_on(): continue
        self._driver.maximize_window()
        self._driver.get(self.current_url)
    
    def ready_document(self,tries=0):
        if tries == 4:
            return
        timeout = time.time() + 60
        while time.time() <= timeout:
            try:
                page_state = self._driver.execute_script('return document.readyState;')
                if page_state == 'complete':
                    tries = 4
                    return
            except WebDriverException as _:
                self.crash_refresh_page()

        if tries < 4:
            self._driver.refresh()
            self.ready_document(tries+1)
        print("La página se cayó")
        duration = 5  # seconds
        freq = 440  # Hz
        if sys.platform == 'linux':
            os.system('play -nq -t alsa synth {} sine {}'.format(duration, freq))
        exit()
    
    def crash_refresh_page(self):
        while not internet_on():
            continue
        try:
            self._driver.close()
            gc.collect(2)
        except WebDriverException:
            pass
        self._driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()) 
                              ,options=self.get_options(self.headless)) 
        self.init_page()
        self.ready_document()
    
    def element_wait_lambda_return(self,element, script):
        values = self.driver.execute_script(script, element)
        date, hour = values.split()[0:2]
        return date.replace('T00:00:00.000Z', f" {hour[0:9]}")

    def element_wait_searh(self, time:int, by, value:str) -> WebElement:
        return WebDriverWait(self._driver, time ).until(EC.presence_of_element_located((by, value)))

    def elements_wait_searh(self, time:int, by, value:str) -> list[WebElement]:
        return WebDriverWait(self._driver, time).until(EC.presence_of_all_elements_located((by, value)))
    
    def element_click_wait_searh(self, time:int, by, value:str) -> WebElement:
        return WebDriverWait(self._driver, time).until(EC.element_to_be_clickable((by, value)))
    
    def click(self,element:WebElement):
        self.driver.execute_script("arguments[0].scrollIntoView();", element)
        time.sleep(1)
        element.click()
    
    def close(self):
        self._driver.close()