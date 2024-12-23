-- изменение специальности врача
CREATE OR REPLACE PROCEDURE update_doctor_spec(
    d_id_doctor INTEGER,
    new_specialization VARCHAR(20)
)
AS $$
BEGIN
    UPDATE doctor
    SET specialization = new_specialization
    WHERE id_doctor = d_id_doctor;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Врач не найден';
    END IF;
    RAISE NOTICE 'Специальность врача изменена на %.', new_specialization;
END;
$$ LANGUAGE plpgsql;

-- изменение ФИО врача
CREATE OR REPLACE PROCEDURE update_doctor_fio(
    d_id_doctor INTEGER,
    new_surname VARCHAR(20),
    new_name VARCHAR(30),
    new_patronymic VARCHAR(35)
)
AS $$
BEGIN
    UPDATE doctor
    SET surname = new_surname,
        name = new_name,
        patronymic = new_patronymic
    WHERE id_doctor = d_id_doctor;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Врач не найден';
    END IF;
    RAISE NOTICE 'ФИО врача изменено на % % %.', new_surname, new_name, new_patronymic;
END;
$$ LANGUAGE plpgsql;