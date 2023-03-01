import os
import pandas as pd
from sqlalchemy import text, Column, Integer, String,  Numeric, DateTime, UniqueConstraint
from sqlalchemy.orm import declarative_base, DeclarativeBase, Session
import contextlib

if 'db' not in os.listdir():
    os.mkdir('db')
Base: DeclarativeBase = declarative_base()


class DataBase(Base):
    """Genera un objeto de la base de datos
    """
    __tablename__ = "betplay"
    id = Column(Integer, primary_key=True)
    id_evento = Column(Integer)
    nombre_evento = Column(Integer)
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

    @contextlib.contextmanager
    @staticmethod
    def get_session(engine, cleanup=False):
        session = Session(bind=engine)
        Base.metadata.create_all(engine)

        try:
            yield session
        except Exception:
            session.rollback()
        finally:
            session.close()

        if cleanup:
            Base.metadata.drop_all(engine)

    @contextlib.contextmanager
    @staticmethod
    def get_conn(engine, cleanup=False):
        conn = engine.connect()
        Base.metadata.create_all(engine)

        yield conn
        conn.close()

        if cleanup:
            Base.metadata.drop_all(engine)
