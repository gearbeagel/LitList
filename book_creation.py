from main import *


def process_book_details(message, selected_list):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message, lambda m: process_list_choice(m))
        return

    title = message.text.strip()
    msg = bot.send_message(message.chat.id, "Як звати автора?")
    bot.register_next_step_handler(msg, lambda m: process_author_name(m, title, selected_list))


def process_author_name(message, title, selected_list):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message, lambda m: process_book_details(m, selected_list))
        return
    chat_id = message.chat.id
    author_name = message.text

    msg = bot.send_message(chat_id, "Яке у нього прізвище?")
    bot.register_next_step_handler(msg, lambda m: process_author_surname(m, title, author_name, selected_list))


def process_author_surname(message, title, author_name, selected_list):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message, lambda m: process_author_name(m, title, selected_list))
        return
    chat_id = message.chat.id
    author_surname = message.text

    msg = bot.send_message(chat_id, "Який рік?")
    bot.register_next_step_handler(msg, lambda m: process_year(m, title, author_name, author_surname, selected_list))


def process_year(message, title, author_name, author_surname, selected_list):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message, lambda m: process_author_surname(m, title, author_name, selected_list))
        return
    chat_id = message.chat.id
    year_input = message.text
    try:
        year = datetime.strptime(year_input, '%Y').date()
    except ValueError:
        bot.send_message(chat_id, "Неправильний формат року. Введіть рік у форматі YYYY (наприклад, 2012).")
        bot.register_next_step_handler(message,
                                       lambda m: process_year(m, title, author_name, author_surname, selected_list))
        return

    msg = bot.send_message(chat_id, "Яке видавництво?")
    bot.register_next_step_handler(msg, lambda m: process_publisher(m, title, author_name, author_surname, year,
                                                                    selected_list))


def process_publisher(message, title, author_name, author_surname, year, selected_list):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_year(m, title, author_name, author_surname, selected_list))
        return
    chat_id = message.chat.id

    publisher = message.text

    save_entry(title, author_name, author_surname, year, publisher, selected_list)
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
