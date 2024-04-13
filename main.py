from utils import *

from add_archive import process_archive_data
from add_article import process_article_data
from add_doc import process_doc_data
from add_ebook import process_ebook_data
from add_interview import process_interview_data
from delete_stuff import delete_list, process_selected_list_deletion
from add_books import process_book_data


@bot.message_handler(commands=['start', 'back'])
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

    if not user:
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

    list_name = message.text

    if message.text == "/back":
        bot.send_message(message.chat.id, "Ти повернувся в головне меню! "
                                          "Якщо хочеш продовжити роботу, вибирай з перелічених функцій:\n"
                                          "/create_list - створити список літератури.\n"
                                          "/create_entry - створити елемент у списку літератури.\n"
                                          "/show_lists - передивитися свої списки літератури.\n"
                                          "/delete_list - видалити список.\n"
                                          "/delete_entry - видалити джерело у списку літератури.")
        return

    if any(existing_list.list_name == list_name for existing_list in user_lists):
        bot.send_message(message.chat.id, 'Список з такою назвою вже існує. Спробуйте іншу назву.')
        bot.register_next_step_handler(message, lambda m: process_list_name(m, user, user_lists))
        return

    new_list = List(
        list_name=list_name,
        list_owner=user.user_id
    )
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
    types.ReplyKeyboardRemove(selective=False)


def process_list_choice(message):
    chat_id = message.chat.id
    list_name = message.text

    user = session.query(User).filter_by(chat_id=chat_id).first()
    selected_list = session.query(List).filter_by(list_name=list_name, list_owner=user.user_id).first()

    if message.text == "/back":
        bot.send_message(message.chat.id, "Ти повернувся в головне меню! "
                                          "Якщо хочеш продовжити роботу, вибирай з перелічених функцій:\n"
                                          "/create_list - створити список літератури.\n"
                                          "/create_entry - створити елемент у списку літератури.\n"
                                          "/show_lists - передивитися свої списки літератури.\n"
                                          "/delete_list - видалити список.\n"
                                          "/delete_entry - видалити джерело у списку літератури.")
        return

    if not selected_list:
        bot.send_message(chat_id, "Помилка при виборі списку. Спробуй ще раз.")
        bot.register_next_step_handler(message, create_entry)
        return

    keyboard = types.ReplyKeyboardMarkup(row_width=2, resize_keyboard=True)
    yes = types.KeyboardButton("Так")
    no = types.KeyboardButton("Ні")
    keyboard.add(yes, no)
    msg = bot.send_message(chat_id, "Окей, чи згадується це джерело вперше?", reply_markup=keyboard)
    bot.register_next_step_handler(msg, lambda m: process_mentioning(m, selected_list))


def process_mentioning(message, selected_list):
    chat_id = message.chat.id
    mentioning = message.text

    if message.text == "/back":
        bot.send_message(message.chat.id, "Ти повернувся в головне меню! "
                                          "Якщо хочеш продовжити роботу, вибирай з перелічених функцій:\n"
                                          "/create_list - створити список літератури.\n"
                                          "/create_entry - створити елемент у списку літератури.\n"
                                          "/show_lists - передивитися свої списки літератури.\n"
                                          "/delete_list - видалити список.\n"
                                          "/delete_entry - видалити джерело у списку літератури.")
        return

    if mentioning not in ["Так", "Ні"]:
        bot.send_message(chat_id, "Будь ласка, виберіть 'Так' або 'Ні'.")
        bot.register_next_step_handler(message, lambda m: process_mentioning(m, selected_list))
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

    bot.register_next_step_handler(msg, lambda m: process_entry_type(m, selected_list, mentioning))


