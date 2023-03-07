import os
import pandas as pd
from sqlalchemy import Column, Integer, String,  Numeric, DateTime, UniqueConstraint, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Session, relationship, Mapped, mapped_column
import contextlib

if 'db' not in os.listdir():
    os.mkdir('db')

class Base(DeclarativeBase):pass

def get_session(engine):
    session = Session(bind=engine)
    return session
    
@contextlib.contextmanager
def get_conn(engine, cleanup=False):
    conn = engine.connect()
    Base.metadata.create_all(engine)

    yield conn
    conn.close()

    if cleanup:
        Base.metadata.drop_all(engine)

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        if column.name in d:
            d[column.name] = str(getattr(row, column.name))

    return d


class Categoria(Base):
    __tablename__ = "categoria"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    sub_categorias:Mapped[list['SubCategoria']] = relationship()

class SubCategoria(Base):
    __tablename__ = "sub_categoria"
    id = Column(Integer, primary_key=True)
    nombre = Column(String, nullable=False)
    categoria_id = mapped_column(ForeignKey('categoria.id'), primary_key=True)
    deportes:Mapped[list['Deporte']] = relationship()

class Deporte(Base): pass

class Tennis(Deporte):
    """Genera un objeto de la base de datos
    """
    __tablename__ = "betplay_tennis"
    id = Column(Integer, primary_key=True)
    id_evento = Column(Integer)
    sub_categoria_id = mapped_column(ForeignKey('sub_categoria.id'))
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
        'id_evento', 'nombre_evento', 'jugador1','jugador2','marcador1','marcador2','set1_marcador','set2_marcador',
            'punto1','punto2','juego1','juego2','set1','set2','partido1','partido2',
        name='_betplay_unique_'),
    )


class Football(Deporte):
    """
        Genera un objeto de la base de datos
    """
    __tablename__ = "betplay_football"
    id = Column(Integer, primary_key=True)
    id_evento = Column(Integer)
    sub_categoria_id = mapped_column(ForeignKey('sub_categoria.id'))
    categoria = Column(String)
    jugador1 = Column(String)
    jugador2 = Column(String)
    final_partido1 = Column(Numeric)
    final_partido_empate = Column(Numeric)
    final_partido2 = Column(Numeric)
    total_goles_mas25 = Column(Numeric)
    total_goles_menos25 = Column(Numeric)
    doble_oportunidad1x = Column(Numeric)
    doble_oportunidad12 = Column(Numeric)
    doble_oportunidadx2 = Column(Numeric)
    ambos_marcan_si = Column(Numeric)
    ambos_marcan_no = Column(Numeric)
    sin_empate1 = Column(Numeric)
    sin_empate2 = Column(Numeric)
    fecha_juego = Column(DateTime)
    resultado1 = Column(Integer)
    resultado2 = Column(Integer)
    timestamp = Column(DateTime)
    __table_args__ = (UniqueConstraint(
        'id_evento', 'nombre_evento', 'jugador1','jugador2','final_partido1','final_partido_empate','final_partido2','total_goles_mas25',
            'total_goles_menos25','doble_oportunidad1x','doble_oportunidad12','doble_oportunidadx2','ambos_marcan_si','ambos_marcan_no'
            ,'sin_empate1','sin_empate2','fecha_juego',
        name='_betplay_unique_football'),
    )
