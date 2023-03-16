from googletrans.client import Translator
from googletrans.models import Translated
from googletrans.gtoken import TokenAcquirer

translator = Translator()
translation:Translated = translator.translate("Reserves Leagues", dest='es')
print(translation)