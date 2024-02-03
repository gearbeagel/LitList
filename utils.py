from datetime import datetime

import telebot
from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from telebot import types

from db_models import *

BOT_TOKEN = "6894160738:AAG58kcR8eg9l8VCHGe6Gk5TipnQcLKt42E"
DATABASE_URL = 'mysql+mysqlconnector://root:Funnyhaha111@localhost:3306/lit_list'

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

Session = scoped_session(sessionmaker(bind=engine))
session = Session()

bot = telebot.TeleBot(BOT_TOKEN)
user_data_dict = {}

ukrainian_months = {
    1: "січня",
    2: "лютого",
    3: "березня",
    4: "квітня",
    5: "травня",
    6: "червня",
    7: "липня",
    8: "серпня",
    9: "вересня",
    10: "жовтня",
    11: "листопада",
    12: "грудня"
}