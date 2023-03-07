import time
import traceback
import sys
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException, NoSuchElementException
from multiprocessing.pool import ThreadPool
from datetime import datetime, timedelta, timezone
import pytz
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from functools import partial

from models.scraper import Scraper
from scraping.betplay_scraper.football.constants import *

engine_scraper = Scraper(PAGE_URL)
links = []
links_done = []
script_date = 'const f = new Date(arguments[0]); return f'
#text = WebDriverWait(driver, 20).until(lambda driver: driver.execute_script(f'return {script}'))
def get_links_games():
    global links, links_done
    if engine_scraper.current_url != PAGE_URL: engine_scraper.driver.get(PAGE_URL)
    try:
        engine_scraper.element_wait_searh(TIME, By.XPATH, XPATH_BUTTON_FOOTBALL).click()
        engine_scraper.element_wait_searh(TIME, By.XPATH, XPATH_DROPDOWN_SORT).click()
        engine_scraper.element_wait_searh(TIME, By.XPATH, XPATH_ITEM_HOUR).click()
        time.sleep(2)
        for el in engine_scraper.elements_wait_searh(TIME, By.XPATH, XPATH_DROPDOWN_LIST_HOURS): el.click()
        for el in engine_scraper.elements_wait_searh(TIME, By.XPATH, XPATH_DROPDWN_LIST_GAMES): el.click()

        return [val.get_attribute("href") for val in engine_scraper.elements_wait_searh(
                TIME, By.XPATH, XPATH_GAMES)]

    except Exception as e:
        print(e.with_traceback(e.__traceback__))


def read_links(link: str, engine:Engine):
    scraper = Scraper(link, NAME_DATA_BASE)
    scraper.driver.implicitly_wait(1)
    scraper.driver.get(link)
    event_id = link.split("/")[-1]

    try:
        event_game = "-".join([val.text for val in scraper.elements_wait_searh(
            TIME, By.XPATH, XPATH_EVENT_GAME)[1:]])
    except Exception as e:
        exp = sys.exc_info()
        traceback.print_exception(*exp)
        return 
    time.sleep(2)
    time_elemnt = scraper.element_wait_searh(TIME,By.XPATH, XPATH_START_GAME)
    date_game = scraper.element_wait_lambda_return(TIME,int(time_elemnt.get_attribute("datetime")),script_date)
    date_game = datetime.fromisoformat(date_game).astimezone(timezone(timedelta(hours=-5)))
    while True:
        try:
            jugador1, jugador2 = scraper.element_wait_searh(TIME,By.XPATH,XPATH_NAME_PLAYER).text.split(' - ')
            apuestas = scraper.elements_wait_searh(
                10, By.XPATH, XPATH_GAME_OFFERS)
            try:
                slider = scraper.element_wait_searh(5,By.XPATH, XPATH_SLIDER_TOAL_GOAL)
                if slider.get_attribute("value") != "2.5": 
                    slider.send_keys("2.5")
            except TimeoutException:
                pass
            total_mas, total_menos = [val.text for val in scraper.elements_wait_searh(TIME,By.XPATH, XPATH_GAME_TOTAL_GOAL)]
            if len(apuestas) > 4:
                final, _, doble, ambos_marcan, _, sin_empate = apuestas[0:6]
                final1, final_empate, final2 = [val.text for val in final.find_elements(By.XPATH, XPATH_GAME_PRICE)]
                doble1, doble12, doble2 = [val.text for val in doble.find_elements(By.XPATH, XPATH_GAME_PRICE)]
                ambos_si, ambos_no = [val.text for val in ambos_marcan.find_elements(By.XPATH, XPATH_GAME_PRICE)]
                sin_empate1, sin_empate2 = [val.text for val in sin_empate.find_elements(By.XPATH, XPATH_GAME_PRICE)]
            else:
                final, _, doble, sin_empate = apuestas
                final1, final_empate, final2 = [val.text for val in final.find_elements(By.XPATH, XPATH_GAME_PRICE)]
                doble1, doble12, doble2 = [val.text for val in doble.find_elements(By.XPATH, XPATH_GAME_PRICE)]
                ambos_si, ambos_no = None,None
                sin_empate1, sin_empate2 = [val.text for val in sin_empate.find_elements(By.XPATH, XPATH_GAME_PRICE)]
            data = pd.DataFrame([{
                "id_evento":event_id, "nombre_evento":event_game,
                "jugador1": jugador1, "jugador2":jugador2, 
                "final_partido1":final1,"final_partido_empate":final_empate,
                "final_partido2":final2, "total_goles_mas25":total_mas, 
                "total_goles_menos25":total_menos, "doble_oportunidad1x":doble1,
                "doble_oportunidad12":doble12,"doble_oportunidadx2":doble2,
                "ambos_marcan_si":ambos_si,"ambos_marcan_no":ambos_no,
                "sin_empate1":sin_empate1,"sin_empate2":sin_empate2,
                "fecha_juego":date_game, "timestamp":datetime.now() }])

            with engine.connect() as conn:
                try:
                    data.to_sql('betplay_football',conn, index=False, if_exists='append')
                    conn.commit()
                except IntegrityError:
                    pass
            scraper.close()
            break
        except StaleElementReferenceException:
            print("Stale")
            continue
        except TimeoutException as e:
            # exp = sys.exc_info()
            # traceback.print_exception(*exp)
            time.sleep(10)
        except Exception:
            exp = sys.exc_info()
            traceback.print_exception(*exp)
            print(link)
            return



def main(engine:Engine):
    global links

    pool = ThreadPool(4)
    links = get_links_games()
    res = []
    for link in links:
        # pool.map_async(partial(read_links,engine=engine), (link,))
        res.append(pool.apply_async(read_links,(link,engine)))
    for r in res :r.get()
    pool.close()
    pool.join()

    engine_scraper.close()