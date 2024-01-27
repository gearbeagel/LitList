from utils import *
from db_models import *


def process_interview_data(message, selected_list):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Функція під розробкою, ссорян!")