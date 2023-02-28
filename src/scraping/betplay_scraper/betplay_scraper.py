import time
import traceback
import sys
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from multiprocessing.pool import ThreadPool, MapResult
from datetime import datetime


from models.scraper import Scraper
from scraping.betplay_scraper.constants import *

engine = Scraper(PAGE_URL)
links = []
links_done = []

def get_links_games():
    global links, links_done
    try:
        time.sleep(2)
        engine.element_wait_searh(TIME, By.XPATH, BUTTON_GAMES).click()
        links = links + \
            [val.get_attribute("href") for val in engine.elements_wait_searh(
                TIME, By.XPATH, XPATH_GAMES)]
        if len(links_done) == 0:
            return
        print(links, links_done)
        for i in range(len(links)):
            if links[i] in links_done:
                del links[i]

    except Exception as e:
        print(e.with_traceback(e.__traceback__))


def read_links(link: str):
    scraper = Scraper(link, NAME_DATA_BASE)
    links_done.append(link)
    scraper.driver.get(link)
    event_id = link.split("/")[-1]
    data = pd.DataFrame(columns=COLUMNS)
    try:
        event_game = "-".join([val.text for val in scraper.elements_wait_searh(
            TIME, By.XPATH, XPATH_EVENT_GAME)[1:]])
    except Exception as e:
        exp = sys.exc_info()
        traceback.print_exception(*exp)
        return
    tries = 0
    while True:
        try:
            scraper.element_wait_searh(2, By.XPATH, XPATH_GAME_OFFERS)
            scraper.db.to_data_base(data)
            
            return
        except StaleElementReferenceException:
            scraper.driver.refresh()
            continue
        except TimeoutException as e:
            pass
        except Exception as e:
            exp = sys.exc_info()
            traceback.print_exception(*exp)
        try:
            point_element = scraper.element_wait_searh(
                TIME, By.XPATH, XPATH_POINT_ITEM)
            set_element = scraper.element_wait_searh(
                TIME, By.XPATH, XPATH_SET_ITEM)
            game_element = scraper.element_wait_searh(
                TIME, By.XPATH, XPATH_GAME_ITEM)
            macth_element = scraper.element_wait_searh(
                TIME, By.XPATH, XPATH_MATCH_ITEM)
            elements = {"punto": point_element, "set": set_element,
                        "juego": game_element, "partido": macth_element}
            ser = pd.Series(index=COLUMNS)
            score_name = scraper.elements_wait_searh(
                TIME, By.XPATH, XPATH_SCORE_GAME_NAME)
            score_value = scraper.elements_wait_searh(
                TIME, By.XPATH, XPATH_SCORE_GAME_VALUE)
            ser.update({"id_evento": int(event_id),
                        "nombre_evento": event_game})
            ser.update({f"jugador{i+1}": val.text for i,
                       val in enumerate(score_name)})
            ser.update({f"marcador{i+1}": int(val.text) for i,
                       val in enumerate(score_value)})
            sets = scraper.elements_wait_searh(
                TIME, By.XPATH, XPATH_SET_VALUES)
            ser.update({f"set{i+1}_marcador": int(val.text) for i,
                       val in enumerate(sets)})

            for name, element in elements.items():
                element.click()
                prices = scraper.elements_wait_searh(
                    TIME, By.XPATH, XPATH_GAME_PRICE)
                ser.update({f"{name}{i+1}": float(val.text) for i,
                           val in enumerate(prices)})
            ser.update({"timestamp": datetime.now()})
            data = pd.concat([data, ser.to_frame().T], ignore_index=True)
        except StaleElementReferenceException:
            continue
        except TimeoutException as e:
            if tries == 2:
                scraper.db.to_data_base(data)
                links_done.append(link)
                return
            exp = sys.exc_info()
            traceback.print_exception(*exp)
            time.sleep(3)
            tries += 1


def main():
    global links

    pool = ThreadPool()

    get_links_games()
    timeout = time.time() + 120
    while time.time() <= timeout:
        if len(links) != 0:
            link = links.pop()
            pool.map_async(read_links, (link,))
        else:
            time.sleep(5)
            engine.driver.get(PAGE_URL)
            pool.apply(get_links_games)

    pool.close()
    pool.join()

    engine.close()
