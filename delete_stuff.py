from utils import *

"""LIST"""


def delete_list(message, user):
    chat_id = message.chat.id
    list_name = message.text.strip()
    user_lists = user.lists
    selected_list = next((lst for lst in user_lists if lst.list_name == list_name), None)
    if message.text == "/back":
        bot.send_message(message.chat.id, "Ти повернувся в головне меню! "
                                          "Якщо хочеш продовжити роботу, вибирай з перелічених функцій:"
                                          "/create_list - створити список літератури.\n"
                                          "/create_entry - створити елемент у списку літератури.\n"
                                          "/show_lists - передивитися свої списки літератури.\n"
                                          "/delete_list - видалити список.\n"
                                          "/delete_entry - видалити джерело у списку літератури.")
        return
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


"""ENTRY"""


def process_selected_list_deletion(message, user):
    chat_id = message.chat.id
    user_lists = user.lists
    list_name_to_utilize = message.text.strip()
    selected_list = next((lst for lst in user_lists if lst.list_name == list_name_to_utilize), None)
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


def process_entry_type_for_deletion(message, selected_list):
    chat_id = message.chat.id
    source_type = message.text
    if message.text == "/back":
        bot.send_message(message.chat.id, "Ти повернувся в головне меню! "
                                          "Якщо хочеш продовжити роботу, вибирай з перелічених функцій:\n"
                                          "/create_list - створити список літератури.\n"
                                          "/create_entry - створити елемент у списку літератури.\n"
                                          "/show_lists - передивитися свої списки літератури.\n"
                                          "/delete_list - видалити список.\n"
                                          "/delete_entry - видалити джерело у списку літератури.")
        return
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
    else:
        bot.send_message(chat_id, "Щось пішло не так... Спробуйте знову.")
        bot.register_next_step_handler(message, process_entry_type_for_deletion, selected_list)


def delete_entry(message, selected_list, source_type):
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
            bot.send_message(chat_id, f"Інтерв'ю з {entry_name} успішно видалено.")
        else:
            bot.send_message(chat_id, f"Інтерв'ю з {entry_name} не знайдено.")
