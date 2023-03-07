
# import requests
# import json

# #ncid=1678117253369&
# params = dict(lang='es_CO',market='CO',client_id=2,channel_id=1,useCombined='true')
# res = requests.get("https://na-offering-api.kambicdn.net/offering/v2018/betplay/listView/tennis.json", params = params)
# events = [event for event in res.json()["events"] if event["event"]["state"] == "STARTED"]
# with open("src/assets/partidos_live.json", "w") as p:
#     json.dump(events, p)

import re, sys

import itertools
print([i for i in filter(lambda x: x % 5, itertools.islice(itertools.count(5), 10 ) ) ])