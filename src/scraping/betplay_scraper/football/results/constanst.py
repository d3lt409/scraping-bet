PAGE_URL_RESULTS = "https://www.flashscore.co/"
PAGE_URL_GOOGLE = "https://www.google.com/search?q={0}+vs+{1}&oq={0}+vs+{1}"
NAME_DATA_BASE = "betplay_football"
CONNECTION_URI = "sqlite:///db/Apuestas.sqlite"
TIME = 5

DICT_MODISM = {"sudamericana":"sudamerica", "europea":"europa","concacaf":"norte-centroamerica-y-caribe", "champions league":"europa", "copa libertadores":"sudamerica","concacaf":"norte centroamerica y caribe"}
XPATH_GAMES_RESULTS = "//div[contains(@class,'event__match event__match--static')]"
DELETE_TEXT_PLAYERS = ["Atlético","Deportivo","Club","Academia","Atletico"]
DELETE_TEXT_CATEGORIES = []


COUNTRIES_DIVS = {"argentina":{"reserves-leagues":"liga-profesional","femenino-(f)":"primera-a-femenina"}, 
                  "mexico":{"liga-premier":"liga-premier-serie-a"},
                  "brasil":{
                            "campeonato-brasileiro-sub20":"brasileirao-sub-20",
                            "goiano":"campeonato-goiano",
                            "gaucho":"campeonato-gaucho",
                            "paraense":"campeonato-paraense",
                            "mineiro":"campeonato-mineiro"
                            },
                  "francia":{"d1-femenina":"division-1-femenina"},
                  "irlanda":{"1ª-division":"division-1"},
                  "belgica":{"eerste-klasse-amateurs":"national-division-1"},
                  "guatemala":{"liga-nacional-guatemala":"liga-nacional"}}

XPATH_GAMES_RESULTS_GOOGLE = "//div[@class='imso-ani imso_mh__tas']"
XPATH_GAMES_RESULTS_GOOGLE_OTHER = "//div[@class='imso_mh__tm-a-sts']"