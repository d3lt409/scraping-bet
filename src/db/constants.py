
import itertools

MAS_MENOS = [str(i+0.5) for i in range(1,6)]
RESULTADOS = list(itertools.chain(*[[f"{i}-{j}" for i in range(6)] for j in range(6)])) 