from models.scraper import Scraper
from db.db import Football, get_session, or_
import json
from selenium.webdriver.common.by import By

# engine_scraper = Scraper("https://s5.sir.sportradar.com/betplay/es/1")

TIME = 5
XPATH_PAISES_TAG = "//a[@class='list-group-item'][descendant::text()='{0}']"
URL_PAIS = "https://s5.sir.sportradar.com/betplay/es/1/category/{0}"


def get_categoria_id(engine):
    with get_session(engine) as se:
        res = se.query(Football.nombre_evento).where(
            or_(Football.resultado1 == None, Football.resultado2 == None)).all()
        paises = set([r[0].split("-")[0] for r in res])

    with open("src/assets/football/arguments.json", "r") as fp:
        id_paises = json.load(fp)
        for pais in paises:
            if pais not in id_paises:
                id_paises[pais] = {"id":engine_scraper.element_wait_searh(
                    TIME, By.XPATH, XPATH_PAISES_TAG.format(pais)).get_attribute("href").split("/")[-1]}

    with open("src/assets/football/arguments.json", "w", encoding='utf-8') as fp:
        json.dump(id_paises, fp, ensure_ascii=False)

    return id_paises


def get_category_by_country(engine,country:str):
    with get_session(engine) as se:
        res = se.query(Football.nombre_evento).where(
                or_(Football.resultado1 == None, Football.resultado2 == None)).all()
        paises = list(map(lambda val: {val[0]:val[1]}, [r[0].split("-") for r in res]))
    