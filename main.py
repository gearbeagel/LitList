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
        bot.send_message(chat_id, "Ви обрали електронну книгу. Введіть дані про електронну книгу.")
        bot.register_next_step_handler(message, lambda m: process_ebook_data(m, selected_list))
    elif source_type == "Документ":
        bot.send_message(chat_id, "Ви обрали документ. Введіть дані про документ.")
        bot.register_next_step_handler(message, lambda m: process_doc_data(m, selected_list))
    elif source_type == "Архів":
        bot.send_message(chat_id, "Ви обрали архів. Введіть дані про архів.")
        bot.register_next_step_handler(message, lambda m: process_archive_data(m, selected_list))
    elif source_type == "Стаття":
        bot.send_message(chat_id, "Ви обрали статтю. Введіть дані про статтю.")
        bot.register_next_step_handler(message, lambda m: process_article_data(m, selected_list))
    elif source_type == "Інтерв'ю":
        bot.send_message(chat_id, "Ви обрали інтерв'ю. Введіть дані про інтерв'ю.")
        bot.register_next_step_handler(message, lambda m: process_interview_data(m, selected_list))
    else:
        bot.send_message(chat_id, "Невідомий тип. Спробуйте ще раз.")
        bot.register_next_step_handler(message, lambda m: process_entry_type(m, selected_list))


"""СТВОРИТИ КНИГУ"""


def process_book_data(message, selected_list):
    chat_id = message.chat.id
    list_id = selected_list.list_id
    book_name = message.text.strip()

    msg = bot.send_message(chat_id, "Скільки авторів у книзі?")
    bot.register_next_step_handler(msg, lambda m: process_author_count(m, list_id, selected_list, book_name))


def process_author_count(message, list_id, selected_list, book_name):
    chat_id = message.chat.id
    try:
        author_count = int(message.text)
        if author_count < 1:
            raise ValueError("Кількість авторів має бути 1 або більше.")
    except ValueError:
        bot.send_message(chat_id, "Невірний формат. Введіть ціле число більше 0.")
        bot.register_next_step_handler(message, lambda m: process_book_data(m, selected_list))
        return

    process_author_data(message, list_id, book_name, author_count)


def process_author_data(message, list_id, book_name, author_count):
    chat_id = message.chat.id

    if author_count == 1 or author_count == 2:
        msg = bot.send_message(chat_id,
                               f"Як звати {'першого ' if author_count == 2 else ''}автора? {
                               "якщо було вказно кількість авторів більше, ніж два,"
                               "введіть прізвище першого автора)" if author_count > 2 else ''}")
        bot.register_next_step_handler(msg, lambda m: process_author_name(m, list_id, book_name, author_count))
    else:
        msg = bot.send_message(chat_id, "Як звати першого автора?")
        bot.register_next_step_handler(msg, lambda m: process_author_name(m, list_id, book_name, author_count))


def process_author_name(message, list_id, book_name, author_count):
    chat_id = message.chat.id
    author1_name = message.text.strip()

    if author_count == 2:
        user_data_dict[chat_id] = {"author1_name": author1_name}

        msg = bot.send_message(chat_id, "Яке у першого автора прізвище?")
        bot.register_next_step_handler(msg,
                                       lambda m, author1=author1_name: process_author_surname(m, list_id, book_name,
                                                                                              author_count, author1,
                                                                                              author2_name=''))

    else:
        user_data_dict[chat_id] = {"author1_name": author1_name}
        author2_name = ""
        msg = bot.send_message(chat_id, "Яке автора прізвище? (якщо було вказно кількість авторів більше, ніж два, "
                                        "введіть прізвище першого автора)")
        bot.register_next_step_handler(msg, lambda m, author1=author1_name, author2=author2_name:
        process_author_surname(m, list_id, book_name, author_count, author1, author2))


def process_author_surname(message, list_id, book_name, author_count, author1_name, author2_name):
    chat_id = message.chat.id
    author1_surname = message.text.strip()

    if author_count == 2:
        user_data_dict[chat_id] = {"author1_surname": author1_surname}
        msg = bot.send_message(chat_id, "Як звати другого автора?")
        bot.register_next_step_handler(msg, lambda m: process_second_author_name(m, list_id, book_name, author1_name,
                                                                                 author1_surname))
    else:
        user_data_dict[chat_id] = {"author1_surname": author1_surname}
        author2_surname = ""
        msg = bot.send_message(chat_id, "Яке видавництво?")
        bot.register_next_step_handler(msg,
                                       lambda m: process_publisher(m, list_id, book_name, author1_name, author1_surname,
                                                                   author2_name, author2_surname))


