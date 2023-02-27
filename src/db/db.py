import pandas as pd
from sqlalchemy import create_engine,text
from sqlalchemy.exc import OperationalError
from datetime import datetime
import time

CONNECTION_URI = "sqlite:///db/Apuestas.sqlite"
CLICK = "arguments[0].click();"

class DataBase():
    """Genera un objeto de la base de datos
    """
    def __init__(self,name_data_base:str) -> None:
        self.engine = create_engine(CONNECTION_URI, echo = False)
        self.name_data_base = name_data_base

        
    def to_data_base(self,data:pd.DataFrame):
        while True:
            try:
                data.to_sql(self.name_data_base,self.engine, if_exists='append', index=False)
                break
            except OperationalError:
                print("Por favor guarde cambios en la base de datos")
                time.sleep(5)
                continue

    def consulta_sql(self,sql:str):
        with self.engine.connect() as conn:
            return conn.execute(text(sql)).fetchall()
    

    def consulta_sql_unica(self,sql:str):
        with self.engine.connect() as conn:
            res = conn.execute(text(sql)).first()
            if res: return res
            return None 
        
    def last_item_db(self):
        date = datetime.now().strftime("%Y-%m-%d")
        res = self.consulta_sql_unica(f"""select Departamento,Categoria,Sub_categoria from {self.name_data_base} 
                where Fecha_resultados = {date!r} AND id = (select max(id) from {self.name_data_base});""")
        if res:
            res = dict(res)
        return res
    
    def close(self):
        self.engine.dispose()