from utils import *
from db_models import *

book_data = {}



def process_book_data(message, selected_list):
    chat_id = message.chat.id
    book_data["book_name"] = message.text

    msg = bot.send_message(chat_id, "Скільки авторів у книзі?")
    bot.register_next_step_handler(msg, lambda m: process_author_count(m, selected_list))


def process_author_count(message, selected_list):
    chat_id = message.chat.id
    try:
        book_data["author_count"] = int(message.text)
        if book_data["author_count"] < 1:
            raise ValueError("Кількість авторів має бути 1 або більше.")
    except ValueError:
        bot.send_message(chat_id, "Невірний формат. Введіть ціле число більше 0.")
        bot.register_next_step_handler(message, lambda m: process_book_data(m, selected_list))
        return

    process_author_data(message, selected_list)


def process_author_data(message, selected_list):
    chat_id = message.chat.id

    msg = bot.send_message(chat_id,
                           f"Як звати {'першого ' if book_data['author_count'] > 1 else ''}автора? {'(якщо було вказно кількість авторів більше, ніж один, введіть прізвище першого автора)' if book_data['author_count'] > 1 else ''}")
    bot.register_next_step_handler(msg, lambda m: process_author_name(m, selected_list))


def process_author_name(message, selected_list):
    chat_id = message.chat.id
    author1_name = message.text

    book_data["author1_name"] = author1_name
    book_data["author2_name"] = ''

    msg = bot.send_message(chat_id, f"Яке у {'першого ' if book_data['author_count'] >= 2 else ''}автора прізвище?")
    bot.register_next_step_handler(msg, lambda m: process_author_surname(m, selected_list))


def process_author_surname(message, selected_list):
    chat_id = message.chat.id
    author1_surname = message.text

    book_data["author1_surname"] = author1_surname

    if book_data["author_count"] == 2:
        msg = bot.send_message(chat_id, "Як звати другого автора?")
        bot.register_next_step_handler(msg, lambda m: process_second_author_name(m, selected_list))
    elif book_data["author_count"] > 2:
        book_data["author1_surname"] = author1_surname + " та ін."
        book_data["author2_surname"] = ""
        msg = bot.send_message(chat_id, "Яке видавництво?")
        bot.register_next_step_handler(msg, lambda m: process_publisher(m, selected_list))
    else:
        book_data["author2_surname"] = ""
        msg = bot.send_message(chat_id, "Яке видавництво?")
        bot.register_next_step_handler(msg, lambda m: process_publisher(m, selected_list))


def process_second_author_name(message, selected_list):
    chat_id = message.chat.id
    author2_name = message.text.strip()

    book_data["author2_name"] = author2_name

    msg = bot.send_message(chat_id, "Яке у другого автора прізвище?")
    bot.register_next_step_handler(msg, lambda m: process_second_author_surname(m, selected_list))


def process_second_author_surname(message, selected_list):
    chat_id = message.chat.id
    author2_surname = message.text.strip()

    book_data['author2_surname'] = author2_surname
    msg = bot.send_message(chat_id, "Яке видавництво?")
    bot.register_next_step_handler(msg, lambda m: process_publisher(m, selected_list))


def process_publisher(message, selected_list):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message, lambda m: process_author_surname(m, selected_list))
        return
    book_data['publisher'] = message.text
    chat_id = message.chat.id
    msg = bot.send_message(chat_id, "Яке місто видавництва?")
    bot.register_next_step_handler(msg, lambda m: process_publisher_city(m, selected_list))


def process_publisher_city(message, selected_list):
    chat_id = message.chat.id
    book_data['publisher_city'] = message.text
    msg = bot.send_message(chat_id, "Який рік публікації?")
    bot.register_next_step_handler(msg, lambda m: process_year(m, selected_list))


def process_year(message, selected_list):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message, lambda m: process_publisher_city(m, selected_list))
        return
    chat_id = message.chat.id
    year_input = message.text
    try:
        book_data['year'] = datetime.strptime(year_input, '%Y').date()
    except ValueError:
        bot.send_message(chat_id, "Неправильний формат року. Введіть рік у форматі YYYY (наприклад, 2012).")
        bot.register_next_step_handler(message, lambda m: process_year(m, selected_list))
        return
    msg = bot.send_message(chat_id,
                           "На якій сторінці знаходиться те, на що ви створюєте посилання? (якщо вона відсутня, напишіть слово 'відсутня')")
    bot.register_next_step_handler(msg, lambda m: process_refs(m, selected_list))


def process_refs(message, selected_list):
    refs = ""
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message, lambda m: process_publisher_city(m, selected_list))
        return

    if message.text.lower() == "відсутня":
        book_data['refs'] = ""
    elif message.text.isdigit():
        book_data['refs'] = int(message.text)
    else:
        bot.send_message(message.chat.id, "Щось пішло не так... Спробуйте ще раз.")
        bot.register_next_step_handler(message, lambda m: process_publisher_city(m, selected_list))

    chat_id = message.chat.id
    save_book(book_data, selected_list)
    bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")


def save_book(book_data, selected_list):
    new_book = Book(
        book_title=book_data["book_name"],
        is_ebook=False,
        authors1_name=book_data["author1_name"],
        authors1_surname=book_data["author1_surname"],
        authors2_name=book_data["author2_name"],
        authors2_surname=book_data["author2_surname"],
        publisher_name=book_data["publisher"],
        publisher_city=book_data["publisher_city"],
        publisher_year=book_data["year"].year,
        refs=book_data["refs"],
        list_id=selected_list.list_id
    )
    session.add(new_book)
    session.commit()

    book_id = new_book.book_id
    new_entry = Entry(
        entry_type='book',
        from_book_resource_id=book_id,
        mentioning="first",
        list_id=selected_list.list_id
    )
    session.add(new_entry)
    session.commit()
