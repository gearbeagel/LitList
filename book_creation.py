from main import *


def process_book_data(message, selected_list):
    chat_id = message.chat.id
    list_id = selected_list.list_id

    msg = bot.send_message(chat_id, "Скільки авторів у книзі?")
    bot.register_next_step_handler(msg, lambda m: process_author_count(m, list_id))


def process_author_count(message, list_id, selected_list):
    chat_id = message.chat.id
    try:
        author_count = int(message.text)
        if author_count < 1:
            raise ValueError("Кількість авторів має бути 1 або більше.")
    except ValueError:
        bot.send_message(chat_id, "Невірний формат. Введіть ціле число більше 0.")
        bot.register_next_step_handler(message, lambda m: process_book_data(m, selected_list))
        return

    session.data[chat_id] = {"list_id": list_id, "author_count": author_count}
    process_author_data(chat_id)


def process_author_data(chat_id):
    list_id = session.data[chat_id]["list_id"]
    author_count = session.data[chat_id]["author_count"]

    if author_count == 1 or author_count == 2:
        msg = bot.send_message(chat_id, f"Як звати {'першого' if author_count == 2 else ''} автора?")
        bot.register_next_step_handler(msg, lambda m: process_author_name(m, list_id, author_count))
    else:
        msg = bot.send_message(chat_id, "Як звати першого автора?")
        bot.register_next_step_handler(msg, lambda m: process_author_name(m, list_id, author_count))


def process_author_name(message, list_id, author_count):
    chat_id = message.chat.id
    title = message.text.strip()

    if author_count == 2:
        msg = bot.send_message(chat_id, "Яке у другого автора прізвище?")
        bot.register_next_step_handler(msg, lambda m: process_author_surname(m, list_id, title))
    else:
        process_author_surname(chat_id, list_id, title)


def process_author_surname(message, list_id, title):
    chat_id = message.chat.id
    author_surname = message.text.strip()

    msg = bot.send_message(chat_id, "Який рік видання?")
    bot.register_next_step_handler(msg, lambda m: process_year(m, list_id, title, author_surname))


def process_publisher(message, title, author_name, author_surname, publisher_city, year, selected_list):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_year(m, title, author_name, author_surname,
                                                              publisher_city, year, selected_list))
        return
    chat_id = message.chat.id

    publisher = message.text

    process_publisher_city(chat_id, title, author_name, author_surname, publisher_city, year, publisher, selected_list)


def process_publisher_city(chat_id, title, author_name, author_surname, publisher_city, year, publisher, selected_list):
    msg = bot.send_message(chat_id, "Яке місто видавництва?")
    bot.register_next_step_handler(msg, lambda m: process_year(m, title, author_name, author_surname,
                                                               publisher_city, year, publisher, selected_list))


def process_year(message, title, author_name, author_surname, publisher_city, year, publisher, selected_list):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_publisher_city(m, title, author_name, author_surname,
                                                                        publisher_city, year, publisher, selected_list))
        return
    chat_id = message.chat.id
    year_input = message.text
    try:
        year = datetime.strptime(year_input, '%Y').date()
    except ValueError:
        bot.send_message(chat_id, "Неправильний формат року. Введіть рік у форматі YYYY (наприклад, 2012).")
        bot.register_next_step_handler(message,
                                       lambda m: process_year(m, title, author_name, author_surname,
                                                              publisher_city, year, publisher, selected_list))
        return

    save_entry(title, author_name, author_surname, year, publisher_city, publisher, selected_list)
    bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")


def save_entry(title, author_name, author_surname, year, publisher, selected_list):
    new_entry = Book(
        title=title,
        authors_name=author_name,
        authors_surname=author_surname,
        year_of_publishing=year,
        publisher=publisher,
        list_id=selected_list.list_id
    )
    session.add(new_entry)
    session.commit()