def process_second_author_name(message, list_id, book_name, author1_name, author1_surname):
    chat_id = message.chat.id
    author2_name = message.text.strip()

    user_data_dict[chat_id] = {"author2_name": author2_name}

    msg = bot.send_message(chat_id, "Яке у другого автора прізвище?")
    bot.register_next_step_handler(msg, lambda m: process_second_author_surname(m, list_id, book_name, author1_name,
                                                                                author1_surname, author2_name))


def process_second_author_surname(message, list_id, book_name, author1_name, author1_surname, author2_name):
    chat_id = message.chat.id
    author2_surname = message.text.strip()

    user_data_dict[chat_id] = {"author2_surname": author2_surname}
    msg = bot.send_message(chat_id, "Яке видавництво?")
    bot.register_next_step_handler(msg,
                                   lambda m: process_publisher(m, list_id, book_name, author1_name, author1_surname,
                                                               author2_name, author2_surname))


def process_publisher(message, list_id, book_name, author1_name, author1_surname, author2_name, author2_surname):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_author_surname(m, list_id, book_name, author1_name,
                                                                        author1_surname,
                                                                        author2_name))
        return
    publisher = message.text
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Яке місто видавництва?")
    bot.register_next_step_handler(msg, lambda m: process_publisher_city(m, list_id, book_name, author1_name,
                                                                         author1_surname, author2_name, author2_surname,
                                                                         publisher))


def process_publisher_city(message, list_id, book_name, author1_name, author1_surname, author2_name, author2_surname,
                           publisher):
    chat_id = message.chat.id
    publisher_city = message.text
    msg = bot.send_message(chat_id, "Який рік публікації?")
    bot.register_next_step_handler(msg, lambda m: process_year(m, list_id, book_name, author1_name, author1_surname,
                                                               author2_name, author2_surname,
                                                               publisher, publisher_city))


def process_year(message, list_id, book_name, author1_name, author1_surname, author2_name, author2_surname,
                 publisher_city, publisher):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_publisher_city(m, list_id, book_name,
                                                                        author1_name, author1_surname, author2_name,
                                                                        author2_surname, publisher))
        return
    chat_id = message.chat.id
    year_input = message.text
    try:
        year = datetime.strptime(year_input, '%Y').date()
    except ValueError:
        bot.send_message(chat_id, "Неправильний формат року. Введіть рік у форматі YYYY (наприклад, 2012).")
        bot.register_next_step_handler(message,
                                       lambda m: process_year(m, list_id, book_name, author1_name, author1_surname,
                                                              author2_name, author2_surname,
                                                              publisher_city, publisher))
        return
    msg = bot.send_message(chat_id, "На якій сторінці знаходиться те, на що ви створюєте посилання?")
    bot.register_next_step_handler(msg, lambda m: process_refs(m, list_id, book_name, author1_name, author1_surname,
                                                               author2_name, author2_surname,
                                                               publisher, publisher_city, year))


def process_refs(message, list_id, book_name, author1_name, author1_surname, author2_name, author2_surname, publisher,
                 publisher_city, year):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_publisher_city(m, list_id, book_name,
                                                                        author1_name, author1_surname, author2_name,
                                                                        author2_surname, publisher))
        return
    refs = message.text
    chat_id = message.chat.id
    selected_list = session.query(List).filter_by(list_id=list_id).first()
    save_book(book_name, author1_name, author1_surname, author2_name, author2_surname, publisher, publisher_city, year,
              refs,
              selected_list)
    bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")


def save_book(book_name, author1_name, author1_surname, author2_name, author2_surname, publisher, publisher_city, year,
              refs,
              selected_list):
    new_book = Book(
        book_title=book_name,
        is_ebook=False,
        authors1_name=author1_name,
        authors1_surname=author1_surname,
        authors2_name=author2_name,
        authors2_surname=author2_surname,
        publisher_name=publisher,
        publisher_city=publisher_city,
        publisher_year=year,
        refs=refs,
        link='',
        list_id=selected_list.list_id
    )
    session.add(new_book)
    session.commit()

    book_id = new_book.book_id
    new_entry = Entry(
        entry_type='book',
        from_book_resource_id=book_id,
        list_id=selected_list.list_id
    )
    session.add(new_entry)
    session.commit()


"""СТВОРЕННЯ ЕЛЕКТРОННОЇ КНИГИ"""


def process_ebook_data(message, selected_list):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Функція під розробкою, ссорян!")


"""СТВОРЕННЯ ДОКУМЕНТУ"""


def process_doc_data(message, selected_list):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Функція під розробкою, ссорян!")


"""СТВОРЕННЯ АРХІВУ"""


def process_archive_data(message, selected_list):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Функція під розробкою, ссорян!")


