import time
import traceback
import sys
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException
from sqlalchemy import Engine, func
from utils.util import elimina_tildes, re, datetime


from db.db import get_session, Football
from models.scraper import Scraper
from scraping.betplay_scraper.football.results.constanst import *


def get_name(value:str):
    l = value.replace(" de "," ").replace("  "," ").strip().split()
    l = sorted(l, key=lambda x: len(x))
    if "Reserves" in l: l.remove("Reserves")
    if len(l) >= 2:
        if len(l[0]) > 4: return re.sub("\W.+","",l[0])
    return re.sub("\W.+","", l[-1])

def save_results(engine, id , res1,res2):
    with get_session(engine) as s:
        football = s.query(Football).get(id)
        football.resultado1 = res1
        football.resultado2 = res2
        s.commit()

def get_first_separator(value:str):
    it = value.split("-")
    if len(it) > 2:
        return f"{it[0]}-{' '.join(it[1:])}"
    return value

def main(engine: Engine):
    global engine_scraper
    engine_scraper = Scraper(PAGE_URL_RESULTS)
    with get_session(engine) as s:
        players = s.query(Football.id, Football.nombre_evento, Football.jugador1, Football.jugador2).where(
            Football.resultado1 == None, Football.resultado2 == None, func.date(Football.fecha_juego) < datetime.utcnow().date()).all()
        for id, evento, j1, j2 in players:
            for text in DELETE_TEXT_PLAYERS: j1 = j1.replace(text, "").strip(); j2 = j2.replace(text, "").strip()
            evento = get_first_separator(elimina_tildes(evento).lower())
            print(evento)
            cat_tipo:list[str] = [val.replace("betplay", "").strip() for val in evento.split("-")]
            if len(cat_tipo) == 1:
                if cat_tipo[0] in DICT_MODISM: 
                    url = f"https://www.flashscore.co/futbol/{DICT_MODISM[cat_tipo[0]]}/{cat_tipo[0].replace(' ','-')}/resultados"
                    engine_scraper.driver.get(url)
                    results(engine, id, j1,j2)
                else: get_result_google(engine, id, j1,j2)
            else:
                pais, cat = [val.replace(" ","-") for val in cat_tipo]
                if pais.__contains__("el-salvador"):
                    url = f"https://www.flashscore.co/futbol/{pais}/primera-division/resultados"
                elif pais in COUNTRIES_DIVS and cat in COUNTRIES_DIVS[pais]:
                    url = f"https://www.flashscore.co/futbol/{pais}/{COUNTRIES_DIVS[pais][cat]}/resultados"
                else:
                    url = f"https://www.flashscore.co/futbol/{pais}/{cat}/resultados"
                time.sleep(3)
                engine_scraper.driver.get(url)
                results(engine, id, j1,j2)

    engine_scraper.close()

def results(engine, id, j1,j2):
    time.sleep(3)
    while True:
        try:
            games = engine_scraper.elements_wait_searh(TIME,By.XPATH,XPATH_GAMES_RESULTS)
            break
        except TimeoutException:
            get_result_google(engine,id,j1,j2)
            return
        except UnexpectedAlertPresentException:
            time.sleep(2)
    j1_names = elimina_tildes(j1).replace("-", " ").split()
    j2_names = elimina_tildes(j2).replace("-", " ").split()
    print(j1_names,j2_names)
    for game in games:
        if game.text.__contains__("tras pen.\n"): text = elimina_tildes(game.text.replace("tras pen.\n","").strip())
        else: text = elimina_tildes(game.text)
        for j in j1_names:
            if text.__contains__(j):
                for k in j2_names:
                    if text.__contains__(k):
                        res = text.split("\n")[1:5]
                        print(res)
                        if res[0].title().__contains__(j.capitalize()): save_results(engine,id, res[-2], res[-1])
                        elif res[0].title().__contains__(k.capitalize()): save_results(engine,id, res[-1], res[-2])
                        else: save_results(engine,id, res[-2], res[-1])
                        return
    get_result_google(engine,id,j1,j2)
    return

def get_result_google(engine, id, j1,j2):
    url = PAGE_URL_GOOGLE.format(j1.replace(" ","+"), j2.replace(" ","+"))
    j1, j2 = elimina_tildes(j1), elimina_tildes(j2)
    engine_scraper.driver.get(url)
    try:
        game = engine_scraper.element_wait_searh(TIME,By.XPATH, XPATH_GAMES_RESULTS_GOOGLE)
        res = game.text.split("\n")[1:6]
        print(res)
        name1, res1,res2, name2 = res[0],res[1], res[3], res[4]
        if not res[1].isdigit() or not res[3].isdigit():
            game = engine_scraper.element_wait_searh(TIME,By.XPATH, XPATH_GAMES_RESULTS_GOOGLE_OTHER)
            text = game.text.split("\n")
            res = text[1:4]+text[6].replace("Total: ","").replace(" ","").split("a")
            name1, name2, res1, res2 = res[0],res[2], res[3], res[4]
        name1, name2 = elimina_tildes(name1), elimina_tildes(name2)
        res = [elimina_tildes(val) for val in res]
        j1_names = j1.replace("-", " ").split()
        j2_names = j2.replace("-", " ").split()
        print(j1_names, j2_names, name1, name2)
        game_text = elimina_tildes(game.text)
        for j in j1_names:
            if j in game_text:
                for k in j2_names:
                    if k in j2_names:
                        print(res, j1,j2)
                        if name1.title().__contains__(j.capitalize()): save_results(engine,id, res1, res2)
                        elif name1.title().__contains__(k.capitalize()): save_results(engine,id, res2, res1)
                        elif name2.title().__contains__(j.capitalize()): save_results(engine,id, res2, res1)
                        else: save_results(engine,id, res1, res2)
                        return
    except TimeoutException:
        return 
    except IndexError:
        exp = sys.exc_info()
        traceback.print_exception(*exp)