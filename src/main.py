# from scraping.betplay_scraper.football.football import main
# from scraping.betplay_scraper.tennis.tennis import main
from scraping.betplay_scraper.football.results_football import main
from db.db import Base, new_engine

engine = new_engine()
Base.metadata.create_all(engine)
main(engine)