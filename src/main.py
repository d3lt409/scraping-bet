from scraping.betplay_scraper.football.football import main as main_football
from scraping.betplay_scraper.tennis.tennis import main as main_tennis
from scraping.betplay_scraper.football.results_football import main as main_results_football
from db.db import Base, new_engine
import click

engine = new_engine()
Base.metadata.create_all(engine)

@click.group()
def main_click():
    pass

@main_click.command(name = "football")
def football_click():
    main_football(engine)

@main_click.command(name = "tennis")
def tennis_click():
    main_tennis(engine)

@main_click.command(name = "results_football")
def results_football_click():
    main_results_football(engine)

if __name__ == '__main__':
    main_click()