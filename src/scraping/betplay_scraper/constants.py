
PAGE_URL = "https://betplay.com.co/apuestas#filter/tennis"
NAME_DATA_BASE = "betplay"
TIME = 30

COLUMNS = ["id_evento","nombre_evento","jugador1", "jugador2","marcador1","marcador2", "set1_marcador","set2_marcador","punto1","punto2","juego1","juego2","set1","set2","partido1","partido2","timestamp"]
DTYPE_COLUMNS = {"id_evento":int,"marcador1":int, "marcador2":int, "set1_marcador":int, "set2_marcador":int, 
                 "punto1": float, "punto2": float, "punto1": float, "juego1": float, "juego2": float, "set1": float, 
                 "set2": float, "partido1": float, "partido2": float }

BUTTON_GAMES = "//div[contains(@class,'CollapsibleContainer__CollapsibleWrapper-sc-14bpk80-0 gOgibc KambiBC-betty-collapsible KambiBC-collapsible-container KambiBC-mod-event-group-container')][descendant::span[text()='En vivo']]"
XPATH_GAMES = "//div[contains(@class,'CollapsibleContainer__CollapsibleWrapper-sc-14bpk80-0 gOgibc KambiBC-betty-collapsible KambiBC-collapsible-container KambiBC-mod-event-group-container')][1]//ul[@class='KambiBC-list-view__column KambiBC-list-view__event-list']//a"
XPATH_GAME_OFFERS = "p[@class='KambiBC-bet-offer-categories__no-betoffers-msg']"

XPATH_POINT_ITEM = "//li[@data-label='Point']"
XPATH_SET_ITEM = "//li[@data-label='Set']"
XPATH_GAME_ITEM = "//li[@data-label='Game']"
XPATH_MATCH_ITEM = "//li[@data-label='Match']"

XPATH_EVENT_GAME = "//span[@class='KambiBC-modularized-event-path__fragmentcontainer']"

XPATH_SET_VALUES = "//div[@class='KambiBC-tennis-scoreboard__set KambiBC-tennis-scoreboard__set--playing']//span[@class='']"
XPATH_SCORE_GAME_VALUE = "//div[@class='KambiBC-scoreboard-container__scorecard-score']/span"
XPATH_SCORE_GAME_NAME = "//span[@class='KambiBC-scoreboard-container__participant-name']"
XPATH_GAME_NAME = "//li[@class='KambiBC-bet-offer-subcategory KambiBC-bet-offer-subcategory--onecrosstwo'][1]//div[@class='OutcomeButton__LabelAndExtras-sc-lxwzc0-1 grSrok' and text() != '']"
XPATH_GAME_PRICE = "//li[@class='KambiBC-bet-offer-subcategory KambiBC-bet-offer-subcategory--onecrosstwo'][1]//div[@class='OutcomeButton__Odds-sc-lxwzc0-6 gKPYii' and text() != '']"