"""СТВОРЕННЯ СТАТТІ"""


def process_article_data(message, selected_list):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Функція під розробкою, ссорян!")


"""СТВОРЕННЯ ІНТВЕРВ'Ю"""


def process_interview_data(message, selected_list):
    chat_id = message.chat.id
    bot.send_message(chat_id, "Функція під розробкою, ссорян!")


"""ПЕРЕГЛЯД ІНФОРМАЦІЇ"""


@bot.message_handler(commands=['show_lists'])
def show_lists(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()
    if user:
        lists = user.lists
        if lists:
            for user_list in lists:
                list_content = f"\nНазва: {user_list.list_name}\n"
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
                        list_content += "\n".join([f"{idx}. {source}" for idx, source in enumerate(sources, start=1)])
                    else:
                        list_content += "Список порожній."
                    bot.send_message(chat_id, list_content, parse_mode='HTML')
        else:
            bot.send_message(chat_id, "У тебе ще немає списків. Використай /create_list, аби створити список.")
    else:
        bot.send_message(chat_id, "Ти не зареєстрований. Клацни /start аби зареєструватися.")


def format_book(book):
    if book.is_ebook:
        if not book.authors2_surname and not book.authors2_name:
            return (
                f"{book.authors1_surname}, {book.authors1_name}, <i>{book.book_title}</i>. "
                f"({book.publisher_city}: {book.publisher_name}, {book.publisher_year}), "
                f"опублікована {book.date_of_pub}, {book.link}\n"
            )
        else:
            return (
                f"{book.authors1_surname}, {book.authors1_name} and {book.authors2_surname}, {book.authors2_name} <i>{book.book_title}</i>. "
                f"({book.publisher_city}: {book.publisher_name}, {book.publisher_year}), "
                f"опублікована {book.date_of_pub}, {book.link}\n"
            )
    else:
        if not book.authors2_surname and not book.authors2_name:
            return (
                f"{book.authors1_surname}, {book.authors1_name}, <i>{book.book_title}</i>. "
                f"({book.publisher_city}: {book.publisher_name}, {book.publisher_year}), {book.refs}\n"
            )
        else:
            return (
                f"{book.authors1_surname}, {book.authors1_name} and {book.authors2_surname}, {book.authors2_name} <i>{book.book_title}</i>. "
                f"({book.publisher_city}: {book.publisher_name}, {book.publisher_year}), {book.refs}\n"
            )


def format_doc(doc):
    return f"{doc.doc_title}. {doc.publisher_city}: {doc.publisher_name}, {doc.publisher_year}\n"


def format_archive(archive):
    return f"{archive.arch_title}. {archive.arch_location}\n"


def format_article(article):
    return f"{article.article_title}. {article.article_link}\n"


def format_interview(interview):
    return f"{interview.getting_interviewed}. {interview.location_of_interview}\n"


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


def delete_list(message, user):
    chat_id = message.chat.id
    list_name = message.text.strip()
    user_lists = user.lists
    selected_list = next((lst for lst in user_lists if lst.list_name == list_name), None)
    if not selected_list:
        bot.send_message(chat_id, "Список з такою назвою не існує. Спробуйте ще раз.")
        bot.register_next_step_handler(message, lambda m: delete_list(m, user))
        return
    for entry in selected_list.entries:
        if entry.entry_type == 'book':
            book = session.query(Book).filter_by(book_id=entry.from_book_resource_id).first()
            if book:
                session.delete(book)
        elif entry.entry_type == 'doc':
            doc = session.query(Doc).filter_by(doc_id=entry.from_doc_resource_id).first()
            if doc:
                session.delete(doc)
        elif entry.entry_type == 'archive':
            archive = session.query(Archive).filter_by(arch_id=entry.from_arch_resource_id).first()
            if archive:
                session.delete(archive)
        elif entry.entry_type == 'article':
            article = session.query(Article).filter_by(article_id=entry.from_artcl_resource_id).first()
            if article:
                session.delete(article)
        elif entry.entry_type == 'interview':
            interview = session.query(Interview).filter_by(interview_id=entry.from_inter_resource_id).first()
            if interview:
                session.delete(interview)

    session.delete(selected_list)
    session.commit()
    bot.send_message(chat_id, f"Список '{list_name}' був успішно видалений, разом із усіма джерелами.")


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
    bot.register_next_step_handler(msg, delete_list, user)


def process_selected_list_deletion(message, user):
    chat_id = message.chat.id
    user_lists = user.lists
    list_name_to_utilize = message.text.strip()
    selected_list = next((lst for lst in user_lists if lst.list_name == list_name_to_utilize), None)
    if not selected_list:
        bot.send_message(chat_id, "Список з такою назвою не існує. Спробуйте ще раз.")
        bot.register_next_step_handler(message, lambda m: start_delete_entry(m, user))
        return
    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    book = types.KeyboardButton("Книга")
    ebook = types.KeyboardButton("Електронна книга")
    doc = types.KeyboardButton("Документ")
    archive = types.KeyboardButton("Архів")
    article = types.KeyboardButton("Стаття")
    interview = types.KeyboardButton("Інтерв'ю")
    keyboard.add(book, ebook, doc, archive, article, interview)
    bot.send_message(chat_id, "Який це тип джерела?", reply_markup=keyboard)
    bot.register_next_step_handler(message, process_entry_type_for_deletion, selected_list, user)


def process_entry_type_for_deletion(message, selected_list, user):
    chat_id = message.chat.id
    source_type = message.text.strip()
    print("Я шось роблю")
    if source_type == 'Книга':
        bot.send_message(chat_id, "Окей, напишіть назву книги, яке хочете видалити.")
        bot.register_next_step_handler(message, delete_entry, selected_list, source_type='book')
    elif source_type == 'Електронна книга':
        bot.send_message(chat_id, "Окей, напишіть назву електронної книги, яке хочете видалити.")
        bot.register_next_step_handler(message, delete_entry, selected_list, source_type='ebook')
    elif source_type == 'Документ':
        bot.send_message(chat_id, "Окей, напишіть назву документу, яке хочете видалити.")
        bot.register_next_step_handler(message, delete_entry, selected_list, source_type='doc')
    elif source_type == 'Архів':
        bot.send_message(chat_id, "Окей, напишіть назву архіву, яке хочете видалити.")
        bot.register_next_step_handler(message, delete_entry, selected_list, source_type='archive')
    elif source_type == 'Стаття':
        bot.send_message(chat_id, "Окей, напишіть назву статті, яке хочете видалити.")
        bot.register_next_step_handler(message, delete_entry, selected_list, source_type='article')
    elif source_type == "Інтерв'ю":
        bot.send_message(chat_id, "Окей, напишіть ім'я людини, з якою ви хочете видалити інтерв'ю.")
        bot.register_next_step_handler(message, delete_entry, selected_list, source_type='interview')


def delete_entry(message, selected_list, source_type):
    chat_id = message.chat.id
    entry_name = message.text.strip()
    print("Я шось роблю")
    if source_type == 'book' or source_type == 'ebook':
        book = session.query(Book).filter_by(book_title=entry_name).first()
        if book:
            session.delete(book)
            session.commit()
            bot.send_message(chat_id, f"Книгу '{entry_name}' успішно видалено зі списку '{selected_list.list_name}'.")
        else:
            bot.send_message(chat_id, f"Книгу '{entry_name}' не знайдено у списку '{selected_list.list_name}'.")

    elif source_type == 'doc':
        doc = session.query(Doc).filter_by(doc_title=entry_name).first()
        if doc:
            session.delete(doc)
            session.commit()
            bot.send_message(chat_id, f"Документ '{entry_name}' успішно видалений.")
        else:
            bot.send_message(chat_id, f"Документ з назвою '{entry_name}' не знайдений.")

    elif source_type == 'archive':
        archive = session.query(Archive).filter_by(arch_title=entry_name).first()
        if archive:
            session.delete(archive)
            session.commit()
            bot.send_message(chat_id, f"Архів '{entry_name}' успішно видалений.")
        else:
            bot.send_message(chat_id, f"Архів з назвою '{entry_name}' не знайдений.")

    elif source_type == 'article':
        article = session.query(Article).filter_by(article_title=entry_name).first()
        if article:
            session.delete(article)
            session.commit()
            bot.send_message(chat_id, f"Стаття '{entry_name}' успішно видалена.")
        else:
            bot.send_message(chat_id, f"Стаття з назвою '{entry_name}' не знайдена.")

    elif source_type == "interview":
        interview = session.query(Interview).filter_by(getting_interviewed=entry_name).first()
        if interview:
            session.delete(interview)
            session.commit()
            bot.send_message(chat_id, f"Інтерв'ю з '{entry_name}' успішно видалено.")
        else:
            bot.send_message(chat_id, f"Інтерв'ю з '{entry_name}' не знайдено.")


"""MISC"""
@bot.message_handler(commands=['back'])
def back_to_start(message):
    bot.send_message(message.chat.id, "Ти повернувся в головне меню! Якщо хочеш продовжити роботу, вибирай з перелічених функцій.", reply_markup=types.ReplyKeyboardRemove())


bot.polling(none_stop=True)