def process_entry_type(message, selected_list, mentioning):
    chat_id = message.chat.id

    try:
        source_type = message.text.strip()
    except KeyError:
        bot.send_message(chat_id, "Невідомий тип. Спробуйте ще раз.")
        bot.register_next_step_handler(message, lambda m: process_entry_type(m, selected_list, mentioning))
        return

    if message.text == "/back":
        bot.send_message(message.chat.id, "Ти повернувся в головне меню! "
                                          "Якщо хочеш продовжити роботу, вибирай з перелічених функцій:\n"
                                          "/create_list - створити список літератури.\n"
                                          "/create_entry - створити елемент у списку літератури.\n"
                                          "/show_lists - передивитися свої списки літератури.\n"
                                          "/delete_list - видалити список.\n"
                                          "/delete_entry - видалити джерело у списку літератури.")
        return

    if source_type == "Книга":
        bot.send_message(chat_id, "Ви обрали книгу. Введіть назву книги.")
        if mentioning == "Так":
            bot.register_next_step_handler(message, lambda m: process_book_data(m, selected_list))
        else:
            bot.register_next_step_handler(message, lambda m: process_entry_name(m, selected_list, source_type))
    elif source_type == "Електронна книга":
        bot.send_message(chat_id, "Ви обрали електронну книгу. Введіть назву електронної книги.")
        if mentioning == "Так":
            bot.register_next_step_handler(message, lambda m: process_ebook_data(m, selected_list))
        else:
            bot.register_next_step_handler(message, lambda m: process_entry_name(m, selected_list, source_type))
    elif source_type == "Документ":
        bot.send_message(chat_id, "Ви обрали документ. Введіть назву документу.")
        if mentioning == "Так":
            bot.register_next_step_handler(message, lambda m: process_doc_data(m, selected_list))
        else:
            bot.register_next_step_handler(message, lambda m: process_entry_name(m, selected_list, source_type))
    elif source_type == "Архів":
        bot.send_message(chat_id, "Ви обрали архів. Введіть назву архівного матеріалу.")
        if mentioning == "Так":
            bot.register_next_step_handler(message, lambda m: process_archive_data(m, selected_list))
        else:
            bot.register_next_step_handler(message, lambda m: process_entry_name(m, selected_list, source_type))
    elif source_type == "Стаття":
        bot.send_message(chat_id, "Ви обрали статтю. Введіть назву статті.")
        if mentioning == "Так":
            bot.register_next_step_handler(message, lambda m: process_article_data(m, selected_list))
        else:
            bot.register_next_step_handler(message, lambda m: process_entry_name(m, selected_list, source_type))
    elif source_type == "Інтерв'ю":
        bot.send_message(chat_id, "Ви обрали інтерв'ю. Введіть ім'я людини, з якою було проведено інтерв'ю.")
        if mentioning == "Так":
            bot.register_next_step_handler(message, lambda m: process_interview_data(m, selected_list))
        else:
            bot.register_next_step_handler(message, lambda m: process_entry_name(m, selected_list, source_type))
    else:
        bot.send_message(chat_id, "Невідомий тип. Спробуйте ще раз.")
        bot.register_next_step_handler(message, lambda m: process_entry_type(m, selected_list, mentioning))


def process_entry_name(message, selected_list, source_type):
    chat_id = message.chat.id
    entry_name = message.text
    if message.text == "/back":
        bot.send_message(message.chat.id, "Ти повернувся в головне меню! "
                                          "Якщо хочеш продовжити роботу, вибирай з перелічених функцій:"
                                          "/create_list - створити список літератури.\n"
                                          "/create_entry - створити елемент у списку літератури.\n"
                                          "/show_lists - передивитися свої списки літератури.\n"
                                          "/delete_list - видалити список.\n"
                                          "/delete_entry - видалити джерело у списку літератури.")
        return

    msg = bot.send_message(chat_id,
                           "Введіть номер сторінки, на якій знаходиться повторне посилання. (якщо її не існує, "
                           "напишіть слово 'відсутня')")
    bot.register_next_step_handler(msg, lambda m: process_additional_notes(m, selected_list, source_type, entry_name))


