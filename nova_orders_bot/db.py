import datetime
from pathlib import Path

from sqlalchemy import *
from sqlalchemy import event
from sqlalchemy.orm import Session, declarative_base, relationship

engine = create_engine("postgresql+psycopg2://nova_user:Ubuntu11!!@localhost/nova_bd")
session = Session(bind=engine)
BASE_DIR = Path(__file__).resolve().parent

Base = declarative_base()

class User(Base):
    __tablename__ = 'user_bot'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id = Column(BigInteger, nullable=False, unique=True)
    status = Column(Integer, default=0)  # 0 - обычный, 1 - админ, 2 - исполнитель
    username = Column(Text, nullable=False, unique=True)
    time_zone = Column(Integer, nullable=False, default=0)

class Orders(Base):
    __tablename__ = 'orders'
    id = Column(Integer, primary_key=True, autoincrement=True)
    tg_id_client = Column(BigInteger, nullable=False)
    username_client = Column(Text, nullable=True)
    tg_id_executor = Column(BigInteger, nullable=True)
    username_executor = Column(Text, nullable=True)
    cat = Column(Text, nullable=False)
    price = Column(BigInteger, nullable=True)
    name = Column(Text, nullable=False)
    descr = Column(Text, nullable=True)

class Dialogs(Base):
    __tablename__ = 'dialogs'
    id = Column(Integer, primary_key=True, autoincrement=True)
    id_order = Column(Integer)
    tg_id_client = Column(BigInteger, nullable=True)
    tg_id_executor = Column(BigInteger, nullable=True)
    message = Column(Text, default='')
    data_time = Column(DateTime, default=datetime.datetime.utcnow())

Base.metadata.create_all(engine)