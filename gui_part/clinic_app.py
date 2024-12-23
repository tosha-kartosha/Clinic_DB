import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.exc import SQLAlchemyError
import pandas as pd
import re

m = st.markdown("""
<style>
div.stButton > button:first-child {
    background-color: rgb(164, 224, 207);
}
</style>""", unsafe_allow_html=True)

# Вкладки администратора
def admin_tab():
    st.title("Страница администратора")
    
    if st.session_state.locked:
        st.warning("Приложение закрыто. База данных была удалена. Для повторной инициализации обновите страницу")
    else:
        if (st.session_state.engine is "default" or st.session_state.engine is None) or (str(st.session_state.engine.url) != 'postgresql://adminchik:***@localhost:5432/clinic' and str(st.session_state.engine.url) != 'postgresql://adminchik:***@localhost:5432/postgres'):
            st.session_state.engine = create_engine('postgresql://adminchik:12345@localhost:5432/clinic')
            try:
                with st.session_state.engine.connect() as connection:
                    print("Соединение как администратор установлено успешно.")
            except SQLAlchemyError as error:
                st.error("Ошибка при установлении соединения с базой данных: " + str(error))
                st.session_state.engine = None
        
        specialties = ['Терапевт', 'Гастроэнтеролог', 'Офтальмолог', 'Окулист', 'Невролог', 'Отоларинголог', 'Хирург', 'Психиатр']
        tab = st.sidebar.radio("Выберите действие", ["Добавить врача", "Изменить данные врача", "Посмотреть врачей в поликлинике", "Посмотреть статистику", "Удалить врача", "Стереть данные"])
        
        if tab == "Добавить врача":
            st.subheader("Добавление врача")
            doctor_name = st.text_input("Введите имя врача")
            doctor_surname = st.text_input("Введите фамилию врача")
            doctor_patronymic = st.text_input("Введите отчество врача")
            doctor_specialty = st.selectbox("Выберите специальность врача", specialties)
            
            if st.button("Добавить врача"):
                if not doctor_name or not doctor_surname or not doctor_patronymic or not doctor_specialty:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_name) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_surname) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_patronymic):
                    st.warning("Поля должны содержать только буквы русского или английского алфавита")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL add_doctor(:surname, :name, :patronymic, :specialization);'''
                            connection.execute(text(sql_call_procedure), {
                                "surname": doctor_surname,
                                "name": doctor_name,
                                "patronymic": doctor_patronymic,
                                "specialization": doctor_specialty
                            })
                            connection.commit()
                        st.success(f"Врач {doctor_name} {doctor_surname} {doctor_patronymic} добавлен!")
                    
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "повторяющееся значение ключа нарушает ограничение уникальности" in str(error):
                            st.warning("Врач с такими данными уже существует в поликлинике")
                        else:
                            st.error("Ошибка при добавлении врача: " + str(error))

        elif tab == "Изменить данные врача":
            st.subheader("Изменение данных у врача")
            action = st.selectbox("Выберите действие", ["Изменить ФИО", "Изменить специальность"])
            
            if action == "Изменить ФИО":
                doctor_id = st.number_input("Введите ID врача для изменения", min_value=1)
                doctor_surname = st.text_input("Введите новую фамилию врача")
                doctor_name = st.text_input("Введите новое имя врача")
                doctor_patronymic = st.text_input("Введите новое отчество врача")
                if st.button("Внести изменения"):
                    if not doctor_name or not doctor_surname or not doctor_patronymic:
                        st.warning("Заполните все поля!")
                    elif not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_name) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_surname) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_patronymic):
                        st.warning("Поля должны содержать только буквы русского или английского алфавита")
                    else:
                        try:
                            with st.session_state.engine.connect() as connection:
                                sql_call_procedure = ''' CALL update_doctor_fio(:id_doctor, :surname, :name, :patronymic);'''
                                connection.execute(text(sql_call_procedure), {
                                    "id_doctor": doctor_id,
                                    "surname": doctor_surname,
                                    "name": doctor_name,
                                    "patronymic": doctor_patronymic
                                })
                                connection.commit()
                            st.success(f"Изменения внесены!")
                        except SQLAlchemyError as error:
                            if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                                st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                            elif "Врач не найден" in str(error):
                                st.warning(f"Врач с ID {doctor_id} не найден!")
                            elif "повторяющееся значение ключа нарушает ограничение уникальности" in str(error):
                                st.warning("Врач с такими данными уже существует в поликлинике")
                            else:
                                st.error("Ошибка при изменении врача: " + str(error))
            
            elif action == "Изменить специальность":
                doctor_id = st.number_input("Введите ID врача для изменения", min_value=1)
                doctor_specialty = st.selectbox("Выберите новую специальность врача", specialties)
                if st.button("Внести изменения"):
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL update_doctor_spec(:id_doctor, :specialization);'''
                            connection.execute(text(sql_call_procedure), {
                                "id_doctor": doctor_id,
                                "specialization": doctor_specialty,
                            })
                            connection.commit()
                        st.success(f"Изменения внесены!")
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "Врач не найден" in str(error):
                            st.warning(f"Врач с ID {doctor_id} не найден!")
                        elif "повторяющееся значение ключа нарушает ограничение уникальности" in str(error):
                            st.warning("Врач с такими данными уже существует в поликлинике")
                        else:
                            st.error("Ошибка при изменении врача: " + str(error))
        
        elif tab == "Посмотреть врачей в поликлинике":
            st.subheader("Список врачей")
            if st.button("Отобразить"):
                try:
                    with st.session_state.engine.connect() as connection:
                        result = connection.execute(text("SELECT * FROM get_doctor();"))
                        doctor_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                        if not doctor_table.empty:
                            st.dataframe(doctor_table)
                        else:
                            st.write("Врачи не найдены.")
                        connection.commit()
                except SQLAlchemyError as error:
                    if "Функция с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    else:
                        st.error("Ошибка при получении списка врачей: " + str(error))

        elif tab == "Посмотреть статистику":
            st.subheader("Статистика врачей в поликлинике по количеству записей")
            if st.button("Отобразить"):
                try:
                    with st.session_state.engine.connect() as connection:
                        result = connection.execute(text("SELECT * FROM get_doctor_statistic();"))
                        doctor_table_stat = pd.DataFrame(result.fetchall(), columns=result.keys())
                        if not doctor_table_stat.empty:
                            st.dataframe(doctor_table_stat)
                        else:
                            st.write("Врачи не найдены.")
                        connection.commit()
                except SQLAlchemyError as error:
                    if "Функция с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    else:
                        st.error("Ошибка при получении списка врачей: " + str(error))

        elif tab == "Удалить врача":
            st.subheader("Удаление врача")
            action = st.selectbox("Выберите способ удаления", ["Удалить врача по ID", "Удалить врача по ФИО и специальности", "Удалить врачей по специальности", "Удалить всех врачей из поликлиники"])
            if action == "Удалить врача по ID":
                doctor_id = st.number_input("Введите ID врача для удаления", min_value=1)
                if st.button("Удалить врача"):
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL delete_doctor(:doctor_id);'''
                            connection.execute(text(sql_call_procedure), {
                                "doctor_id": doctor_id,
                            })
                            connection.commit()
                        st.success(f"Врач с ID {doctor_id} удален!")
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "не существует в базе" in str(error):
                            st.warning(f"Врач с ID {doctor_id} не найден!")
                        else:
                            st.error("Ошибка при удалении врача: " + str(error))
            
            elif action == "Удалить врача по ФИО и специальности":
                doctor_surname = st.text_input("Фамилия врача")
                doctor_name = st.text_input("Имя врача")
                doctor_patronymic = st.text_input("Отчество врача")
                doctor_specialty = st.selectbox("Специальность врача", specialties)
                if st.button("Удалить"):
                    if not doctor_name or not doctor_surname or not doctor_patronymic:
                        st.warning("Заполните все поля!")
                    elif not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_name) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_surname) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_patronymic):
                        st.warning("Поля должны содержать только буквы русского или английского алфавита")
                    else:
                        try:
                            with st.session_state.engine.connect() as connection:
                                sql_call_procedure = ''' CALL delete_doctor(:surname, :name, :patronymic, :specialization);'''
                                connection.execute(text(sql_call_procedure), {
                                    "surname": doctor_surname,
                                    "name": doctor_name,
                                    "patronymic": doctor_patronymic,
                                    "specialization": doctor_specialty
                                })
                                connection.commit()
                            st.success(f"{doctor_specialty} {doctor_surname} {doctor_name} {doctor_patronymic} удален!")
                        except SQLAlchemyError as error:
                            if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                                st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                            elif "не существует в базе" in str(error):
                                st.warning(f"Врач {doctor_specialty} {doctor_surname} {doctor_name} {doctor_patronymic} не найден!")
                            else:
                                st.error("Ошибка при удалении врача: " + str(error))
            
            elif action == "Удалить врачей по специальности":
                doctor_specialty = st.selectbox("Специальность врача", specialties)
                if st.button("Удалить"):
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL delete_doctor_on_spec(:specialization);'''
                            connection.execute(text(sql_call_procedure), {
                                "specialization": doctor_specialty
                            })
                            connection.commit()
                        st.success(f"Все врачи по специальности {doctor_specialty} и записи к ним были удалены!")
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "не существует в базе" in str(error):
                            st.warning(f"Врачи по специальности {doctor_specialty} не найдены!")
                        else:
                            st.error("Ошибка при удалении врача: " + str(error))
            
            elif action == "Удалить всех врачей из поликлиники":
                if st.button("Удалить"):
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL delete_all_doctor();'''
                            connection.execute(text(sql_call_procedure))
                            connection.commit()
                        st.success(f"Все врачи удалены из базы!")
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        else:
                            st.error("Ошибка при удалении врачей: " + str(error))

        elif tab == "Стереть данные":
            st.subheader("Удаление")
            action = st.selectbox("Выберите, что хотите удалить", ["Стереть данные из БД без удаления БД", "Удалить БД"])
            
            if action == "Стереть данные из БД без удаления БД":
                if st.button("Удалить"):
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL delete_all();'''
                            connection.execute(text(sql_call_procedure))
                            connection.commit()
                        st.success(f"База данных очищена!")
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        else:
                            st.error("Ошибка при очистке базы данных: " + str(error))
            
            elif action == "Удалить БД":
                if st.button("Удалить"):
                    if st.session_state.engine is not None:
                        st.session_state.engine.dispose()
                    st.session_state.engine = create_engine('postgresql://adminchik:12345@localhost:5432/postgres')
                    try:
                        with st.session_state.engine.connect() as connection:
                            st.session_state.engine.dispose()
                            sql_call_procedure = ''' CALL drop_clinic_db();'''
                            connection.execute(text(sql_call_procedure))
                            connection.commit()
                        st.success(f"БД удалена!")
                        st.session_state.locked = True
                        st.experimental_rerun()
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        else:
                            st.error("Ошибка при удалении БД: " + str(error))

        if st.sidebar.button("Выйти"):
            st.session_state.logged_in = False
            st.session_state.user_role = None
            st.session_state.engine = "default"
            st.experimental_rerun()

