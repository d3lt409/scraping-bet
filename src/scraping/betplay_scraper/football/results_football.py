import time
import traceback
import sys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, StaleElementReferenceException
from multiprocessing.pool import ThreadPool
from sqlalchemy import Engine, Date, cast, func
from utils.util import elimina_tildes, re, datetime


from db.db import get_session, Football, row2dict
from models.scraper import Scraper
from scraping.betplay_scraper.football.constants import *


DICT_MODISM = {"sudamericana":"sudamerica", "europea":"europa","concacaf":"norte-centroamerica-y-caribe", "champions league":"europa", "copa libertadores":"sudamerica","concacaf":"norte centroamerica y caribe"}
XPATH_GAMES_RESULTS = "//div[contains(@class,'event__match event__match--static')]"
DELETE_TEXT_PLAYERS = ["Atlético","Deportivo","Club","Academia","Atletico"]
DELETE_TEXT_CATEGORIES = []
PAGE_URL_GOOGLE = "https://www.google.com/search?q={0}+vs+{1}&oq={0}+vs+{1}"

XPATH_GAMES_RESULTS_GOOGLE = "//div[@class='imso-ani imso_mh__tas']"

def get_name(value:str):
    l = value.replace(" de "," ").replace("  "," ").strip().split()
    l = sorted(l, key=lambda x: len(x))
    if "Reserves" in l: l.remove("Reserves")
    if len(l) >= 2:
        if len(l[0]) > 4: return re.sub("\W.+","",l[0])
    return re.sub("\W.+","", l[-1])

def main(engine: Engine):
    global engine_scraper
    engine_scraper = Scraper(PAGE_URL_RESULTS)
    with get_session(engine) as s:
        players = s.query(Football.id, Football.nombre_evento, Football.jugador1, Football.jugador2).where(
            Football.resultado1 == None, Football.resultado2 == None, func.date(Football.fecha_juego) < datetime.utcnow().date()).all()
        for id, evento, j1, j2 in players:
            for text in DELETE_TEXT_PLAYERS: j1 = j1.replace(text, "").strip(); j2 = j2.replace(text, "").strip()
            evento = elimina_tildes(evento).lower()
            cat_tipo:list[str] = [val.replace("betplay", "").strip() for val in evento.split("-")]
            if len(cat_tipo) == 1:
                if get_result_google(engine, id, j1,j2): 
                    continue
                    for k,v in DICT_MODISM.items():
                        if cat_tipo[0].__contains__(k):
                            for d in DELETE_TEXT_CATEGORIES: cat_tipo[0] = cat_tipo[0].replace(d.lower(),"").strip()
                            if cat_tipo[0].__contains__("concacaf") and cat_tipo[0].__contains__("champions"):
                                url = f"https://www.flashscore.co/futbol/{v}/concacaf-liga-de-campeones/resultados"
                                break
                            url = f"https://www.flashscore.co/futbol/{v}/{cat_tipo[0].replace(' ','-')}/resultados"
                            break
            else:
                pais, cat = [val.replace(" ","-") for val in cat_tipo]
                if pais.__contains__("el-salvador"):
                    url = f"https://www.flashscore.co/futbol/{pais}/primera-division/resultados"
                else: url = f"https://www.flashscore.co/futbol/{pais}/{cat}/resultados"
                time.sleep(3)
                engine_scraper.driver.get(url)
                results(engine, id, j1,j2)
    engine_scraper.close()

def results(engine, id, j1,j2):
    try:
        games = engine_scraper.elements_wait_searh(TIME,By.XPATH,XPATH_GAMES_RESULTS)
    except TimeoutException:
        get_result_google(engine,id,j1,j2)
        return
    j1, j2 = get_name(j1), get_name(j2)
    for game in games:
        if game.text.__contains__("tras pen.\n"): text = elimina_tildes(game.text.replace("tras pen.\n","").strip())
        else: text = elimina_tildes(game.text)
        if text.title().__contains__(j1.capitalize()) and text.title().__contains__(j2.capitalize()):
            res = game.text.split("\n")[1:5]
            print(res)
            if res[0].title().__contains__(j1.capitalize()):
                with get_session(engine) as s:
                    football = s.query(Football).get(id)
                    football.resultado1 = res[-2]
                    football.resultado2 = res[-1]
                    s.commit()
            elif res[0].title().__contains__(j2.capitalize()):
                with get_session(engine) as s:
                        football = s.query(Football).get(id)
                        football.resultado2 = res[-2]
                        football.resultado1 = res[-1]
                        s.commit()
            else:
                with get_session(engine) as s:
                    football = s.query(Football).get(id)
                    football.resultado1 = res[-2]
                    football.resultado2 = res[-1]
                    s.commit()
            return

def get_result_google(engine, id, j1,j2):
    print(j1,j2)
    url = PAGE_URL_GOOGLE.format(j1.replace(" ","+"), j2.replace(" ","+"))
    j1, j2 = get_name(j1), get_name(j2)
    engine_scraper.driver.get(url)
    try:
        game = engine_scraper.element_wait_searh(TIME,By.XPATH, XPATH_GAMES_RESULTS_GOOGLE)
        res = game.text.split("\n")[1:6]
        print(res, j1,j2)
        if res[0].title().__contains__(j1.capitalize()):
            with get_session(engine) as s:
                football = s.query(Football).get(id)
                football.resultado1 = res[1]
                football.resultado2 = res[3]
                s.commit()
        elif res[0].title().__contains__(j2.capitalize()):
            with get_session(engine) as s:
                    football = s.query(Football).get(id)
                    football.resultado2 = res[1]
                    football.resultado1 = res[3]
                    s.commit()
        return True
    except TimeoutException:
        return False