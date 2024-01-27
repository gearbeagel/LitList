from utils import *
from db_models import *


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