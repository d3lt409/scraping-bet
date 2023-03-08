import time
import traceback
import sys
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from multiprocessing.pool import ThreadPool
from datetime import datetime
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError


from models.scraper import Scraper
from scraping.betplay_scraper.tennis.constants import *

from functools import partial, reduce

engine_scraper = Scraper(PAGE_URL)
links = []
links_done = []

def get_links_games():
    global links, links_done
    try:
        engine_scraper.element_wait_searh(TIME, By.XPATH, BUTTON_GAMES).click()
        links = links + \
            [val.get_attribute("href") for val in engine_scraper.elements_wait_searh(
                TIME, By.XPATH, XPATH_GAMES)]
        if len(links_done) == 0:
            with open("src/assets/links.txt", "w") as fp:
                fp.writelines(map(lambda x: f"{x}\n", links))
            return
        print(links, links_done)
        for i in range(len(links)):
            if links[i] in links_done:
                del links[i]

    except Exception as e:
        print(e.with_traceback(e.__traceback__))


def read_links(link: str, engine:Engine):
    scraper = Scraper(link, NAME_DATA_BASE)
    scraper.driver.implicitly_wait(1)
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
        return data
    time.sleep(2)
    while True:
        try:
            scraper.element_wait_searh(2, By.XPATH, XPATH_GAME_OFFERS)
            print("salio")
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
                10, By.XPATH, XPATH_POINT_ITEM)
            set_element = scraper.element_wait_searh(
                10, By.XPATH, XPATH_SET_ITEM)
            game_element = scraper.element_wait_searh(
                10, By.XPATH, XPATH_GAME_ITEM)
            macth_element = scraper.element_wait_searh(
                10, By.XPATH, XPATH_MATCH_ITEM)
            elements = {"punto": point_element, "set": set_element,
                        "juego": game_element, "partido": macth_element}
            ser = pd.Series(index=COLUMNS)
            score_name = scraper.elements_wait_searh(
                5, By.XPATH, XPATH_SCORE_GAME_NAME)
            
            score_value = scraper.elements_wait_searh(
                5, By.XPATH, XPATH_SCORE_GAME_VALUE)
            
            
            ser.update({"id_evento": int(event_id),
                        "nombre_evento": event_game})
            ser.update({f"jugador{i+1}": val.text for i,
                       val in enumerate(score_name)})

            for i,val in enumerate(score_value):
                try:
                    val.find_element(By.CLASS_NAME, 'KambiBC-scoreboard__serve-indicator')
                    ser.update({"servicio":ser[f"jugador{i+1}"]})
                except NoSuchElementException:
                    continue
            ser.update({f"marcador{i+1}": val.find_element(By.TAG_NAME,"span").text for i,
                       val in enumerate(score_value)})
            sets = scraper.elements_wait_searh(
                5, By.XPATH, XPATH_SET_VALUES)
            ser.update({f"set{i+1}_marcador": int(val.text) for i,
                       val in enumerate(sets)})
            for name, element in elements.items():
                element.click()
                prices = scraper.elements_wait_searh(
                    5, By.XPATH, XPATH_GAME_PRICE)
                ser.update({f"{name}{i+1}": float(val.text) for i,
                           val in enumerate(prices)})
            ser.update({"timestamp": datetime.now()})
            
            with engine.connect() as conn:
                try:
                    ser.to_frame().T.to_sql('betplay',conn, index=False, if_exists='append')
                    conn.commit()
                except IntegrityError:
                    pass
        except StaleElementReferenceException:
            print("entra")
            continue
        except TimeoutException as e:
            # exp = sys.exc_info()
            # traceback.print_exception(*exp)
            time.sleep(10)



def main(engine:Engine):
    global links

    pool = ThreadPool(5)
    response = []
    get_links_games()
    timeout = time.time() + 60*24*24
    while time.time() <= timeout:
        if len(links) != 0:
            link = links.pop()
            # pool.map_async(partial(read_links,engine=engine), (link,))
            response.append(pool.apply_async(read_links,(link,engine)))
            links_done.append(link)
        else:
            for res in response: pool.apply_async(res.get)
            response = []
            time.sleep(5)
            engine_scraper.driver.get(PAGE_URL)
            time.sleep(5)
            pool.map_async(get_links_games,()).get()

    pool.close()
    pool.join()

    engine_scraper.close()
