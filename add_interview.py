from utils import *
from db_models import *

interview_info = {}


def process_interview_data(message, selected_list):
    chat_id = message.chat.id
    getting_interviewed = message.text
    interview_info["getting_interviewed"] = getting_interviewed
    msg = bot.send_message(chat_id, "Який рік народження людини, з якою проводили інтерв'ю?")
    bot.register_next_step_handler(msg, lambda m: process_dob_of_gi(m, selected_list))


def process_dob_of_gi(message, selected_list):
    chat_id = message.chat.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_interview_data(m, selected_list))
    year_input = message.text
    try:
        dob_of_gi = datetime.strptime(year_input, '%Y').date()
        interview_info["dob_of_gi"] = dob_of_gi
    except ValueError:
        bot.send_message(chat_id, "Неправильний формат року. Введіть рік у форматі YYYY (наприклад, 2012).")
        bot.register_next_step_handler(lambda m: process_interview_date(m, selected_list))
    msg = bot.send_message(chat_id, "Хто проводив інтерв'ю? (введіть повне ім'я)")
    bot.register_next_step_handler(msg, lambda m: process_interviewer(m, selected_list))


def process_interviewer(message, selected_list):
    chat_id = message.chat.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_dob_of_gi(m, selected_list))
    interviewer = message.text
    interview_info["interviewer"] = interviewer
    msg = bot.send_message(chat_id, "Де було проведено інтерв'ю?")
    bot.register_next_step_handler(msg, lambda m: process_interview_location(m, selected_list))


def process_interview_location(message, selected_list):
    chat_id = message.chat.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_dob_of_gi(m, selected_list))
    location = message.text
    interview_info["location"] = location
    msg = bot.send_message(chat_id, "Коли було проведене інтерв'ю?")
    bot.register_next_step_handler(msg, lambda m: process_interview_date(m, selected_list))


def process_interview_date(message, selected_list):
    chat_id = message.chat.id
    if message.content_type != 'text':
        bot.send_message(message.chat.id, 'Назва елементу має бути текстом. Спробуйте ще раз.')
        bot.register_next_step_handler(message,
                                       lambda m: process_dob_of_gi(m, selected_list))
    interview_date = datetime.strptime(message.text, "%d-%m-%Y").date()
    interview_info["interview_date"] = interview_date
    save_interview(selected_list)
    bot.send_message(chat_id, f"Елемент збережений у список '{selected_list.list_name}'!")


def save_interview(selected_list):
    new_inter = Interview(
        getting_interviewed=interview_info.get("getting_interviewed"),
        gi_year_of_birth=interview_info.get("dob_of_gi"),
        interviewing=interview_info.get("interviewer"),
        location_of_interview=interview_info.get("location"),
        interview_date=interview_info.get("interview_date"),
        list_id=selected_list.list_id
    )
    session.add(new_inter)
    session.commit()

    inter_id = new_inter.interview_id
    inter_entry = Entry(
        entry_type='interview',
        from_inter_resource_id=inter_id,
        mentioning='first',
        list_id=selected_list.list_id
    )
    session.add(inter_entry)
    session.commit()
