
PAGE_URL = "https://betplay.com.co/apuestas#filter/all/all/all/all/starting-soon"
NAME_DATA_BASE = "betplay_football"
CONNECTION_URI = "sqlite:///db/Apuestas.sqlite"
TIME = 15

COLUMNS = ["id_evento","nombre_evento","jugador1", "jugador2","marcador1","marcador2", "servicio",
           "set1_marcador","set2_marcador","punto1","punto2","juego1","juego2","set1",
           "set2","partido1","partido2","timestamp"]

XPATH_BUTTON_FOOTBALL = "//div[@class='KambiBC-filter-events-by-sports-icon-container KambiBC-filter-events-by-sports-icon-container--small'][descendant::p[text()='Fútbol']]"
XPATH_DROPDOWN_SORT = "//div[@class='KambiBC-dropdown KambiBC-dropdown--event-list-sort-dropdown']"
XPATH_ITEM_HOUR = "//li[@class='KambiBC-dropdown__option ignore-react-onclickoutside']"
XPATH_DROPDOWN_LIST_HOURS = "//div[@class='CollapsibleContainer__CollapsibleWrapper-sc-14bpk80-0 gOgibc KambiBC-betty-collapsible KambiBC-collapsible-container KambiBC-mod-event-group-container']"
XPATH_DROPDWN_LIST_GAMES = "//div[@class='CollapsibleContainer__CollapsibleWrapper-sc-14bpk80-0 kkAwUc KambiBC-betty-collapsible-container'][descendant::header[@class='CollapsibleContainer__HeaderWrapper-sc-14bpk80-1 hDaRiN']]"

XPATH_GAMES = "//a[@class='KambiBC-event-item__link']"
XPATH_START_GAME = "//time[@class='KambiBC-single-event-card__starttime']"
XPATH_EVENT_GAME = "//span[@class='KambiBC-modularized-event-path__fragmentcontainer']"

XPATH_GAME_OFFERS = "//div[@class='KambiBC-bet-offer-subcategory__container']"


XPATH_NAME_PLAYER = "//span[@class='KambiBC-modularized-scoreboard__participant-name']"
XPATH_GAME_PRICE = ".//div[@class='OutcomeButton__Odds-sc-lxwzc0-6 gKPYii' and text()!= '']"

XPATH_SLIDER_TOAL_GOAL = "//input[@class='KambiBC-slider']"
XPATH_GAME_TOTAL_GOAL = "//div[@class='KambiBC-bet-offer-subcategory__container'][descendant::h3/span[text()='Total de goles']]//div[@class='OutcomeButton__Wrapper-sc-lxwzc0-0 bJwiPp'][descendant::div[text()='2.5']]//div[@class='OutcomeButton__Odds-sc-lxwzc0-6 gKPYii']"

