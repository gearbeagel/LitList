from utils import *
from db_models import *


def process_doc_data(message, selected_list):
    chat_id = message.chat.id
    doc_title = message.text
    list_id = selected_list.list_id

    msg = bot.send_message(chat_id, "Із якої збірки документ?")
    bot.register_next_step_handler(msg, lambda m: process_doc_source(m, selected_list, doc_title))


def process_doc_source(message, selected_list, doc_title):
    chat_id = message.chat.id
    doc_source = message.text
    list_id = selected_list.list_id

    msg = bot.send_message(chat_id, "Хто створив документ?")
    bot.register_next_step_handler(msg, lambda m: process_author(m, selected_list, list_id, doc_title, doc_source))


def process_author(message, selected_list, list_id, doc_title, doc_source):
    chat_id = message.chat.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_doc_data(m, selected_list))
    doc_author = message.text
    msg = bot.send_message(chat_id, "Коли він був оприлюднений?")
    bot.register_next_step_handler(msg,
                                   lambda m: process_year(m, selected_list, list_id, doc_title, doc_source, doc_author))


def process_year(message, selected_list, list_id, doc_title, doc_source, doc_author):
    chat_id = message.chat.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_author(m, selected_list, list_id, doc_title))
    doc_year = datetime.strptime(message.text, '%Y').date()
    msg = bot.send_message(chat_id, "Яке видавництво його оприлюднило?")
    bot.register_next_step_handler(msg, lambda m: process_publisher(m, selected_list, list_id, doc_title, doc_source,
                                                                    doc_author,
                                                                    doc_year))


def process_publisher(message, selected_list, list_id, doc_title, doc_source, doc_author, doc_year):
    chat_id = message.chat.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_year(m, selected_list, list_id, doc_title, doc_source,
                                                              doc_author))
    doc_publisher = message.text
    msg = bot.send_message(chat_id, "В якому місті знаходиться видавництво?")
    bot.register_next_step_handler(msg,
                                   lambda m: process_publisher_city(m, selected_list, list_id, doc_title, doc_source,
                                                                    doc_author, doc_year, doc_publisher))


def process_publisher_city(message, selected_list, list_id, doc_title, doc_source, doc_author, doc_year, doc_publisher):
    chat_id = message.chat.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_publisher(m, selected_list, list_id,
                                                                   doc_title, doc_source, doc_author, doc_year))
    doc_publisher_city = message.text
    msg = bot.send_message(chat_id,
                           "На якій сторінці знаходиться те, на що ви створюєте посилання? "
                           "(якщо вона відсутня, напишіть слово 'відсутня')")
    bot.register_next_step_handler(msg, lambda m: process_doc_refs(m, selected_list, list_id, doc_title, doc_source,
                                                                   doc_author, doc_year, doc_publisher,
                                                                   doc_publisher_city))


def process_doc_refs(message, selected_list, list_id, doc_title, doc_source, doc_author, doc_year, doc_publisher,
                     doc_publisher_city):
    doc_refs = ""
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_publisher_city(m, selected_list, list_id, doc_title,
                                                                        doc_source,
                                                                        doc_author, doc_year, doc_publisher))
        return

    if message.text.lower() == "відсутня":
        doc_refs = ""
    elif message.text.isdigit():
        doc_refs = int(message.text)
    else:
        bot.send_message(message.chat.id, "Щось пішло не так... Спробуйте ще раз.")
        bot.register_next_step_handler(message,
                                       lambda m: process_publisher_city(m, selected_list, list_id, doc_title,
                                                                        doc_source,
                                                                        doc_author, doc_year, doc_publisher))
    chat_id = message.chat.id
    save_doc(list_id, doc_title, doc_source, doc_author, doc_year, doc_publisher, doc_publisher_city, doc_refs)
    bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")


def save_doc(list_id, doc_title, doc_source, doc_author, doc_year, doc_publisher, doc_publisher_city, doc_refs):
    new_doc = Doc(
        doc_title=doc_title,
        doc_source=doc_source,
        doc_author=doc_author,
        publisher_name=doc_publisher,
        publisher_city=doc_publisher_city,
        publisher_year=doc_year.year,
        refs=doc_refs,
        list_id=list_id
    )
    session.add(new_doc)
    session.commit()

    doc_id = new_doc.doc_id
    doc_entry = Entry(
        entry_type='doc',
        from_doc_resource_id=doc_id,
        list_id=list_id
    )
    session.add(doc_entry)
    session.commit()