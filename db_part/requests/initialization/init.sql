CREATE USER initializator WITH SUPERUSER PASSWORD 'init'; -- системный для инициализации, т.к. CREATE EXTENSION dblink может только superuser 
CREATE USER adminchik WITH PASSWORD '12345'; -- администратор
CREATE USER staff with password '123'; -- врач или регистратура

CREATE OR REPLACE FUNCTION check_database_exists(db_name TEXT)
RETURNS TEXT
LANGUAGE plpgsql
AS $$
DECLARE
    db_exists BOOLEAN;
BEGIN
    SELECT EXISTS (SELECT 1 FROM pg_database WHERE datname = db_name) INTO db_exists;

    IF db_exists THEN
        RETURN 'YES';
    ELSE
        RETURN 'NO';
    END IF;
END;
$$;

CREATE OR REPLACE PROCEDURE please_create_db(dbname text) -- function to create bd
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_database WHERE datname = dbname) THEN
        RAISE NOTICE 'Database already exists'; 
    ELSE
        PERFORM dblink_exec('dbname=postgres user=initializator password=init', 'CREATE DATABASE ' || quote_ident(dbname));
        PERFORM dblink_exec('dbname=' || quote_ident(dbname) || ' user=initializator password=init', 'ALTER DATABASE ' || quote_ident(dbname) || ' OWNER TO adminchik');
    END IF;
END
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE install_dblink_in_db(target_db text) -- function to CREATE EXTENSION dblink in new bd to init function from db postgres to new bd
AS $$
BEGIN
    PERFORM dblink_exec('dbname=' || target_db || ' user=initializator password=init', 'CREATE EXTENSION IF NOT EXISTS dblink;');
END;
$$ LANGUAGE plpgsql;

CREATE OR REPLACE PROCEDURE drop_clinic_db() -- отдельно для удаления в postgres (нельзя удалить бд, находясь в ней, поэтому перключаемся в бд postgres и уже там удаляем)
AS $$
BEGIN
    IF EXISTS (SELECT 1 FROM pg_database WHERE datname = 'clinic') THEN
        PERFORM dblink_exec('dbname=postgres user=adminchik password=12345', 'DROP DATABASE clinic');
        RAISE NOTICE 'БД была удалена.';
    ELSE
        RAISE NOTICE 'Такой БД не существует.';
    END IF;
END
$$ LANGUAGE plpgsql;

