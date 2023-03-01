from scraping.betplay_scraper.betplay_scraper import main
from sqlalchemy import create_engine
from scraping.betplay_scraper.constants import CONNECTION_URI
from db.db import Base

engine = create_engine(CONNECTION_URI, echo = False)
Base.metadata.create_all(engine)

main(engine)