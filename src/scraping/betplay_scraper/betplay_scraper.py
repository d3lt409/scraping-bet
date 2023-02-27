import time
import traceback, sys
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException,ElementClickInterceptedException,StaleElementReferenceException
from multiprocessing.pool import ThreadPool, MapResult
from datetime import datetime


from models.scraper import Scraper
from scraping.betplay_scraper.constants import *

engine = Scraper(PAGE_URL,NAME_DATA_BASE)
links = []

def get_links_games(links_done:list):
    global links
    try:
        
        links = links + [val.get_attribute("href") for val in engine.elements_wait_searh(TIME, By.XPATH, XPATH_GAMES)]
        if len(links_done) == 0: return links
        print(links)
        for i in range(len(links)):
            if links[i] in links_done: del links[i]
        
    except Exception as e:
        print(e.with_traceback(e.__traceback__))

def read_links(link:str):
    scraper = Scraper(link, NAME_DATA_BASE)
    scraper.driver.get(link)
    event_id= link.split("/")[-1]
    data = pd.DataFrame(columns=COLUMNS)
   
    event_game = "-".join([val.text for val in scraper.elements_wait_searh(TIME, By.XPATH, XPATH_EVENT_GAME)[1:]])
    while True:
        try:
            scraper.element_wait_searh(2,By.XPATH, XPATH_GAME_OFFERS)
            return data
        except TimeoutException:
            pass
        try:
            
            point_element = scraper.element_wait_searh(TIME, By.XPATH, XPATH_POINT_ITEM)
            set_element = scraper.element_wait_searh(TIME, By.XPATH, XPATH_SET_ITEM)
            game_element = scraper.element_wait_searh(TIME, By.XPATH, XPATH_GAME_ITEM)
            macth_element = scraper.element_wait_searh(TIME, By.XPATH, XPATH_MATCH_ITEM)
            elements = {"punto":point_element,"set":set_element,"juego":game_element,"partido":macth_element}
            ser = pd.Series(index=COLUMNS)
            score_name = scraper.elements_wait_searh(TIME, By.XPATH, XPATH_SCORE_GAME_NAME)
            score_value = scraper.elements_wait_searh(TIME, By.XPATH, XPATH_SCORE_GAME_VALUE)
            ser.update({"id_evento":event_id,
                        "nombre_evento":event_game})
            ser.update({f"jugador{i+1}":val.text for i,val in enumerate(score_name)})
            ser.update({f"marcador{i+1}":val.text for i,val in enumerate(score_value)})
            sets = scraper.elements_wait_searh(TIME, By.XPATH, XPATH_SET_VALUES)
            ser.update({f"set{i+1}_marcador":val.text for i,val in enumerate(sets)})

            for name,element in elements.items():
                element.click()
                prices = scraper.elements_wait_searh(TIME, By.XPATH, XPATH_GAME_PRICE)
                ser.update({f"{name}{i+1}":val.text for i,val in enumerate(prices)})
            ser.update({"timestamp":datetime.now()})
            data = pd.concat([data,ser.to_frame().T], ignore_index=True)
        except StaleElementReferenceException:
            continue
        except TimeoutException as e:
            exp = sys.exc_info()
            traceback.print_exception(*exp)
            return data

def main():
    global links
    
    pool = ThreadPool(4)
    links_done = []
    engine.element_wait_searh(TIME, By.XPATH, BUTTON_GAMES).click()
    get_links_games(links_done)
    timeout = time.time() + 240
    results:list[MapResult] = []
    while time.time() <= timeout or len(links) != 0:
        if len(links) != 0: 
            link = links.pop()
            results.append(pool.map_async(read_links,(link,)))
            links_done.append(link)
            
        else:
            time.sleep(2)
            engine.driver.refresh()
            time.sleep(2)
            get_links_games(links_done)
    for result in results:
        print(result)
        df:pd.DataFrame = result.get()[0]
        engine.db.to_data_base(df)
    pool.close()
    pool.join()

    engine.close()