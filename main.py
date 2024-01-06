from datetime import datetime
import telebot
from telebot import types
from db_models import *

BOT_TOKEN = "6894160738:AAG58kcR8eg9l8VCHGe6Gk5TipnQcLKt42E"
DATABASE_URL = 'mysql+mysqlconnector://root:Funnyhaha111@localhost:3306/lit_list'

engine = create_engine(DATABASE_URL)
Base.metadata.create_all(bind=engine)

Session = scoped_session(sessionmaker(bind=engine))
session = Session()

bot = telebot.TeleBot(BOT_TOKEN)


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
                                  "/delete_list - видалити список.")
    else:
        bot.send_message(chat_id, "Знову привіт! Вибирай, що хочеш зробити:\n"
                                  "/create_list - створити список літератури.\n"
                                  "/create_entry - створити елемент у списку літератури.\n"
                                  "/show_lists - передивитися свої списки літератури.\n"
                                  "/delete_list - видалити список.")


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

    msg = bot.send_message(chat_id, "Файно! Яка назва?")
    bot.register_next_step_handler(msg, lambda m: process_entry_details(m, selected_list))


def process_entry_details(message, selected_list):
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message, lambda m: process_entry_details(m, selected_list))
        return

    title = message.text.strip()
    msg = bot.send_message(message.chat.id, "Хто автор?")
    bot.register_next_step_handler(msg, lambda m: process_author(m, title, selected_list))


def process_author(message, title, selected_list):
    chat_id = message.chat.id
    try:
        author_name, author_surname = message.text.strip().split(maxsplit=1)
    except ValueError:
        bot.send_message(chat_id, "Введіть як ім'я, так і прізвище автора. Спробуйте ще раз.")
        bot.register_next_step_handler(message, lambda m: process_author(m, title, selected_list))
        return

    msg = bot.send_message(chat_id, "Який рік?")
    bot.register_next_step_handler(msg, lambda m: process_year(m, title, author_name, author_surname, selected_list))


def process_year(message, title, author_name, author_surname, selected_list):
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
    chat_id = message.chat.id

    publisher = message.text

    save_entry(title, author_name, author_surname, year, publisher, selected_list)
    bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")


def save_entry(title, author_name, author_surname, year, publisher, selected_list):
    new_entry = Entry(
        title=title,
        authors_name=author_name,
        authors_surname=author_surname,
        year_of_publishing=year,
        publisher=publisher,
        list_id=selected_list.list_id
    )
    session.add(new_entry)
    session.commit()
    print(selected_list.list_id)


@bot.message_handler(commands=['show_lists'])
def show_lists(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if user:
        lists = user.lists
        if lists:
            for i, user_list in enumerate(lists, start=1):
                list_content = f"Список літератури:\n"
                list_content += f"Назва: {user_list.list_name}\n"

                entries = user_list.entries
                if entries:
                    for j, entry in enumerate(entries, start=1):
                        list_content += (
                            f"\n{j}. {entry.authors_surname}, {entry.authors_name}: {entry.title}: {entry.publisher}, "
                            f"{entry.year_of_publishing}\n")
                else:
                    list_content += "Список порожній."
                bot.send_message(chat_id, list_content)
        else:
            bot.send_message(chat_id, "У тебе ще немає списків. Використай /create_list, аби створити список.")
    else:
        bot.send_message(chat_id, "Ти не зареєстрований. Клацни /start аби зарєструватися.")


@bot.message_handler(commands=['delete_list'])
def start_delete_list(message):
    chat_id = message.chat.id
    user = session.query(User).filter_by(chat_id=chat_id).first()

    if not user:
        bot.send_message(chat_id, "Користувача не знайдено. Почніть спочатку.")
        return

    bot.send_message(chat_id, "Введіть назву списку, який ви хочете видалити.")
    bot.register_next_step_handler(message, delete_list, user)


def delete_list(message, user):
    chat_id = message.chat.id
    list_name = message.text.strip()

    user_lists = user.lists

    selected_list = next((lst for lst in user_lists if lst.list_name == list_name), None)

    if not selected_list:
        bot.send_message(chat_id, "Список з такою назвою не існує. Спробуйте ще раз.")
        bot.register_next_step_handler(message, lambda m: delete_list(m, user))
        return

    entries_in_list = selected_list.entries
    session.delete(entries_in_list)
    session.delete(selected_list)
    session.commit()

    bot.send_message(chat_id, f"Список '{list_name}' був успішно видалений.")


bot.polling(none_stop=True)
