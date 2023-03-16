import time
import traceback
import sys
import pandas as pd
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException

from multiprocessing.pool import ThreadPool
from datetime import datetime, timedelta, timezone
from sqlalchemy import Engine
from sqlalchemy.exc import IntegrityError
from functools import partial

from models.scraper import Scraper
from scraping.betplay_scraper.football.constants import *


links = []
links_done = []
script_date = '''
    var f = new Date(arguments[0]);
    return f.toISOString()+' '+f.toTimeString();
'''
#text = WebDriverWait(driver, 20).until(lambda driver: driver.execute_script(f'return {script}'))
def get_links_games():
    global links, links_done, engine_scraper
    while engine_scraper.driver.current_url != PAGE_URL: 
        engine_scraper.close()
        engine_scraper = Scraper(PAGE_URL)
        time.sleep(5)
    time.sleep(3)

    try:
        engine_scraper.element_click_wait_searh(TIME, By.XPATH, XPATH_BUTTON_FOOTBALL).click()
        engine_scraper.element_click_wait_searh(TIME, By.XPATH, XPATH_DROPDOWN_SORT).click()
        engine_scraper.element_click_wait_searh(TIME, By.XPATH, XPATH_ITEM_HOUR).click()
        time.sleep(3)
        try:
            for el in engine_scraper.elements_wait_searh(4, By.XPATH, XPATH_DROPDOWN_LIST_HOURS): 
                engine_scraper.click(el)
        except TimeoutException: pass
        time.sleep(3)
        try:
            for el in engine_scraper.elements_wait_searh(4, By.XPATH, XPATH_DROPDWN_LIST_GAMES): 
                engine_scraper.click(el)
        except TimeoutException: pass
        links = links + \
            [val.get_attribute("href") for val in engine_scraper.elements_wait_searh(
                TIME, By.XPATH, XPATH_GAMES)]
        if len(links_done) == 0: return
        for i in range(len(links)):
            if links[i] in links_done:
                del links[i]

    except Exception as e:
        exp = sys.exc_info()
        traceback.print_exception(*exp)



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
        scraper.close()
        return 
    time.sleep(3)
    time_elemnt = scraper.element_wait_searh(TIME,By.XPATH, XPATH_START_GAME)
    date_game = scraper.element_wait_lambda_return(int(time_elemnt.get_attribute("datetime")),script_date)
    date_game = datetime.fromisoformat(date_game.replace(".000Z",""))
    try:
        for element in scraper.elements_wait_searh(3,By.XPATH, XPATH_BUTTON_ALL_OFFERS): 
            element.click()
            time.sleep(1)
    except TimeoutException: pass
    while True:
        try:
            jugador1, jugador2 = scraper.element_wait_searh(TIME,By.XPATH,XPATH_NAME_PLAYER).text.split(' - ')
            apuestas = scraper.elements_wait_searh(
                10, By.XPATH, XPATH_GAME_OFFERS)
            resultados = {}
            mas_menos = {}
            if len(apuestas) > 4:
                final=total_mas_menos=doble=ambos_marcan=resultados_elements=sin_empate = None
                for ap in apuestas:
                    if final and total_mas_menos and doble and ambos_marcan and resultados_elements and sin_empate: break
                    if ap.text.startswith("Final del partido"): final = ap
                    elif ap.text.startswith("Total de goles"): total_mas_menos = ap
                    elif ap.text.startswith("Doble Oportunidad"): doble = ap
                    elif ap.text.startswith("Ambos Equipos"): ambos_marcan = ap
                    elif ap.text.startswith("Resultado Correcto"): resultados_elements = ap
                    elif ap.text.startswith("Apuesta sin empate"): sin_empate = ap
                for el in total_mas_menos.find_elements(By.XPATH, XPATH_RESULT_GAME):
                    dato = el.text.replace(" de","").split("\n")
                    if float(dato[1]) > 5.5: continue
                    if len(dato) == 3:
                        tipo, valor, apuesta = dato
                        mas_menos[f"total_goles_{tipo.replace('á','a').lower()}{valor.replace('.','')}"] = apuesta
                    else: 
                        tipo, valor = dato
                        mas_menos[f"total_goles_{tipo.replace('á','a').lower()}{valor.replace('.','')}"] = None
                
                for el in resultados_elements.find_elements(By.XPATH, XPATH_RESULT_GAME):
                    dato = el.text.split("\n")
                    if len(dato) > 1:
                        init, end = dato[0].split("-")
                        if int(init) > 5 or int(end) > 5: continue
                        resultados[f"resultado_{init}_{end}"] = dato[1]
                    else:
                        init, end = dato[0].split("-")
                        if int(init) > 5 or int(end) > 5: continue
                        resultados[f"resultado_{init}_{end}"] = None
                final1, final_empate, final2 = [val.text for val in final.find_elements(By.XPATH, XPATH_GAME_PRICE)]
                doble1, doble12, doble2 = [val.text for val in doble.find_elements(By.XPATH, XPATH_GAME_PRICE)]
                try:
                    ambos_si, ambos_no = [val.text for val in ambos_marcan.find_elements(By.XPATH, XPATH_GAME_PRICE)]
                except AttributeError: 
                    ambos_si = ambos_no = None
                sin_empate1, sin_empate2 = [val.text for val in sin_empate.find_elements(By.XPATH, XPATH_GAME_PRICE)]
            else:
                final, total_mas_menos, doble, sin_empate = apuestas
                for el in total_mas_menos.find_elements(By.XPATH, XPATH_RESULT_GAME):
                    dato = el.text.replace(" de","").split("\n")
                    if float(dato[1]) > 5.5: continue
                    if len(dato) == 3:
                        tipo, valor, apuesta = dato
                        mas_menos[f"total_goles_{tipo.replace('á','a').lower()}{valor.replace('.','')}"] = apuesta
                    else: 
                        tipo, valor = dato
                        mas_menos[f"total_goles_{tipo.replace('á','a').lower()}{valor.replace('.','')}"] = None
                final1, final_empate, final2 = [val.text for val in final.find_elements(By.XPATH, XPATH_GAME_PRICE)]
                doble1, doble12, doble2 = [val.text for val in doble.find_elements(By.XPATH, XPATH_GAME_PRICE)]
                ambos_si, ambos_no = None,None
                sin_empate1, sin_empate2 = [val.text for val in sin_empate.find_elements(By.XPATH, XPATH_GAME_PRICE)]
            data = pd.DataFrame([{**{
                "id_evento":event_id, "nombre_evento":event_game,
                "jugador1": jugador1, "jugador2":jugador2, 
                "final_partido1":final1,"final_partido_empate":final_empate,
                "final_partido2":final2, "doble_oportunidad1x":doble1,
                "doble_oportunidad12":doble12,"doble_oportunidadx2":doble2,
                "ambos_marcan_si":ambos_si,"ambos_marcan_no":ambos_no,
                "sin_empate1":sin_empate1,"sin_empate2":sin_empate2,
                "fecha_juego":date_game, "timestamp":datetime.now() }, **resultados, **mas_menos}])

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
        except ValueError:
            if scraper.driver.current_url != link or date_game >= datetime.now():
                return
            scraper.driver.refresh()
            time.sleep(4)
            scraper.driver.get(link)
            continue
        except Exception:
            exp = sys.exc_info()
            traceback.print_exception(*exp)
            print(link)
            return



def main(engine:Engine):
    global links, engine_scraper
    engine_scraper = Scraper(PAGE_URL)
    pool = ThreadPool(4)
    response = []
    get_links_games()
    timeout = time.time() + 60
    while time.time() <= timeout:
        if len(links) != 0:
            link = links.pop()
            # pool.map_async(partial(read_links,engine=engine), (link,))
            response.append(pool.apply_async(read_links,(link,engine)))
            links_done.append(link)
        else:
            for res in response: pool.map_async(res.get,())
            response = []
            time.sleep(120)
            engine_scraper.driver.get(PAGE_URL)
            time.sleep(10)
            pool.apply(get_links_games,())

    pool.close()
    pool.join()

    engine_scraper.close()