CREATE OR replace PROCEDURE init_tables(target_db text) -- это создает схему, в которой будет весь функционал
AS $$
declare
p_sql text;
BEGIN 
p_sql:= format('-- tables
    CREATE TABLE IF NOT EXISTS doctor (
    id_doctor SERIAL PRIMARY KEY,
    surname VARCHAR(35) NOT NULL,
    name VARCHAR(30) NOT NULL,
    patronymic VARCHAR(35) NOT NULL,
    specialization VARCHAR(20) NOT NULL CHECK (specialization IN (''Терапевт'', ''Гастроэнтеролог'', ''Офтальмолог'', ''Окулист'', ''Невролог'', ''Отоларинголог'', ''Хирург'', ''Психиатр'')),
    appointment_count INT DEFAULT 0,
    UNIQUE (surname, name, patronymic, specialization)
    );

    -- index
    CREATE INDEX IF NOT EXISTS spec ON doctor (specialization);
    
    CREATE TABLE IF NOT EXISTS patient (
    SNILS VARCHAR(14) PRIMARY KEY,
    surname VARCHAR(35) NOT NULL,
    name VARCHAR(30) NOT NULL,
    patronymic VARCHAR(35) NOT NULL,
    birth_date DATE NOT NULL, 
    address text
    );

    CREATE TABLE IF NOT EXISTS sickleave (
    id_sheet SERIAL PRIMARY KEY,
    SNILS VARCHAR(14) UNIQUE,
    begin_time DATE NOT NULL,
    end_time DATE NOT NULL,
    CONSTRAINT begin_end_time_check CHECK (begin_time < end_time),
    FOREIGN KEY (SNILS) REFERENCES patient(SNILS) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS appointment (
    id_appointment SERIAL PRIMARY KEY,
    id_doctor INTEGER NOT NULL,
    SNILS_patient VARCHAR(14) NOT NULL,
    record_date TIMESTAMP NOT NULL,
    ICD VARCHAR(5) DEFAULT NULL CHECK (ICD IS NULL OR ICD ~ ''^[A-Z][0-9]{2}\.[0-9]$''),
    UNIQUE (id_doctor, record_date),
    UNIQUE(SNILS_patient, record_date),
    FOREIGN KEY (id_doctor) REFERENCES doctor(id_doctor) ON DELETE CASCADE,
    FOREIGN KEY (SNILS_patient) REFERENCES patient(SNILS) ON DELETE CASCADE
    );

    -- добавление врача
    CREATE OR REPLACE PROCEDURE add_doctor(
    new_surname VARCHAR(35),
    new_name VARCHAR(30),
    new_patronymic VARCHAR(35),
    new_specialization VARCHAR(20)
    )
    AS $proc2$
    BEGIN
        INSERT INTO doctor (surname, name, patronymic, specialization)
        VALUES (new_surname, new_name, new_patronymic, new_specialization);
        RAISE NOTICE ''Доктор "%%" был успешно добавлен в базу.'', new_surname || '' '' || new_name || '' '' || new_patronymic;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- добавление пациента
    CREATE OR REPLACE PROCEDURE add_patient(
    new_SNILS VARCHAR(14),
    new_surname VARCHAR(35),
    new_name VARCHAR(30),
    new_patronymic VARCHAR(35),
    new_birth_date DATE,
    new_address TEXT
    )
    AS $proc2$
    BEGIN
        INSERT INTO patient (SNILS, surname, name, patronymic, birth_date, address)
        VALUES (new_SNILS, new_surname, new_name, new_patronymic, new_birth_date, new_address);
        
        RAISE NOTICE ''Пациент "%%" был успешно добавлен в базу.'', new_surname || '' '' || new_name || '' '' || new_patronymic;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- добавление больничного листа
    CREATE OR REPLACE PROCEDURE add_sickleave(
    new_SNILS VARCHAR(14),
    new_begin_time DATE,
    new_end_time DATE
    )
    AS $proc2$
    BEGIN
        INSERT INTO sickleave (SNILS, begin_time, end_time)
        VALUES (new_SNILS, new_begin_time, new_end_time);
        
        RAISE NOTICE ''Больничный лист был успешно добавлен в базу.'';
    END;
    $proc2$ LANGUAGE plpgsql;

    -- добавление записи
    CREATE OR REPLACE PROCEDURE add_appointment(
    new_id_doctor INTEGER,
    new_SNILS_patient VARCHAR(14),
    new_record_date TIMESTAMP
    )
    AS $proc2$
    BEGIN
        INSERT INTO appointment (id_doctor, SNILS_patient, record_date)
        VALUES (new_id_doctor, new_SNILS_patient, new_record_date);
        RAISE NOTICE ''Запись успешно добавлена.'';
    END;
    $proc2$ LANGUAGE plpgsql;

    -- очистка все таблиц
    CREATE OR REPLACE PROCEDURE delete_all()
    AS $proc2$
    BEGIN
        DELETE FROM appointment;
        DELETE FROM sickleave;
        DELETE FROM doctor;
        DELETE FROM patient;
        RAISE NOTICE ''Информация из всех таблиц БД была очищена'';
    END;
    $proc2$ LANGUAGE plpgsql;

    -- удаление записи по ID
    CREATE OR REPLACE PROCEDURE delete_appointment(
    delete_id_appointment INTEGER
    )
    AS $proc2$
    BEGIN
        DELETE FROM appointment where id_appointment = delete_id_appointment;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''Записи с ID "%%" не существует в базе'', delete_id_appointment;
        END IF;

        RAISE NOTICE ''Запись с ID "%%" была удалена.'', delete_id_appointment;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- удаление врача по ID
    CREATE OR REPLACE PROCEDURE delete_doctor(
    delete_id_doctor INTEGER
    )
    AS $proc2$
    BEGIN
        DELETE FROM doctor where id_doctor = delete_id_doctor;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''Доктор с ID "%%" не существует в базе'', delete_id_doctor;
        END IF;

        RAISE NOTICE ''Врач с ID "%%" и все записи к нему были удалены.'', delete_id_doctor;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- удаление врача по ФИО и специальности
    CREATE OR REPLACE PROCEDURE delete_doctor(
        doc_surname VARCHAR(35),
        doc_name VARCHAR(30),
        doc_patronymic VARCHAR(35),
        doctor_spec VARCHAR(20)
    )
    AS $proc2$
    BEGIN
        DELETE FROM doctor where surname = doc_surname AND name = doc_name AND patronymic = doc_patronymic AND specialization = doctor_spec;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''%% %% %% %% не существует в базе'', doctor_spec, doc_surname, doc_name, doc_patronymic;
        END IF;

        RAISE NOTICE ''Врач %% %% %% по специальности "%%" и все записи к нему были удалены.'', doc_surname, doc_name, doc_patronymic, doctor_spec;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- удаление врачей по специальности
    CREATE OR REPLACE PROCEDURE delete_doctor_on_spec(
        doctor_spec VARCHAR(20)
    )
    AS $proc2$
    BEGIN
        DELETE FROM doctor WHERE specialization = doctor_spec;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''%% не существует в базе'', doctor_spec;
        END IF;

        RAISE NOTICE ''Все врачи по специальности %% и записи к ним были удалены.'', doctor_spec;
    END;
    $proc2$ LANGUAGE plpgsql;


    -- удаление всех врачей из базы
    CREATE OR REPLACE PROCEDURE delete_all_doctor()
    AS $proc2$
    BEGIN
        DELETE FROM doctor;
        RAISE NOTICE ''Все врачи удалены из базы'';
    END;
    $proc2$ LANGUAGE plpgsql;

    -- удаление больничного листа по снилсу
    CREATE OR REPLACE PROCEDURE delete_sickleave(
        delete_snils VARCHAR(14)
    )
    AS $proc2$
    BEGIN
        DELETE FROM sickleave WHERE delete_snils = SNILS;

        IF NOT FOUND THEN
            RAISE EXCEPTION ''Больничный лист не найден'';
        END IF;

        RAISE NOTICE ''Больничный лист удален'';
    END;
    $proc2$ LANGUAGE plpgsql;

    -- добавление врачом МКБ заболевания
    CREATE OR REPLACE PROCEDURE update_appointment_icd(
        a_id INTEGER,
        new_ICD VARCHAR(5)
    )
    AS $proc2$
    BEGIN
        UPDATE appointment
        SET ICD = new_ICD
        WHERE id_appointment = a_id;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''Запись не найдена'';
        END IF;
        RAISE NOTICE ''Запись успешно изменена.'';
    END;
    $proc2$ LANGUAGE plpgsql;

    -- изменение даты записи
    CREATE OR REPLACE PROCEDURE update_appointment_date(
        a_id INTEGER,
        new_record_date TIMESTAMP
    )
    AS $proc2$
    BEGIN
        UPDATE appointment
        SET record_date = new_record_date
        WHERE id_appointment = a_id;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''Запись не найдена'';
        END IF;
        RAISE NOTICE ''Запись успешно изменена.'';
    END;
    $proc2$ LANGUAGE plpgsql;

    -- изменение специальности врача
    CREATE OR REPLACE PROCEDURE update_doctor_spec(
        d_id_doctor INTEGER,
        new_specialization VARCHAR(20)
    )
    AS $proc2$
    BEGIN
        UPDATE doctor
        SET specialization = new_specialization
        WHERE id_doctor = d_id_doctor;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''Врач не найден'';
        END IF;
        RAISE NOTICE ''Специальность врача изменена на %%.'', new_specialization;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- изменение ФИО врача
    CREATE OR REPLACE PROCEDURE update_doctor_fio(
        d_id_doctor INTEGER,
        new_surname VARCHAR(20),
        new_name VARCHAR(30),
        new_patronymic VARCHAR(35)
    )
    AS $proc2$
    BEGIN
        UPDATE doctor
        SET surname = new_surname,
            name = new_name,
            patronymic = new_patronymic
        WHERE id_doctor = d_id_doctor;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''Врач не найден'';
        END IF;
        RAISE NOTICE ''ФИО врача изменено на %% %% %%.'', new_surname, new_name, new_patronymic;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- изменение ФИО пациента
    CREATE OR REPLACE PROCEDURE update_patient_med(
        p_SNILS VARCHAR(14),
        new_surname VARCHAR(20),
        new_name VARCHAR(30),
        new_patronymic VARCHAR(35)
    )
    AS $proc2$
    BEGIN
        UPDATE patient
        SET surname = new_surname,
            name = new_name,
            patronymic = new_patronymic
        WHERE SNILS = p_SNILS;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''Пациент не найден'';
        END IF;
        RAISE NOTICE ''ФИО изменено на %% %% %%.'', new_surname, new_name, new_patronymic;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- изменение адреса пациента
    CREATE OR REPLACE PROCEDURE update_patient_med_address(
        p_SNILS VARCHAR(14),
        new_address text
    )
    AS $proc2$
    BEGIN
        UPDATE patient
        SET address = new_address
        WHERE SNILS = p_SNILS;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''Пациент не найден'';
        END IF;
        RAISE NOTICE ''Адрес изменен на %%.'', new_address;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- продление больничного листа
    CREATE OR REPLACE PROCEDURE update_sickleave_end_date(
        p_SNILS VARCHAR(14),
        new_end_time DATE
    )
    AS $proc2$
    BEGIN
        UPDATE sickleave
        SET end_time = new_end_time
        WHERE SNILS = p_SNILS;
        IF NOT FOUND THEN
            RAISE EXCEPTION ''Больничный лист не найден'';
        END IF;
        RAISE NOTICE ''Больничный лист продлен до %%.'', new_end_time;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- Вывод всех записей
    CREATE OR REPLACE FUNCTION get_schedule() 
    RETURNS TABLE (
        "ID записи" INTEGER,
        "Специальность" VARCHAR(20),
        "ФИО врача" text,
        "ФИО пациента" text,
        "Д/Р пациента" DATE,
        "Дата приема" TIMESTAMP,
        "Код заболевания" VARCHAR(5)
    )
    AS $proc2$
    BEGIN
        RETURN QUERY
        SELECT
            a.id_appointment,
            d.specialization,
            (d.surname || '' '' || d.name || '' '' || d.patronymic),
            (p.surname || '' '' || p.name || '' '' || p.patronymic),
            p.birth_date,
            a.record_date,
            a.ICD
        FROM appointment a
        JOIN doctor d ON a.id_doctor = d.id_doctor
        JOIN patient p ON a.SNILS_patient = p.SNILS
        ORDER BY a.record_date;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- Поиск записей по ФИО врача
    CREATE OR REPLACE FUNCTION get_schedule(doc_surname VARCHAR(35), doc_name VARCHAR(30), doc_patronymic VARCHAR(35)) 
    RETURNS TABLE (
        "ID записи" INTEGER,
        "Специальность" VARCHAR(20),
        "ФИО врача" text,
        "ФИО пациента" text,
        "Д/Р пациента" DATE,
        "Дата приема" TIMESTAMP,
        "Код заболевания" VARCHAR(5)
    )
    AS $proc2$
    BEGIN
        RETURN QUERY
        SELECT
            a.id_appointment,
            d.specialization,
            (d.surname || '' '' || d.name || '' '' || d.patronymic),
            (p.surname || '' '' || p.name || '' '' || p.patronymic),
            p.birth_date,
            a.record_date,
            a.ICD
        FROM appointment a
        JOIN doctor d ON a.id_doctor = d.id_doctor
        JOIN patient p ON a.SNILS_patient = p.SNILS
        WHERE d.surname = doc_surname AND d.name = doc_name AND d.patronymic = doc_patronymic
        ORDER BY a.record_date;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- Поиск записей по специальности врача
    CREATE OR REPLACE FUNCTION get_schedule(doctor_spec VARCHAR(20)) 
    RETURNS TABLE (
        "ID записи" INTEGER,
        "Специальность" VARCHAR(20),
        "ФИО врача" text,
        "ФИО пациента" text,
        "Д/Р пациента" DATE,
        "Дата приема" TIMESTAMP,
        "Код заболевания" VARCHAR(5)
    )
    AS $proc2$
    BEGIN
        RETURN QUERY
        SELECT
            a.id_appointment,
            d.specialization,
            (d.surname || '' '' || d.name || '' '' || d.patronymic),
            (p.surname || '' '' || p.name || '' '' || p.patronymic),
            p.birth_date,
            a.record_date,
            a.ICD
        FROM appointment a
        JOIN doctor d ON a.id_doctor = d.id_doctor
        JOIN patient p ON a.SNILS_patient = p.SNILS
        WHERE d.specialization = doctor_spec
        ORDER BY a.record_date;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- получение статистики по врачам в поликлинике
    CREATE OR REPLACE FUNCTION get_doctor_statistic()
    RETURNS TABLE(
        "ФИО врача" text,
        "Должность врача" VARCHAR(20),
        "Количество записей" INT
    ) AS $proc2$
    BEGIN
        RETURN QUERY
        SELECT (surname || '' '' || name || '' '' || patronymic),
            specialization,
            appointment_count
        FROM doctor
        ORDER BY appointment_count DESC;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- Вывод всех врачей
    CREATE OR REPLACE FUNCTION get_doctor() 
    RETURNS TABLE (
        "ID врача" INTEGER,
        "ФИО врача" text,
        "Специальность" VARCHAR(20)
    )
    AS $proc2$
    BEGIN
        RETURN QUERY
        SELECT
            d.id_doctor, 
            (d.surname || '' '' || d.name || '' '' || d.patronymic),
            d.specialization
        FROM doctor d
        ORDER BY d.specialization;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- Поиск врачей по специальности
    CREATE OR REPLACE FUNCTION get_doctor(doctor_spec VARCHAR(20)) 
    RETURNS TABLE (
        "ID врача" INTEGER,
        "ФИО врача" text,
        "Специальность" VARCHAR(20)
    )
    AS $proc2$
    BEGIN
        RETURN QUERY
        SELECT
            d.id_doctor, 
            (d.surname || '' '' || d.name || '' '' || d.patronymic),
            d.specialization
        FROM doctor d
        WHERE d.specialization = doctor_spec
        ORDER BY d.specialization;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- Поиск врачей по ФИО врача
    CREATE OR REPLACE FUNCTION get_doctor(doc_surname VARCHAR(35), doc_name VARCHAR(30), doc_patronymic VARCHAR(35)) 
    RETURNS TABLE (
        "ID врача" INTEGER,
        "ФИО врача" text,
        "Специальность" VARCHAR(20)
    )
    AS $proc2$
    BEGIN
        RETURN QUERY
        SELECT
            d.id_doctor, 
            (d.surname || '' '' || d.name || '' '' || d.patronymic),
            d.specialization
        FROM doctor d
        WHERE d.surname = doc_surname AND d.name = doc_name AND d.patronymic = doc_patronymic
        ORDER BY d.specialization;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- Поиск пациента по ФИО конкретного пациента и его дате рождения
    CREATE OR REPLACE FUNCTION get_patient(pat_surname VARCHAR(35), pat_name VARCHAR(30), pat_patronymic VARCHAR(35), pat_birth_date DATE) 
    RETURNS TABLE (
        "СНИЛС" VARCHAR(14),
        "ФИО" text,
        "Д/Р пациента" DATE,
        "Адрес проживания" text
    )
    AS $proc2$
    BEGIN
        RETURN QUERY
        SELECT
            p.SNILS, 
            (p.surname || '' '' || p.name || '' '' || p.patronymic),
            p.birth_date,
            P.address
        FROM patient p
        WHERE p.surname = pat_surname AND p.name = pat_name AND p.patronymic = pat_patronymic AND p.birth_date = pat_birth_date
        ORDER BY p.SNILS;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- Поиск пациента по СНИЛС
    CREATE OR REPLACE FUNCTION get_patient(pat_SNILS VARCHAR(14)) 
    RETURNS TABLE (
        "СНИЛС" VARCHAR(14),
        "ФИО" text,
        "Д/Р пациента" DATE,
        "Адрес проживания" text
    )
    AS $proc2$
    BEGIN
        RETURN QUERY
        SELECT
            p.SNILS,
            (p.surname || '' '' || p.name || '' '' || p.patronymic),
            p.birth_date,
            P.address
        FROM patient p
        WHERE p.SNILS = pat_SNILS
        ORDER BY p.SNILS;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- Поиск больничного листа по снилсу пациента
    CREATE OR REPLACE FUNCTION get_sickleave(pat_SNILS VARCHAR(14)) 
    RETURNS TABLE (
        "Номер больничного листа" INTEGER,
        "ФИО" text,
        "Дата открытия" DATE,
        "Дата закрытии" DATE
    )
    AS $proc2$
    BEGIN
        RETURN QUERY
        SELECT
            s.id_sheet,
            (p.surname || '' '' || p.name || '' '' || p.patronymic),
            s.begin_time, s.end_time
        FROM sickleave s
        JOIN patient p ON s.SNILS = p.SNILS
        WHERE p.SNILS = pat_SNILS;
    END;
    $proc2$ LANGUAGE plpgsql;

    -- тригер на поле с кол-вом записей у врача
    CREATE OR REPLACE FUNCTION update_appointment_count()
    RETURNS TRIGGER AS $proc2$
    BEGIN
        IF TG_OP = ''INSERT'' THEN
            UPDATE doctor
            SET appointment_count = appointment_count + 1
            WHERE id_doctor = NEW.id_doctor;
        ELSIF TG_OP = ''DELETE'' THEN
            UPDATE doctor
            SET appointment_count = appointment_count - 1
            WHERE id_doctor = OLD.id_doctor;
        END IF;

        RETURN NEW;
    END;
    $proc2$ LANGUAGE plpgsql;

    CREATE TRIGGER after_add_new_appointment
    AFTER INSERT ON appointment
    FOR EACH ROW EXECUTE FUNCTION update_appointment_count();

    CREATE TRIGGER after_delete_appointment
    AFTER DELETE ON appointment
    FOR EACH ROW EXECUTE FUNCTION update_appointment_count();
    
    GRANT SELECT, INSERT, UPDATE, DELETE ON doctor to adminchik;
    GRANT USAGE, SELECT, UPDATE ON doctor_id_doctor_seq to adminchik;
    GRANT SELECT, DELETE ON appointment to adminchik;
    GRANT SELECT, DELETE ON patient to adminchik;
    GRANT SELECT, DELETE ON sickleave to adminchik;
    GRANT SELECT ON appointment_id_appointment_seq to adminchik;
    GRANT SELECT, INSERT, UPDATE, DELETE ON appointment to regist;
    GRANT USAGE, SELECT, UPDATE ON appointment_id_appointment_seq to regist;
    GRANT SELECT ON doctor_id_doctor_seq to regist;
    GRANT SELECT, UPDATE ON doctor to regist;
    GRANT SELECT, INSERT, UPDATE ON patient to regist;
    GRANT SELECT, INSERT, UPDATE, DELETE ON appointment to doc;
    GRANT USAGE, SELECT, UPDATE ON appointment_id_appointment_seq to doc;
    GRANT SELECT, UPDATE ON doctor to doc;
    GRANT SELECT ON patient to doc;
    GRANT SELECT, INSERT, UPDATE, DELETE ON sickleave to doc;
    GRANT USAGE, SELECT, UPDATE ON sickleave_id_sheet_seq to doc;');
perform dblink_exec('dbname=' || target_db || ' user=initializator password=init' , p_sql);
END;
$$ LANGUAGE plpgsql;

-- DO $$
-- BEGIN
--     PERFORM dblink_exec('dbname=database5 user=postgres password=Bambi3229', 'CREATE EXTENSION IF NOT EXISTS dblink;');
-- END $$;
