from utils import *
from db_models import *

article_data = {}


def process_article_data(message, selected_list):
    chat_id = message.chat.id
    article_data['article_title'] = message.text

    msg = bot.send_message(chat_id, "Як звати автора статті? (Якщо автора нема, напишіть слово 'Немає')")
    bot.register_next_step_handler(msg, lambda m: process_article_author_name(m, selected_list))


def process_article_author_name(message, selected_list):
    chat_id = message.chat.id
    article_data['article_author_name'] = message.text
    if article_data['article_author_name'] == "Немає" or article_data['article_author_name'] == "немає":
        article_data['article_author_surname'] = ''
        msg = bot.send_message(chat_id, "Коли була опублікована стаття?")
        bot.register_next_step_handler(msg, lambda m: process_article_dop(m, selected_list))
    else:
        msg = bot.send_message(chat_id, "Яке прізвище у автора статті?")
        bot.register_next_step_handler(msg, lambda m: process_article_author_surname(m, selected_list))


def process_article_author_surname(message, selected_list):
    chat_id = message.chat.id
    article_data['article_author_surname'] = message.text

    msg = bot.send_message(chat_id, "Коли була опублікована стаття?")
    bot.register_next_step_handler(msg, lambda m: process_article_dop(m, selected_list))


def process_article_dop(message, selected_list):
    chat_id = message.chat.id
    article_data['article_dop'] = datetime.strptime(message.text, "%d-%m-%Y").date()

    keyboard = types.ReplyKeyboardMarkup(row_width=1, resize_keyboard=True)
    newspaper_article = types.KeyboardButton("Стаття із газети")
    internet_publication = types.KeyboardButton("Публікація в інтернеті")
    magazine_article = types.KeyboardButton("Стаття із журналу")
    keyboard.add(newspaper_article, internet_publication, magazine_article)
    msg = bot.send_message(chat_id, "Якого виду ця стаття?", reply_markup=keyboard)
    bot.register_next_step_handler(msg, lambda m: process_article_type(m, selected_list))


def process_article_type(message, selected_list):
    chat_id = message.chat.id
    article_type = message.text
    article_data["article_type"] = article_type

    msg = bot.send_message(chat_id, f"Із {'якого журналу' if article_type == 'Стаття із журналу'
    else 'якої газети' if article_type == 'Стаття із газети'
    else 'якого джерела'} дана стаття?")
    bot.register_next_step_handler(msg, lambda m: process_article_source(m, selected_list))


def process_article_source(message, selected_list):
    chat_id = message.chat.id
    article_data['article_source'] = message.text

    if article_data['article_type'] == 'Стаття із журналу':
        msg = bot.send_message(chat_id, "Який це номер журналу?")
        bot.register_next_step_handler(msg, lambda m: process_magazine_number(m, selected_list))
    elif article_data['article_type'] == "Публікація в інтернеті":
        msg = bot.send_message(chat_id, "Коли було отримано доступ до статті?")
        bot.register_next_step_handler(msg, lambda m: process_access_date(m, selected_list))
    else:
        save_newspaper_article(article_data, selected_list)
        bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")


def process_magazine_number(message, selected_list):
    chat_id = message.chat.id
    article_data['magazine_number'] = message.text

    msg = bot.send_message(chat_id, "На якій сторінці знаходиться те, на що ви посилаєтеся в джерелі?")
    bot.register_next_step_handler(msg, lambda m: process_article_page(m, selected_list))


def process_article_page(message, selected_list):
    chat_id = message.chat.id
    article_data['article_page'] = message.text

    save_magazine_article(article_data, selected_list)
    bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")


def process_access_date(message, selected_list):
    chat_id = message.chat.id
    article_data['access_date'] = datetime.strptime(message.text, "%d-%m-%Y").date()

    msg = bot.send_message(chat_id, "Надішли посилання, на якому знаходиться стаття.")
    bot.register_next_step_handler(msg, lambda m: process_article_link(m, selected_list))


def process_article_link(message, selected_list):
    chat_id = message.chat.id
    article_link = message.text

    if "http" not in article_link:
        bot.send_message(chat_id, "Ви не надіслали посилання. Перевірте ще раз.")
    else:
        article_data['article_link'] = article_link
        save_internet_article(article_data, selected_list)
        bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")


def save_newspaper_article(article_data, selected_list):
    new_newsp_art = Article(
        article_type=article_data.get('article_type'),
        article_title=article_data.get('article_title'),
        article_author_name=article_data.get('article_author_name'),
        article_author_surname=article_data.get('article_author_surname'),
        article_dop=article_data.get('article_dop'),
        source_title=article_data.get('article_source'),
        list_id=selected_list.list_id
    )
    session.add(new_newsp_art)
    session.commit()

    newsp_art_id = new_newsp_art.article_id
    newsp_art_entry = Entry(
        entry_type="article",
        from_artcl_resource_id=newsp_art_id,
        mentioning='first',
        list_id=selected_list.list_id
    )
    session.add(newsp_art_entry)
    session.commit()


def save_magazine_article(article_data, selected_list):
    new_magazine_art = Article(
        article_type=article_data.get('article_type'),
        article_title=article_data.get('article_title'),
        article_author_name=article_data.get('article_author_name'),
        article_author_surname=article_data.get('article_author_surname'),
        article_dop=article_data.get('article_dop'),
        source_title=article_data.get('article_source'),
        magazine_info=article_data.get('magazine_number'),
        article_page=article_data.get('article_page'),
        list_id=selected_list.list_id
    )
    session.add(new_magazine_art)
    session.commit()

    magazine_art_id = new_magazine_art.article_id
    magazine_art_entry = Entry(
        entry_type="article",
        from_artcl_resource_id=magazine_art_id,
        mentioning='first',
        list_id=selected_list.list_id
    )
    session.add(magazine_art_entry)
    session.commit()


def save_internet_article(article_data, selected_list):
    new_article = Article(
        article_type=article_data.get('article_type'),
        article_title=article_data.get('article_title'),
        article_author_name=article_data.get('article_author_name'),
        article_author_surname=article_data.get('article_author_surname'),
        article_dop=article_data.get('article_dop'),
        source_title=article_data.get('article_source'),
        article_link=article_data.get('article_link'),
        access_date=article_data.get('access_date'),
        list_id=selected_list.list_id
    )
    session.add()
    session.commit()

    new_article_id = new_article.article_id
    new_article_entry = Entry(
        entry_type="article",
        from_artcl_resource_id=new_article_id,
        mentioning='first',
        list_id=selected_list.list_id
    )
    session.add(new_article_entry)
    session.commit()