# Вкладки регистратуры
def registrar_tab():
    st.title("Страница Регистратуры")

    if st.session_state.engine is None or st.session_state.engine is "default" or str(st.session_state.engine.url) != 'postgresql://regist:***@localhost:5432/clinic':
        st.session_state.engine = create_engine('postgresql://regist:123@localhost:5432/clinic')
        try:
            with st.session_state.engine.connect() as connection:
                print("Соединение как регистратура установлено успешно.")
        except SQLAlchemyError as error:
            st.error("Ошибка при установлении соединения с базой данных: " + str(error))
            st.session_state.engine = None
    
    specialties = ['Терапевт', 'Гастроэнтеролог', 'Офтальмолог', 'Окулист', 'Невролог', 'Отоларинголог', 'Хирург', 'Психиатр']
    tab = st.sidebar.radio("Выберите действие", ["Просмотр графика записей", "Просмотр врачей", "Добавление пациента", "Добавление записи", "Изменение записи", "Удаление записи", "Поиск пациента", "Изменение данных у пациента"])

    if tab == "Просмотр графика записей":
        st.subheader("Просмотр графика записей")
        action = st.selectbox("Выберите отображение графика записей", ["Полный график записей", "Расписание конкретного врача", "Расписание по специальности"])
        
        if action == "Полный график записей":
            if st.button("Отобразить"):
                try:
                    with st.session_state.engine.connect() as connection:
                        result = connection.execute(text("SELECT * FROM get_schedule();"))
                        appointment_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                        if not appointment_table.empty:
                            st.dataframe(appointment_table)
                        else:
                            st.write("Записей нет.")
                        connection.commit()
                except SQLAlchemyError as error:
                    if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                        st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    else:
                        st.error("Ошибка при получении графика записей: " + str(error))
        
        elif action == "Расписание конкретного врача":
            doctor_name = st.text_input("Введите имя врача")
            doctor_surname = st.text_input("Введите фамилию врача")
            doctor_patronymic = st.text_input("Введите отчество врача")
            
            if st.button("Поиск"):
                if not doctor_name or not doctor_surname or not doctor_patronymic:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_name) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_surname) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_patronymic):
                    st.warning("Поля должны содержать только буквы русского или английского алфавита")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' SELECT * FROM get_schedule(:surname, :name, :patronymic);'''
                            result = connection.execute(text(sql_call_procedure), {
                                "surname": doctor_surname,
                                "name": doctor_name,
                                "patronymic": doctor_patronymic,
                            })
                            appointment_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                            if not appointment_table.empty:
                                st.dataframe(appointment_table)
                            else:
                                st.write("Записей нет.")
                            connection.commit()
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        else:
                            st.error("Ошибка при получении графика записей: " + str(error))
        
        elif action == "Расписание по специальности":
            doctor_specialty = st.selectbox("Выберите специальность врача", specialties)
            if st.button("Поиск"):
                try:
                    with st.session_state.engine.connect() as connection:
                        sql_call_procedure = ''' SELECT * FROM get_schedule(:specialization);'''
                        result = connection.execute(text(sql_call_procedure), {
                            "specialization": doctor_specialty
                        })
                        appointment_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                        if not appointment_table.empty:
                            st.dataframe(appointment_table)
                        else:
                            st.write("Записей нет.")
                        connection.commit()
                except SQLAlchemyError as error:
                    if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                        st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    else:
                        st.error("Ошибка при получении графика записей: " + str(error))
    
    elif tab == "Просмотр врачей":
        st.subheader("Просмотр врачей в поликлинике")
        if st.button("Отобразить"):
            try:
                with st.session_state.engine.connect() as connection:
                    result = connection.execute(text("SELECT * FROM get_doctor();"))
                    doctor_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                    if not doctor_table.empty:
                        st.dataframe(doctor_table)
                    else:
                        st.write("Врачи не найдены.")
                    connection.commit()
            except SQLAlchemyError as error:
                if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                    st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                else:
                    st.error("Ошибка при получении списка врачей: " + str(error))
    
    elif tab == "Добавление пациента":
        st.subheader("Добавление пациента")
        pat_snils = st.text_input("Введите СНИЛС пациента (123-456-789 01)")
        pat_name = st.text_input("Введите имя пациента")
        pat_surname = st.text_input("Введите фамилию пациента")
        pat_patronymic = st.text_input("Введите отчество пациента")
        pat_birth = st.date_input("Введите дату рождения пациента (дд-мм-гггг)")
        pat_address = st.text_input("Введите адрес пациента")
        if st.button("Добавить пациента"):
            if not pat_snils or not pat_name or not pat_surname or not pat_patronymic or not pat_birth or not pat_address:
                st.warning("Заполните все поля!")
            elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', pat_snils):
                st.warning("Неверный формат СНИЛС")
            elif not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_name) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_surname) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_patronymic):
                st.warning("Поля ФИО пациента должны содержать только буквы русского или английского алфавита")
            elif not re.match(r'^(?=.*[a-zA-Zа-яА-ЯёЁ0-9])(?=.*\d)[a-zA-Zа-яА-ЯёЁ0-9.,]*$', pat_address):
                st.warning("Поле адреса может содержать только цифры (хотя бы 1), буквы русского или английского алфавита (хотя бы 1), символы ',' и '.'.")
            else:
                try:
                    with st.session_state.engine.connect() as connection:
                        sql_call_procedure = ''' CALL add_patient(:snils, :surname, :name, :patronymic, :birthdate, :address);'''
                        connection.execute(text(sql_call_procedure), {
                            "snils": pat_snils,
                            "surname": pat_surname,
                            "name": pat_name,
                            "patronymic": pat_patronymic,
                            "birthdate": pat_birth,
                            "address": pat_address
                        })
                        connection.commit()
                    st.success(f"Пациент {pat_surname} {pat_name} {pat_patronymic} добавлен!")
                
                except SQLAlchemyError as error:
                    if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                        st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    elif "повторяющееся значение ключа нарушает ограничение уникальности" in str(error):
                        st.warning("Пациент с таким СНИЛС уже существует")
                    else:
                        st.error("Ошибка при добавлении пациента: " + str(error))
    
    elif tab == "Изменение данных у пациента":
        st.subheader("Изменение данных у пациента")
        action = st.selectbox("Выберите действие", ["Изменить ФИО", "Изменить адрес"])
        
        if action == "Изменить ФИО":
            pat_snils = st.text_input("Введите СНИЛС пациента (123-456-789 01)")
            pat_name = st.text_input("Введите имя пациента")
            pat_surname = st.text_input("Введите фамилию пациента")
            pat_patronymic = st.text_input("Введите отчество пациента")
            if st.button("Внести изменения"):
                if not pat_snils or not pat_name or not pat_surname or not pat_patronymic:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', pat_snils):
                    st.warning("Неверный формат СНИЛС")
                elif not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_name) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_surname) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_patronymic):
                    st.warning("Поля ФИО пациента должны содержать только буквы русского или английского алфавита")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL update_patient_med(:par_snils, :pat_surname, :par_name, :par_patro);'''
                            connection.execute(text(sql_call_procedure), {
                                "par_snils": pat_snils,
                                "pat_surname": pat_surname,
                                "par_name": pat_name,
                                "par_patro": pat_patronymic
                            })
                            connection.commit()
                        st.success("Изменения внесены в базу!")
                    
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "повторяющееся значение ключа нарушает ограничение уникальности" in str(error):
                            st.warning("Пациент с таким СНИЛС уже существует")
                        elif "Пациент не найден" in str(error):
                            st.warning("Пациент не найден")
                        else:
                            st.error("Ошибка при изменении ФИО: " + str(error))
        
        elif action == "Изменить адрес":
            pat_snils = st.text_input("Введите СНИЛС пациента (123-456-789 01)")
            pat_address = st.text_input("Введите адрес пациента")
            if st.button("Внести изменения"):
                if not pat_snils or not pat_address:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', pat_snils):
                    st.warning("Неверный формат СНИЛС")
                elif not re.match(r'^(?=.*[a-zA-Zа-яА-ЯёЁ0-9])(?=.*\d)[a-zA-Zа-яА-ЯёЁ0-9.,]*$', pat_address):
                    st.warning("Поле адреса может содержать только цифры (хотя бы 1), буквы русского или английского алфавита (хотя бы 1), символы ',' и '.'.")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL update_patient_med_address(:par_snils, :pat_addr);'''
                            connection.execute(text(sql_call_procedure), {
                                "par_snils": pat_snils,
                                "pat_addr": pat_address
                            })
                            connection.commit()
                        st.success("Изменения внесены в базу!")
                    
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "повторяющееся значение ключа нарушает ограничение уникальности" in str(error):
                            st.warning("Пациент с таким СНИЛС уже существует")
                        elif "Пациент не найден" in str(error):
                            st.warning("Пациент не найден")
                        else:
                            st.error("Ошибка при изменении адреса: " + str(error))
    
    elif tab == "Поиск пациента":
        st.subheader("Поиск пациента")
        action = st.selectbox("Выберите способ поиска", ["Поиск по СНИЛС", "Поиск по ФИО и дате рождения"])
        if action == "Поиск по СНИЛС":
            snils_search = st.text_input("Введите СНИЛС пациента")
            if st.button("Поиск"):
                if not snils_search:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', snils_search):
                    st.warning("Неверный формат СНИЛС")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' SELECT * FROM get_patient(:snils_pat);'''
                            result = connection.execute(text(sql_call_procedure), {
                                "snils_pat": snils_search
                            })
                            patient_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                            if not patient_table.empty:
                                st.dataframe(patient_table)
                            else:
                                st.write(f"Пациент со снилсом {snils_search} не найдены.")
                            connection.commit()
                    except SQLAlchemyError as error:
                        if "Функция с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        else:
                            st.error("Ошибка при получении списка пациентов: " + str(error))
        
        elif action == "Поиск по ФИО и дате рождения":
            pat_surname = st.text_input("Введите фамилию пациента")
            pat_name = st.text_input("Введите имя пациента")
            pat_patronymic = st.text_input("Введите отчество пациента")
            pat_birth = st.date_input("Введите дату рождения пациента")
            if st.button("Поиск"):
                if not pat_name or not pat_surname or not pat_patronymic or not pat_birth:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_name) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_surname) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_patronymic):
                    st.warning("Поля ФИО пациента должны содержать только буквы русского или английского алфавита")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' SELECT * FROM get_patient(:surname, :name, :patronymic, :birth);'''
                            result = connection.execute(text(sql_call_procedure), {
                                "surname": pat_surname,
                                "name": pat_name,
                                "patronymic": pat_patronymic,
                                "birth": pat_birth
                            })
                            patient_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                            if not patient_table.empty:
                                st.dataframe(patient_table)
                            else:
                                st.write(f"Пациент с этими данными не найден.")
                            connection.commit()
                    except SQLAlchemyError as error:
                        if "Функция с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        else:
                            st.error("Ошибка при получении списка врачей: " + str(error))
    
    elif tab == "Добавление записи":
        st.subheader("Добавление записи")
        doctor_id = st.number_input("Введите ID врача", min_value=1)
        patient_snils = st.text_input("Введите СНИЛС пациента")
        appointment_datetime = st.text_input("Введите дату и время записи (гггг-мм-дд чч:мм:сс)")
        
        if st.button("Добавить запись"):
            if not doctor_id or not patient_snils or not appointment_datetime:
                st.warning("Заполните все поля!")
            elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', patient_snils):
                st.warning("Неверный формат СНИЛС")
            elif not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', appointment_datetime):
                st.warning("Неверный формат даты и времени записи")
            else:
                try:
                    with st.session_state.engine.connect() as connection:
                        sql_call_procedure = ''' CALL add_appointment(:doc_id, :pat_snils, :appointment_date);'''
                        connection.execute(text(sql_call_procedure), {
                            "doc_id": doctor_id,
                            "pat_snils": patient_snils,
                            "appointment_date": appointment_datetime
                        })
                        connection.commit()
                    st.success(f"Пациент записан на {appointment_datetime}!")
                except SQLAlchemyError as error:
                    if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                        st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    elif 'нарушает ограничение внешнего ключа "appointment_id_doctor_fkey"' in str(error):
                        st.warning("Такого врача в базе нет!")
                    elif 'нарушает ограничение внешнего ключа "appointment_snils_patient_fkey"' in str(error):
                        st.warning("Такого пациента в базе нет!")
                    else:
                        st.error("Ошибка при добавлении пациента: " + str(error))
    
    elif tab == "Изменение записи":
        appointment_id = st.number_input("Введите ID записи", min_value=1)
        appointment_datetime = st.text_input("Введите дату и время записи (гггг-мм-дд чч:мм:сс)")
        if st.button("Изменить"):
            if not appointment_datetime:
                st.warning("Заполните все поля")
            elif not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', appointment_datetime):
                st.warning("Неверный формат даты и времени записи")
            else:
                try:
                    with st.session_state.engine.connect() as connection:
                        sql_call_procedure = ''' CALL update_appointment_date(:appoint_id, :appoint_date);'''
                        connection.execute(text(sql_call_procedure), {
                            "appoint_id": appointment_id,
                            "appoint_date": appointment_datetime
                        })
                        connection.commit()
                    st.success(f"Запись перенесена на {appointment_datetime}!")
                
                except SQLAlchemyError as error:
                    if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                        st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    elif "Запись не найдена" in str(error):
                        st.warning("Запись не найдена")
                    else:
                        st.error("Ошибка при изменении даты записи: " + str(error))
    
    elif tab == "Удаление записи":
        appointment_id = st.number_input("Введите ID записи", min_value=1)
        if st.button("Удалить"):
            try:
                with st.session_state.engine.connect() as connection:
                    sql_call_procedure = ''' CALL delete_appointment(:appoint_id);'''
                    connection.execute(text(sql_call_procedure), {
                        "appoint_id": appointment_id,
                    })
                    connection.commit()
                st.success(f"Запись с ID {appointment_id} удалена!")
            except SQLAlchemyError as error:
                if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                    st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                elif "не существует в базе" in str(error):
                    st.warning(f"Записи с ID {appointment_id} не найдена!")
                else:
                    st.error("Ошибка при удалении записи: " + str(error))
    
    if st.sidebar.button("Выйти"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.engine = "default"
        st.experimental_rerun()

# Вкладки врача
def doc_tab():
    st.title("Страница Врача")
    
    if st.session_state.engine is None or st.session_state.engine is "default" or str(st.session_state.engine.url) != 'postgresql://doc:***@localhost:5432/clinic':
        st.session_state.engine = create_engine('postgresql://doc:111@localhost:5432/clinic')
        try:
            with st.session_state.engine.connect() as connection:
                print("Соединение как врач установлено успешно.")
        except SQLAlchemyError as error:
            st.error("Ошибка при установлении соединения с базой данных: " + str(error))
            st.session_state.engine = None
    
    specialties = ['Терапевт', 'Гастроэнтеролог', 'Офтальмолог', 'Окулист', 'Невролог', 'Отоларинголог', 'Хирург', 'Психиатр']
    tab = st.sidebar.radio("Выберите действие", ["Просмотр графика записей", "Посмотреть врачей в поликлинике", "Добавить запись", "Изменить записи", "Больничный лист", "Поиск пациента"])

    if tab == "Просмотр графика записей":
        st.subheader("Просмотр графика записей")
        action = st.selectbox("Выберите отображение графика записей", ["Полный график записей", "Расписание конкретного врача", "Расписание по специальности"])
        
        if action == "Полный график записей":
            if st.button("Отобразить"):
                try:
                    with st.session_state.engine.connect() as connection:
                        result = connection.execute(text("SELECT * FROM get_schedule();"))
                        appointment_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                        if not appointment_table.empty:
                            st.dataframe(appointment_table)
                        else:
                            st.write("Записей нет.")
                        connection.commit()
                except SQLAlchemyError as error:
                    if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                        st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    else:
                        st.error("Ошибка при получении графика записей: " + str(error))
        
        elif action == "Расписание конкретного врача":
            doctor_name = st.text_input("Введите имя врача")
            doctor_surname = st.text_input("Введите фамилию врача")
            doctor_patronymic = st.text_input("Введите отчество врача")
            
            if st.button("Поиск"):
                if not doctor_name or not doctor_surname or not doctor_patronymic:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_name) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_surname) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', doctor_patronymic):
                    st.warning("Поля должны содержать только буквы русского или английского алфавита")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' SELECT * FROM get_schedule(:surname, :name, :patronymic);'''
                            result = connection.execute(text(sql_call_procedure), {
                                "surname": doctor_surname,
                                "name": doctor_name,
                                "patronymic": doctor_patronymic,
                            })
                            appointment_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                            if not appointment_table.empty:
                                st.dataframe(appointment_table)
                            else:
                                st.write("Записей нет.")
                            connection.commit()
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        else:
                            st.error("Ошибка при получении графика записей: " + str(error))
        
        elif action == "Расписание по специальности":
            doctor_specialty = st.selectbox("Выберите специальность врача", specialties)
            if st.button("Поиск"):
                try:
                    with st.session_state.engine.connect() as connection:
                        sql_call_procedure = ''' SELECT * FROM get_schedule(:specialization);'''
                        result = connection.execute(text(sql_call_procedure), {
                            "specialization": doctor_specialty
                        })
                        appointment_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                        if not appointment_table.empty:
                            st.dataframe(appointment_table)
                        else:
                            st.write("Записей нет.")
                        connection.commit()
                except SQLAlchemyError as error:
                    if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                        st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    else:
                        st.error("Ошибка при получении графика записей: " + str(error))

    elif tab == "Посмотреть врачей в поликлинике":
        st.subheader("Список врачей")
        if st.button("Отобразить"):
            try:
                with st.session_state.engine.connect() as connection:
                    result = connection.execute(text("SELECT * FROM get_doctor();"))
                    doctor_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                    if not doctor_table.empty:
                        st.dataframe(doctor_table)
                    else:
                        st.write("Врачи не найдены.")
                    connection.commit()
            except SQLAlchemyError as error:
                if "Функция с данными именем и типами аргументов не найдена" in str(error):
                        st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                else:
                    st.error("Ошибка при получении списка врачей: " + str(error))
    
    elif tab == "Изменить записи":
        st.subheader("Изменение записи")
        action = st.selectbox("Выберите действие", ["Удаление записи", "Добавление/изменение кода МКБ", "Изменение даты записи"])
        
        if action == "Удаление записи":
            appointment_id = st.number_input("Введите ID записи", min_value=1)
            if st.button("Удалить"):
                try:
                    with st.session_state.engine.connect() as connection:
                        sql_call_procedure = ''' CALL delete_appointment(:appoint_id);'''
                        connection.execute(text(sql_call_procedure), {
                            "appoint_id": appointment_id,
                        })
                        connection.commit()
                    st.success(f"Запись с ID {appointment_id} удалена!")
                except SQLAlchemyError as error:
                    if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                        st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    elif "не существует в базе" in str(error):
                        st.warning(f"Записи с ID {appointment_id} не найдена!")
                    else:
                        st.error("Ошибка при удалении записи: " + str(error))
        
        elif action == "Добавление/изменение кода МКБ":
            appointment_id = st.number_input("Введите ID записи", min_value=1)
            mkb_code = st.text_input("Введите код МКБ (например, A01.1)")
            if st.button("Изменить/Добавить"):
                if not mkb_code:
                    st.warning('Заполните все поля!')
                elif not re.match(r'^[a-zA-Z]\d{2}\.\d$', mkb_code):
                    st.warning('Недопустимый формат МКб!')
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL update_appointment_icd(:appoint_id, :new_icd);'''
                            connection.execute(text(sql_call_procedure), {
                                "appoint_id": appointment_id,
                                "new_icd": mkb_code
                            })
                            connection.commit()
                        st.success(f"Добавлен код МКБ {mkb_code}!")
                    
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "Запись не найдена" in str(error):
                            st.warning("Запись не найдена")
                        else:
                            st.error("Ошибка при изменении/добавлении кода МКБ: " + str(error))
        
        elif action == "Изменение даты записи":
            appointment_id = st.number_input("Введите ID записи", min_value=1)
            appointment_datetime = st.text_input("Введите дату и время записи (гггг-мм-дд чч:мм:сс)")
            if st.button("Изменить"):
                if not appointment_datetime:
                    st.warning("Заполните все поля")
                elif not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', appointment_datetime):
                    st.warning("Неверный формат даты и времени записи")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL update_appointment_date(:appoint_id, :appoint_date);'''
                            connection.execute(text(sql_call_procedure), {
                                "appoint_id": appointment_id,
                                "appoint_date": appointment_datetime
                            })
                            connection.commit()
                        st.success(f"Запись перенесена на {appointment_datetime}!")
                    
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "Запись не найдена" in str(error):
                            st.warning("Запись не найдена")
                        else:
                            st.error("Ошибка при изменении даты записи: " + str(error))

    elif tab == "Больничный лист":
        st.subheader("Больничный лист")
        action = st.selectbox("Выберите действие с больничным листом", ["Поиск больничного листа", "Добавление больничного листа", "Продление больничного листа", "Удаление больничного листа"])
        
        if action == "Поиск больничного листа":
            snils_search = st.text_input("Введите СНИЛС пациента")
            if st.button("Поиск"):
                if not snils_search:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', snils_search):
                    st.warning("Неверный формат СНИЛС")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' SELECT * FROM get_sickleave(:snils_pat);'''
                            result = connection.execute(text(sql_call_procedure), {
                                "snils_pat": snils_search
                            })
                            sickleave_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                            if not sickleave_table.empty:
                                st.dataframe(sickleave_table)
                            else:
                                st.write(f"Больничный лист у пациента со снилсом {snils_search} не найден.")
                            connection.commit()
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        else:
                            st.error("Ошибка при получении больничного листа: " + str(error))

        elif action == "Добавление больничного листа":
            snils_add = st.text_input("Введите СНИЛС пациента")
            start_date = st.date_input("Дата начала больничного")
            end_date = st.date_input("Дата окончания больничного")
            if st.button("Добавить больничный лист"):
                if not snils_add:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', snils_add):
                    st.warning("Неверный формат СНИЛС")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL add_sickleave(:snils_id, :st_date, :end_date);'''
                            connection.execute(text(sql_call_procedure), {
                                "snils_id": snils_add,
                                "st_date": start_date,
                                "end_date": end_date
                            })
                            connection.commit()
                        st.success(f"Больничный лист с {start_date} по {end_date} добавлен!")
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "Больничный лист не найден" in str(error):
                            st.warning(f"Больничный лист не найден!")
                        elif 'нарушает ограничение-проверку "begin_end_time_check"' in str(error):
                            st.warning("Дата начала больничного листа должна быть меньше даты его окончания.")
                        elif 'нарушает ограничение внешнего ключа "sickleave_snils_fkey"' in str(error):
                            st.warning("Такого пациента нет в базе.")
                        elif 'повторяющееся значение ключа нарушает ограничение уникальности "sickleave_snils_key"':
                            st.warning("У пациента уже есть больничный лист")
                        else:
                            st.error("Ошибка при добавлении больничного листа: " + str(error))

        elif action == "Продление больничного листа":
            snils_extend = st.text_input("Введите СНИЛС пациента")
            new_end_date = st.date_input("Новая дата окончания больничного")
            if st.button("Продлить больничный лист"):
                if not snils_extend:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', snils_extend):
                    st.warning("Неверный формат СНИЛС")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL update_sickleave_end_date(:snils_ser, :new_date);'''
                            connection.execute(text(sql_call_procedure), {
                                "snils_ser": snils_extend,
                                "new_date": new_end_date
                            })
                            connection.commit()
                        st.success(f"Больничный лист для пациента с СНИЛС {snils_extend} продлен до {new_end_date}.")
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "Больничный лист не найден" in str(error):
                            st.warning(f"Больничный лист не найден!")
                        elif 'нарушает ограничение-проверку "begin_end_time_check"':
                            st.warning("Дата начала больничного листа должна быть меньше даты его окончания.")
                        else:
                            st.error("Ошибка при продлении больничного листа: " + str(error))                    

        elif action == "Удаление больничного листа":
            snils_delete = st.text_input("Введите СНИЛС пациента")
            if st.button("Удалить больничный лист"):
                if not snils_delete:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', snils_delete):
                    st.warning("Неверный формат СНИЛС")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' CALL delete_sickleave(:snils_id);'''
                            connection.execute(text(sql_call_procedure), {
                                "snils_id": snils_delete,
                            })
                            connection.commit()
                        st.success(f"Больничный лист удален!")
                    except SQLAlchemyError as error:
                        if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        elif "Больничный лист не найден" in str(error):
                            st.warning(f"Больничный лист не найден!")
                        else:
                            st.error("Ошибка при удалении больничного листа: " + str(error))

    elif tab == "Добавить запись":
        st.subheader("Добавить запись")
        doctor_id = st.number_input("Введите ID врача", min_value=1)
        patient_snils = st.text_input("Введите СНИЛС пациента")
        appointment_datetime = st.text_input("Введите дату и время записи (гггг-мм-дд чч:мм:сс)")
        
        if st.button("Добавить запись"):
            if not doctor_id or not patient_snils or not appointment_datetime:
                st.warning("Заполните все поля!")
            elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', patient_snils):
                st.warning("Неверный формат СНИЛС")
            elif not re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', appointment_datetime):
                st.warning("Неверный формат даты и времени записи")
            else:
                try:
                    with st.session_state.engine.connect() as connection:
                        sql_call_procedure = ''' CALL add_appointment(:doc_id, :pat_snils, :appointment_date);'''
                        connection.execute(text(sql_call_procedure), {
                            "doc_id": doctor_id,
                            "pat_snils": patient_snils,
                            "appointment_date": appointment_datetime
                        })
                        connection.commit()
                    st.success(f"Пациент записан на {appointment_datetime}!")
                except SQLAlchemyError as error:
                    if "Процедура с данными именем и типами аргументов не найдена" in str(error):
                        st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                    elif 'нарушает ограничение внешнего ключа "appointment_id_doctor_fkey"' in str(error):
                        st.warning("Такого врача в базе нет!")
                    elif 'нарушает ограничение внешнего ключа "appointment_snils_patient_fkey"' in str(error):
                        st.warning("Такого пациента в базе нет!")
                    else:
                        st.error("Ошибка при добавлении пациента: " + str(error))
        
    elif tab == "Поиск пациента":
        st.subheader("Поиск пациента")
        action = st.selectbox("Выберите способ поиска", ["Поиск по СНИЛС", "Поиск по ФИО и дате рождения"])
        if action == "Поиск по СНИЛС":
            snils_search = st.text_input("Введите СНИЛС пациента")
            if st.button("Поиск"):
                if not snils_search:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^\d{3}-\d{3}-\d{3} \d{2}$', snils_search):
                    st.warning("Неверный формат СНИЛС")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' SELECT * FROM get_patient(:snils_pat);'''
                            result = connection.execute(text(sql_call_procedure), {
                                "snils_pat": snils_search
                            })
                            patient_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                            if not patient_table.empty:
                                st.dataframe(patient_table)
                            else:
                                st.write(f"Пациент со снилсом {snils_search} не найдены.")
                            connection.commit()
                    except SQLAlchemyError as error:
                        if "Функция с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        else:
                            st.error("Ошибка при получении списка пациентов: " + str(error))
        
        elif action == "Поиск по ФИО и дате рождения":
            pat_surname = st.text_input("Введите фамилию пациента")
            pat_name = st.text_input("Введите имя пациента")
            pat_patronymic = st.text_input("Введите отчество пациента")
            pat_birth = st.date_input("Введите дату рождения пациента")
            if st.button("Поиск"):
                if not pat_name or not pat_surname or not pat_patronymic or not pat_birth:
                    st.warning("Заполните все поля!")
                elif not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_name) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_surname) or not re.match(r'^[а-яА-ЯёЁa-zA-Z\s-]+$', pat_patronymic):
                    st.warning("Поля ФИО пациента должны содержать только буквы русского или английского алфавита")
                else:
                    try:
                        with st.session_state.engine.connect() as connection:
                            sql_call_procedure = ''' SELECT * FROM get_patient(:surname, :name, :patronymic, :birth);'''
                            result = connection.execute(text(sql_call_procedure), {
                                "surname": pat_surname,
                                "name": pat_name,
                                "patronymic": pat_patronymic,
                                "birth": pat_birth
                            })
                            patient_table = pd.DataFrame(result.fetchall(), columns=result.keys())
                            if not patient_table.empty:
                                st.dataframe(patient_table)
                            else:
                                st.write(f"Пациент с этими данными не найден.")
                            connection.commit()
                    except SQLAlchemyError as error:
                        if "Функция с данными именем и типами аргументов не найдена" in str(error):
                            st.warning("База данных была ранее удалена. Для повторной инициализации - запустите приложение заново")
                        else:
                            st.error("Ошибка при получении списка врачей: " + str(error))
    
    if st.sidebar.button("Выйти"):
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.engine = "default"
        st.experimental_rerun()


