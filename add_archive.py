from utils import *
from db_models import *

archive_data = {}

def process_archive_data(message, selected_list):
    chat_id = message.chat.id
    archive_data['archive_title'] = message.text

    msg = bot.send_message(chat_id, "В який період були створені дані архівні матеріали?")
    bot.register_next_step_handler(msg, lambda m: process_archive_period(m, selected_list))

def process_archive_period(message, selected_list):
    chat_id = message.chat.id
    archive_data['archive_period'] = message.text

    msg = bot.send_message(chat_id, "Як називається архів, що є джерелом даних матеріалів?")
    bot.register_next_step_handler(msg, lambda m: process_archive_location(m, selected_list))

def process_archive_location(message, selected_list):
    chat_id = message.chat.id
    archive_data['archive_location'] = message.text

    msg = bot.send_message(chat_id, "Де знаходиться інформація про документ? (наприклад: ф. 36, оп. 1, спр. 51, арк. 3)")
    bot.register_next_step_handler(msg, lambda m:process_archive_found(m, selected_list))


def process_archive_found(message, selected_list):
    chat_id = message.chat.id
    archive_data['archive_placement'] = message.text

    save_archive(archive_data, selected_list)
    bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")

def save_archive(archive_data, selected_list):
    new_arch = Archive(
        arch_title=archive_data['archive_title'],
        arch_period=archive_data['archive_period'],
        arch_location=archive_data['archive_location'],
        arch_placemenr=archive_data['archive_placement'],
        list_id=selected_list.list_id
    )
    session.add(new_arch)
    session.commit()

    arch_id = new_arch.arch_id
    arch_entry = Entry(
        entry_type='archive',
        from_arch_resource_id=arch_id,
        mentioning='first',
        list_id=selected_list.list_id
    )
    session.add(arch_entry)
    session.commit()