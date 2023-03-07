# from scraping.betplay_scraper.football.betplay_scraper_football import main
from scraping.betplay_scraper.football.betplay_scraper_results_football import get_country_id, get_category_by_country
from sqlalchemy import create_engine
from scraping.betplay_scraper.tennis.constants import CONNECTION_URI
from db.db import Base

engine = create_engine(CONNECTION_URI, echo = False)
Base.metadata.create_all(engine)

# main(engine)
get_category_by_country(engine,'')