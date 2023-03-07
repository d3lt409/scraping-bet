import os
from sqlalchemy import text, Column, Integer, String,  Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import DeclarativeBase, Session
from db.constants import *

if 'db' not in os.listdir():
    os.mkdir('db')
 
class Base(DeclarativeBase): pass

def get_session(engine, cleanup=False):
    session = Session(bind=engine)
    Base.metadata.create_all(engine)

    try:
        return session
    except Exception:
        session.rollback()
    finally:
        session.close()

    if cleanup:
        Base.metadata.drop_all(engine)


def get_conn(engine, cleanup=False):
    conn = engine.connect()
    Base.metadata.create_all(engine)

    yield conn
    conn.close()

    if cleanup:
        Base.metadata.drop_all(engine)

class Tenis(Base):
    """Genera un objeto de la base de datos
    """
    __tablename__ = "betplay_tenis"
    id = Column(Integer, primary_key=True)
    id_evento = Column(Integer)
    nombre_evento = Column(String)
    jugador1 = Column(String)
    jugador2 = Column(String)
    marcador1 = Column(String)
    marcador2 = Column(String)
    servicio = Column(String)
    set1_marcador = Column(String)
    set2_marcador = Column(String)
    punto1 = Column(Numeric)
    punto2 = Column(Numeric)
    juego1 = Column(Numeric)
    juego2 = Column(Numeric)
    set1 = Column(Numeric)
    set2 = Column(Numeric)
    partido1 = Column(Numeric)
    partido2 = Column(Numeric)
    timestamp = Column(DateTime)
    __table_args__ = (UniqueConstraint(
        'id_evento', 'nombre_evento', 'jugador1','jugador2','set1_marcador','set2_marcador',
            'punto1','punto2','juego1','juego2','set1','set2','partido1','partido2',
        name='_betplay_unique_'),
    )



class Football(Base):
    """
        Genera un objeto de la base de datos
    """
    __tablename__ = "betplay_football"
    id = Column(Integer, primary_key=True)
    id_evento = Column(Integer)
    nombre_evento = Column(String)
    categoria = Column(String)
    jugador1 = Column(String)
    jugador2 = Column(String)
    final_partido1 = Column(Numeric)
    final_partido_empate = Column(Numeric)
    final_partido2 = Column(Numeric)
    for num in MAS_MENOS:
        exec(f'total_goles_mas{num} = Column(Numeric)')
        exec(f'total_goles_menos{num} = Column(Numeric)')
    doble_oportunidad1x = Column(Numeric)
    doble_oportunidad12 = Column(Numeric)
    doble_oportunidadx2 = Column(Numeric)
    ambos_marcan_si = Column(Numeric)
    ambos_marcan_no = Column(Numeric)
    for val in RESULTADOS:
        exec(f'resultado_{val} = Column(Numeric)')
    sin_empate1 = Column(Numeric)
    sin_empate2 = Column(Numeric)
    fecha_juego = Column(DateTime)
    resultado1 = Column(Integer)
    resultado2 = Column(Integer)
    timestamp = Column(DateTime)
    __table_args__ = (UniqueConstraint(
        'id_evento', 'nombre_evento', 'jugador1','jugador2',
        exec(",".join([f'total_goles_mas{num}' for num in MAS_MENOS])),
        exec(",".join([f'total_goles_menos{num}' for num in MAS_MENOS])),
        'final_partido1','final_partido_empate','final_partido2','total_goles_mas25','doble_oportunidad1x','doble_oportunidad12','doble_oportunidadx2','ambos_marcan_si','ambos_marcan_no',
        exec(",".join([f'resultado_{num}' for num in RESULTADOS])), 'sin_empate1','sin_empate2','fecha_juego',
        name='_betplay_unique_football'),
    )