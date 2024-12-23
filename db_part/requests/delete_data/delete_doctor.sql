-- удаление врача по ID
CREATE OR REPLACE PROCEDURE delete_doctor(
    delete_id_doctor INTEGER
)
AS $$
BEGIN
    DELETE FROM doctor where id_doctor = delete_id_doctor;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Доктор с ID "%" не существует в базе', delete_id_doctor;
    END IF;

    RAISE NOTICE 'Все записи к врачу с ID "%" были удалены.', delete_id_doctor;
END;
$$ LANGUAGE plpgsql;


-- удаление врача по ФИО и специальности
CREATE OR REPLACE PROCEDURE delete_doctor(
    doc_surname VARCHAR(35),
    doc_name VARCHAR(30),
    doc_patronymic VARCHAR(35),
    doctor_spec VARCHAR(20)
)
AS $$
BEGIN
    DELETE FROM doctor where surname = doc_surname AND name = doc_name AND patronymic = doc_patronymic AND specialization = doctor_spec;
    IF NOT FOUND THEN
        RAISE EXCEPTION '% % % % не существует в базе', doctor_spec, doc_surname, doc_name, doc_patronymic;
    END IF;

    RAISE NOTICE 'Все записи к врачу % % % по специальности "%" были удалены.', doc_surname, doc_name, doc_patronymic, doctor_spec;
END;
$$ LANGUAGE plpgsql;

-- удаление врачей по специальности
CREATE OR REPLACE PROCEDURE delete_doctor_on_spec(
    doctor_spec VARCHAR(20)
)
AS $proc2$
BEGIN
    DELETE FROM doctor WHERE specialization = doctor_spec;
    IF NOT FOUND THEN
        RAISE EXCEPTION '% не существует в базе', doc_patronymic;
    END IF;

    RAISE NOTICE 'Все врачи по специальности % и записи к ним были удалены.', doctor_spec;
END;
$proc2$ LANGUAGE plpgsql;

-- удаление всех врачей из базы

CREATE OR REPLACE PROCEDURE delete_all_doctor()
AS $$
BEGIN
    DELETE FROM doctor;
    RAISE NOTICE 'Все врачи удалены из базы';
END;
$$ LANGUAGE plpgsql;
