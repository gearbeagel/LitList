import calendar

from utils import *

from add_archive import process_archive_data
from add_article import process_article_data
from add_doc import process_doc_data
from add_ebook import process_ebook_data
from add_interview import process_interview_data
from delete_stuff import delete_list, process_selected_list_deletion
from add_books import process_book_data


@bot.message_handler(commands=['start'])
def start(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if not user:
        user = User(
            username=message.from_user.username,
            first_name=message.from_user.first_name,
            last_name=message.from_user.last_name,
            chat_id=chat_id
        )
        session.add(user)
        session.commit()

        bot.send_message(chat_id, f"Привіт! Розкажу про функціонал бота:\n"
                                  "/create_list - створити список літератури.\n"
                                  "/create_entry - створити елемент у списку літератури.\n"
                                  "/show_lists - передивитися свої списки літератури.\n"
                                  "/delete_list - видалити список.\n"
                                  "/delete_entry - видалити джерело у списку літератури.")
    else:
        bot.send_message(chat_id, "Знову привіт! Вибирай, що хочеш зробити:\n"
                                  "/create_list - створити список літератури.\n"
                                  "/create_entry - створити елемент у списку літератури.\n"
                                  "/show_lists - передивитися свої списки літератури.\n"
                                  "/delete_list - видалити список.\n"
                                  "/delete_entry - видалити джерело у списку літератури.")


"""СТВОРИТИ СПИСОК"""


@bot.message_handler(commands=['create_list'])
def create_list(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if not user:
        bot.send_message(chat_id, "Ти не зареєстрований. Клацни /start аби зарєструватися.")
        return
    user_lists = session.query(List).filter_by(list_owner=user.user_id).all()

    bot.send_message(chat_id, "Напиши назву свого списку літератури:")
    bot.register_next_step_handler(message, lambda m: process_list_name(m, user, user_lists))


def process_list_name(message, user, user_lists):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва списку має бути текстом. Спробуй ще раз.')
        bot.register_next_step_handler(message, lambda m: process_list_name(m, user, user_lists))
        return

    list_name = message.text.strip()
    if any(existing_list.list_name == list_name for existing_list in user_lists):
        bot.send_message(message.chat.id, 'Список з такою назвою вже існує. Спробуйте іншу назву.')
        return

    new_list = List(list_name=list_name, list_owner=user.user_id)
    session.add(new_list)
    session.commit()

    bot.send_message(message.chat.id, f"Створено новий список літератури: '{list_name}'!")


"""СТВОРИТИ ДЖЕРЕЛО"""


@bot.message_handler(commands=['create_entry'])
def create_entry(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if not user:
        bot.send_message(chat_id, "Ти не зареєстрований. Клацни /start аби зарєструватися.")
        return
    user_lists = session.query(List).filter_by(list_owner=user.user_id).all()
    if not user_lists:
        bot.send_message(chat_id, "У вас немає створених списків. Створіть список за допомогою /create_list.")
        return
    list_markup = types.ReplyKeyboardMarkup(row_width=1)
    for user_list in user_lists:
        list_markup.add(types.KeyboardButton(user_list.list_name))
    msg = bot.send_message(chat_id, "Вибери список:", reply_markup=list_markup)
    bot.register_next_step_handler(msg, process_list_choice)
    list_markup = types.ReplyKeyboardRemove(selective=False)


def process_list_choice(message):
    chat_id = message.chat.id
    list_name = message.text

    user = session.query(User).filter_by(chat_id=chat_id).first()
    selected_list = session.query(List).filter_by(list_name=list_name, list_owner=user.user_id).first()

    if not selected_list:
        bot.send_message(chat_id, "Помилка при виборі списку. Спробуй ще раз.")
        bot.register_next_step_handler(message, create_entry)
        return

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    book = types.KeyboardButton("Книга")
    ebook = types.KeyboardButton("Електронна книга")
    doc = types.KeyboardButton("Документ")
    archive = types.KeyboardButton("Архів")
    article = types.KeyboardButton("Стаття")
    interview = types.KeyboardButton("Інтерв'ю")
    keyboard.add(book, ebook, doc, archive, article, interview)
    msg = bot.send_message(chat_id, "Файно! Який це має бути вид джерела?", reply_markup=keyboard)
    bot.register_next_step_handler(msg, lambda m: process_entry_type(m, selected_list))


def process_entry_type(message, selected_list):
    chat_id = message.chat.id

    try:
        source_type = message.text.strip()
    except KeyError:
        bot.send_message(chat_id, "Невідомий тип. Спробуйте ще раз.")
        bot.register_next_step_handler(message, lambda m: process_entry_type(m, selected_list))
        return

    if source_type == "Книга":
        bot.send_message(chat_id, "Ви обрали книгу. Введіть назву книги.")
        bot.register_next_step_handler(message, lambda m: process_book_data(m, selected_list))
    elif source_type == "Електронна книга":
        bot.send_message(chat_id, "Ви обрали електронну книгу. Введіть назву електронної книги.")
        bot.register_next_step_handler(message, lambda m: process_ebook_data(m, selected_list))
    elif source_type == "Документ":
        bot.send_message(chat_id, "Ви обрали документ. Введіть назву документу.")
        bot.register_next_step_handler(message, lambda m: process_doc_data(m, selected_list))
    elif source_type == "Архів":
        bot.send_message(chat_id, "Ви обрали архів. Введіть дані про архів.")
        bot.register_next_step_handler(message, lambda m: process_archive_data(m, selected_list))
    elif source_type == "Стаття":
        bot.send_message(chat_id, "Ви обрали статтю. Введіть дані про статтю.")
        bot.register_next_step_handler(message, lambda m: process_article_data(m, selected_list))
    elif source_type == "Інтерв'ю":
        bot.send_message(chat_id, "Ви обрали інтерв'ю. Введіть ім'я людини, з якою було проведено інтерв'ю.")
        bot.register_next_step_handler(message, lambda m: process_interview_data(m, selected_list))
    else:
        bot.send_message(chat_id, "Невідомий тип. Спробуйте ще раз.")
        bot.register_next_step_handler(message, lambda m: process_entry_type(m, selected_list))


"""ПЕРЕГЛЯД ІНФОРМАЦІЇ"""


@bot.message_handler(commands=['show_lists'])
def show_lists(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        lists = user.lists
        if lists:
            for user_list in lists:
                list_content = f"Назва: {user_list.list_name}\n\n"
                sources = []
                entries = user_list.entries
                if entries:
                    for idx, entry in enumerate(entries, start=1):
                        if entry.entry_type == 'book':
                            book = session.query(Book).filter_by(book_id=entry.from_book_resource_id).first()
                            if book:
                                sources.append(format_book(book))
                        elif entry.entry_type == 'doc':
                            doc = session.query(Doc).filter_by(doc_id=entry.from_doc_resource_id).first()
                            if doc:
                                sources.append(format_doc(doc))
                        elif entry.entry_type == 'archive':
                            archive = session.query(Archive).filter_by(arch_id=entry.from_arch_resource_id).first()
                            if archive:
                                sources.append(format_archive(archive))
                        elif entry.entry_type == 'article':
                            article = session.query(Article).filter_by(article_id=entry.from_artcl_resource_id).first()
                            if article:
                                sources.append(format_article(article))
                        elif entry.entry_type == 'interview':
                            interview = session.query(Interview).filter_by(
                                interview_id=entry.from_inter_resource_id).first()
                            if interview:
                                sources.append(format_interview(interview))
                    if sources:
                        list_content += "".join([f"{idx}. {source}" for idx, source in enumerate(sources, start=1)])
                    else:
                        list_content += "Список порожній."
                    bot.send_message(chat_id, list_content, parse_mode='HTML', disable_web_page_preview=True)
        else:
            bot.send_message(chat_id, "У тебе ще немає списків. Використай /create_list, аби створити список.")
    else:
        bot.send_message(chat_id, "Ти не зареєстрований. Клацни /start аби зареєструватися.")


def format_book(book):
    if book.is_ebook:
        if not book.authors2_surname and not book.authors2_name:
            return (
                f"{book.authors1_surname}, {book.authors1_name}, <i>{book.book_title}</i>. "
                f"{book.publisher_city}: {book.publisher_name}, {book.publisher_year}. "
                f"опублікована {book.date_of_pub.day} {ukrainian_months[book.date_of_pub.month]}, {book.date_of_pub.year}, {book.link}\n"
            )
        else:
            return (
                f"{book.authors1_surname}, {book.authors1_name} і {book.authors2_surname}, {book.authors2_name} <i>{book.book_title}</i>. "
                f"{book.publisher_city}: {book.publisher_name}, {book.publisher_year}. "
                f"опублікована {book.date_of_pub.day} {ukrainian_months[book.date_of_pub.month]}, {book.date_of_pub.year} {book.link}\n"
            )
    else:
        if not book.authors2_surname and not book.authors2_name:
            return (
                f"{book.authors1_surname}, {book.authors1_name}, <i>{book.book_title}</i>. "
                f"({book.publisher_city}: {book.publisher_name}, {book.publisher_year})"
                f"{", " + book.refs if book.refs else " "}\n"
            )
        else:
            return (
                f"{book.authors1_surname}, {book.authors1_name} і {book.authors2_surname}, {book.authors2_name} <i>{book.book_title}</i>. "
                f"({book.publisher_city}: {book.publisher_name}, {book.publisher_year})"
                f"{", " + book.refs if book.refs else " "}\n"
            )


def format_doc(doc):
    return (f"{doc.doc_title}. <i>{doc.doc_source}</i>, упоряд. і авт. комент. {doc.doc_author}. "
            f"({doc.publisher_city}: {doc.publisher_name}, {doc.publisher_year}){", " + doc.refs if doc.refs else " "}\n")


def format_archive(archive):
    return f"{archive.arch_title}. {archive.arch_location}\n"


def format_article(article):
    return f"{article.article_title}. {article.article_link}\n"


def format_interview(interview):
    return (f"{interview.getting_interviewed} ({interview.gi_year_of_birth.year} р. н.), провів(ла) інтерв'ю {interview.interviewing}, "
            f"{interview.location_of_interview}, {interview.interview_date.day} {ukrainian_months[interview.interview_date.month]}, "
            f"{interview.interview_date.year}\n")


"""ВИДАЛЕННЯ"""


@bot.message_handler(commands=['delete_list'])
def start_delete_list(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()
    user_lists = user.lists
    if not user:
        bot.send_message(chat_id, "Користувача не знайдено. Почніть спочатку.")
        return
    list_markup = types.ReplyKeyboardMarkup(row_width=1)
    for user_list in user_lists:
        list_markup.add(types.KeyboardButton(user_list.list_name))
    msg = bot.send_message(chat_id, "Вибери список, який хочеш видалити:", reply_markup=list_markup)
    list_markup = types.ReplyKeyboardRemove(selective=False)
    bot.register_next_step_handler(msg, delete_list, user)


@bot.message_handler(commands=['delete_entry'])
def start_delete_entry(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()
    user_lists = user.lists
    if not user:
        bot.send_message(chat_id, "Користувача не знайдено. Почніть спочатку.")
        return
    list_markup = types.ReplyKeyboardMarkup(row_width=1)
    for user_list in user_lists:
        list_markup.add(types.KeyboardButton(user_list.list_name))
    msg = bot.send_message(chat_id, "Вибери список, з якого хочеш видалити джерело:", reply_markup=list_markup)
    list_markup = types.ReplyKeyboardRemove(selective=False)
    bot.register_next_step_handler(msg, process_selected_list_deletion, user)

"""MISC"""


@bot.message_handler(commands=['back'])
def back_to_start(message):
    bot.clear_step_handler(message.chat.id)
    bot.send_message(message.chat.id, "Ти повернувся в головне меню! "
                                      "Якщо хочеш продовжити роботу, вибирай з перелічених функцій.",
                     reply_markup=types.ReplyKeyboardRemove())


bot.polling(none_stop=True)