def process_additional_notes(message, selected_list, source_type, entry_name):
    chat_id = message.chat.id
    notes = message.text
    if message.text == "/back":
        bot.send_message(message.chat.id, "Ти повернувся в головне меню! "
                                          "Якщо хочеш продовжити роботу, вибирай з перелічених функцій:"
                                          "/create_list - створити список літератури.\n"
                                          "/create_entry - створити елемент у списку літератури.\n"
                                          "/show_lists - передивитися свої списки літератури.\n"
                                          "/delete_list - видалити список.\n"
                                          "/delete_entry - видалити джерело у списку літератури.")
        return

    if source_type == "Книга" or source_type == "Електронна книга":
        book = session.query(Book).filter_by(book_title=entry_name).first()
        if book:
            book_entry = Entry(
                entry_type="book",
                from_book_resource_id=book.book_id,
                mentioning='not first',
                notes=str(notes),
                list_id=selected_list.list_id
            )
            session.add(book_entry)
            session.commit()
            bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")
        else:
            bot.send_message(chat_id, "Книга не знайдена у даному списку. Спробуйте ще раз.")

    elif source_type == "Документ":
        doc = session.query(Doc).filter_by(doc_title=entry_name).first()
        if doc:
            doc_entry = Entry(
                entry_type="doc",
                from_doc_resource_id=doc.doc_id,
                mentioning='not first',
                notes=str(notes),
                list_id=selected_list.list_id
            )
            session.add(doc_entry)
            session.commit()
            bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")
        else:
            bot.send_message(chat_id, "Документ не знайдений у даному списку. Спробуйте ще раз.")

    elif source_type == "Архів":
        arch = session.query(Archive).filter_by(arch_title=entry_name).first()
        if arch:
            arch_entry = Entry(
                entry_type="archive",
                from_doc_resource_id=arch.arch_id,
                mentioning='not first',
                notes=str(notes),
                list_id=selected_list.list_id
            )
            session.add(arch_entry)
            session.commit()
            bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")
        else:
            bot.send_message(chat_id, "Архів не знайдений у даному списку. Спробуйте ще раз.")

    elif source_type == "Стаття":
        article = session.query(Article).filter_by(article_title=entry_name).first()
        if article:
            art_entry = Entry(
                entry_type="article",
                from_doc_resource_id=article.article_id,
                mentioning='not first',
                notes=str(notes),
                list_id=selected_list.list_id
            )
            session.add(art_entry)
            session.commit()
            bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")
        else:
            bot.send_message(chat_id, "Стаття не знайдена у даному списку. Спробуйте ще раз.")

    elif source_type == "Інтерв'ю":
        interview = session.query(Interview).filter_by(getting_interviewed=entry_name).first()
        if interview:
            inter_entry = Entry(
                entry_type="interview",
                from_doc_resource_id=interview.interview_id,
                mentioning='not first',
                notes=str(notes),
                list_id=selected_list.list_id
            )
            session.add(inter_entry)
            session.commit()
            bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")
        else:
            bot.send_message(chat_id, "Інтерв'ю не знайдено у даному списку. Спробуйте ще раз.")

    else:
        bot.send_message(chat_id, "Щось пішло не так...")


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
                        if entry.mentioning == 'first':
                            if entry.entry_type == 'book':
                                book = session.query(Book).filter_by(book_id=entry.from_book_resource_id).first()
                                if book:
                                    sources.append(format_book_first(book))
                            elif entry.entry_type == 'doc':
                                doc = session.query(Doc).filter_by(doc_id=entry.from_doc_resource_id).first()
                                if doc:
                                    sources.append(format_doc_first(doc))
                            elif entry.entry_type == 'archive':
                                archive = session.query(Archive).filter_by(arch_id=entry.from_arch_resource_id).first()
                                if archive:
                                    sources.append(format_archive_first(archive))
                            elif entry.entry_type == 'article':
                                article = session.query(Article).filter_by(
                                    article_id=entry.from_artcl_resource_id).first()
                                if article:
                                    sources.append(format_article_first(article))
                            elif entry.entry_type == 'interview':
                                interview = session.query(Interview).filter_by(
                                    interview_id=entry.from_inter_resource_id).first()
                                if interview:
                                    sources.append(format_interview_first(interview))
                        else:
                            if entry.entry_type == 'book':
                                book = session.query(Book).filter_by(book_id=entry.from_book_resource_id).first()
                                if book:
                                    sources.append(format_book_nonfirst(book, entry))
                            elif entry.entry_type == 'doc':
                                doc = session.query(Doc).filter_by(doc_id=entry.from_doc_resource_id).first()
                                if doc:
                                    sources.append(format_doc_nonfirst(doc, entry))
                            elif entry.entry_type == 'archive':
                                archive = session.query(Archive).filter_by(arch_id=entry.from_arch_resource_id).first()
                                if archive:
                                    sources.append(format_archive_nonfirst(archive, entry))
                            elif entry.entry_type == 'article':
                                article = session.query(Article).filter_by(
                                    article_id=entry.from_artcl_resource_id).first()
                                if article:
                                    sources.append(format_article_nonfirst(article, entry))
                            elif entry.entry_type == 'interview':
                                interview = session.query(Interview).filter_by(
                                    interview_id=entry.from_inter_resource_id).first()
                                if interview:
                                    sources.append(format_interview_nonfirst(interview))
                    if sources:
                        list_content += "".join([f"{idx}. {source}" for idx, source in enumerate(sources, start=1)])
                    else:
                        list_content += "Список порожній."
                    bot.send_message(chat_id, list_content, parse_mode='HTML', disable_web_page_preview=True)
        else:
            bot.send_message(chat_id, "У тебе ще немає списків. Використай /create_list, аби створити список.")
    else:
        bot.send_message(chat_id, "Ти не зареєстрований. Клацни /start аби зареєструватися.")


