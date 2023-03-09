
import itertools

CONNECTION_URI = "sqlite:///db/Apuestas.sqlite"

MAS_MENOS = [str(i+0.5).replace(".","") for i in range(6)]
RESULTADOS = list(itertools.chain(*[[f"{i}_{j}" for i in range(6)] for j in range(6)])) 