def main():
    if 'locked' not in st.session_state:
        st.session_state.locked = False

    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False
        st.session_state.user_role = None
        st.session_state.engine = None
    
    if st.session_state.engine is None:
        try:
            st.session_state.engine = create_engine('postgresql://initializator:init@localhost:5432/postgres')
            with st.session_state.engine.connect() as connection:
                
                db_name = "clinic"
                                
                result = connection.execute(text("SELECT check_database_exists(:db_name)"), {"db_name": db_name}).fetchone()

                if result[0] == 'NO':  # Если база данных не существует
                    connection.execute(text("CALL please_create_db('clinic')"))
                    connection.commit()
                    connection.execute(text("CALL install_dblink_in_db('clinic')"))
                    connection.commit()
                    connection.execute(text("CALL init_tables('clinic')"))
                    connection.commit()
                    print("База данных создана успешно")
                else:
                    print("База данных уже существует")
        
        except SQLAlchemyError as error:
            st.error(f"Ошибка при работе с PostgreSQL: {error}")

    if not st.session_state.logged_in:
        login = st.text_input("Логин")
        password = st.text_input("Пароль", type="password")
        
        if st.button("Войти"):
            if login == "admin" and password == "12345":
                st.session_state.logged_in = True
                st.session_state.user_role = "admin"
                st.sidebar.write(f"Вы вошли как: **Администратор**")
                st.experimental_rerun()
            elif login == "regist" and password == "123":
                st.session_state.logged_in = True
                st.session_state.user_role = "registrar"
                st.sidebar.write(f"Вы вошли как: **Регистратура**")
                st.experimental_rerun()
            elif login == "doctor" and password == "111":
                st.session_state.logged_in = True
                st.session_state.user_role = "doc"
                st.sidebar.write(f"Вы вошли как: **Врач**")
                st.experimental_rerun()
            else:
                st.error("Неверный логин или пароль")
    else:
        if st.session_state.user_role == "admin":
            admin_tab()
        elif st.session_state.user_role == "registrar":
            registrar_tab()
        elif st.session_state.user_role == "doc":
            doc_tab()

if __name__ == "__main__":
    main()