def format_book_first(book):
    if book.is_ebook:
        if not book.authors2_surname and not book.authors2_name:
            return (
                f"{book.authors1_name} {book.authors1_surname}, <i>{book.book_title}</i>. "
                f"{book.publisher_city}: {book.publisher_name}, {book.publisher_year}. "
                f"опублікована {book.date_of_pub.day} {ukrainian_months[book.date_of_pub.month]}, {book.date_of_pub.year}, {book.link}\n"
            )
        else:
            return (
                f"{book.authors1_name} {book.authors1_surname}, і {book.authors2_name} {book.authors2_surname}, <i>{book.book_title}</i>. "
                f"{book.publisher_city}: {book.publisher_name}, {book.publisher_year}. "
                f"опублікована {book.date_of_pub.day} {ukrainian_months[book.date_of_pub.month]}, {book.date_of_pub.year} {book.link}\n"
            )
    else:
        if not book.authors2_surname and not book.authors2_name:
            return (
                f"{book.authors1_name} {book.authors1_surname}, <i>{book.book_title}</i>. "
                f"({book.publisher_city}: {book.publisher_name}, {book.publisher_year})"
                f"{", " + book.refs if book.refs else " "}\n"
            )
        else:
            return (
                f"{book.authors1_name} {book.authors1_surname}, і {book.authors2_name} {book.authors2_surname}, <i>{book.book_title}</i>. "
                f"({book.publisher_city}: {book.publisher_name}, {book.publisher_year})"
                f"{", " + book.refs if book.refs else " "}\n"
            )


def format_book_nonfirst(book, entry):
    if book.is_ebook:
        return f"{book.authors1_surname}, <i>{book.book_title}</i>, {entry.notes if entry.notes != "відсутня" else ""}\n"
    else:
        if book.authors2_name and book.authors2_name:
            return f"{book.authors1_surname} і {book.authors2_surname}, <i>{book.book_title}</i>, {entry.notes if entry.notes != "відсутня" else ""}\n"
        else:
            return f"{book.authors1_surname}, <i>{book.book_title}</i>, {entry.notes if entry.notes != "відсутня" else ""}\n"


def format_doc_first(doc):
    return (
        f"{doc.doc_title}. <i>{doc.doc_source}</i>, упоряд. і авт. комент. {doc.doc_author_name} {doc.doc_author_surname}. "
        f"({doc.publisher_city}: {doc.publisher_name}, {doc.publisher_year}){", " + doc.refs if doc.refs else " "}\n")


def format_doc_nonfirst(doc, entry):
    return f"{doc.doc_title}. <i>{doc.doc_source}</i>, {entry.notes}"


def format_archive_first(archive):
    return f"{archive.arch_title}, {archive.arch_period}, <i>{archive.arch_location}</i>, {archive.arch_placement}\n"


def format_archive_nonfirst(archive, entry):
    return f"{archive.arch_title}, <i>{archive.arch_location}</i>, {entry.notes}\n"


def format_article_first(article):
    author = f"{article.article_author_name + article.article_author_surname + ', '}" if article.article_author_name != "Немає" else ""

    if article.article_type == "Стаття із газети":
        return (f"{author}'{article.article_title}', <i>{article.source_title}</i>, "
                f"{article.article_dop.day} {ukrainian_months[article.article_dop.month]}, {article.article_dop.year}.\n")
    elif article.article_type == "Стаття із журналу":
        return (f"{author}'{article.article_title}', <i>{article.source_title}</i>, "
                f"{article.magazine_info} ({article.article_dop.year}): {article.article_page}\n")
    else:
        return (f"{author}'{article.article_title}'. <i>{article.source_title}</i>, "
                f"{article.article_dop.day} {ukrainian_months[article.article_dop.month]}, {article.article_dop.year}, "
                f"доступ отримано {article.access_date.day} {ukrainian_months[article.access_date.month]}, {article.access_date.year}, "
                f"{article.article_link}\n")


def format_article_nonfirst(article, entry):
    if article.article_type == "Стаття із газети":
        return f"{article.article_author_surname}, <i>{article.article_title}\n</i>"
    elif article.article_type == "Стаття із журналу":
        return (f"{article.article_author_name} {article.article_author_surname}, <i>{article.article_title}</i>, "
                f"{entry.notes if entry.notes != "відсутня" else ""}\n")
    else:
        return f"{article.article_author_name} {article.article_author_surname}, <i>{article.article_title}</i>\n"


def format_interview_first(interview):
    return (
        f"{interview.getting_interviewed} ({interview.gi_year_of_birth.year} р. н.), провів(ла) інтерв'ю {interview.interviewing}, "
        f"{interview.location_of_interview}, {interview.interview_date.day} {ukrainian_months[interview.interview_date.month]}, "
        f"{interview.interview_date.year}\n")


def format_interview_nonfirst(interview):
    return "{interview.getting_interviewed} ({interview.gi_year_of_birth.year} р. н.), {interview.location_of_interview}\n"


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


bot.polling(none_stop=True)
