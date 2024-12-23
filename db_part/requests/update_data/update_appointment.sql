-- добавление врачом МКБ заболевания
CREATE OR REPLACE PROCEDURE update_appointment_doctor(
    a_id INTEGER,
    new_ICD VARCHAR(5)
)
AS $$
BEGIN
    UPDATE appointment
    SET ICD = new_ICD
    WHERE id_appointment = a_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Запись не найдена';
    END IF;
    RAISE NOTICE 'Запись успешно изменена.';
END;
$$ LANGUAGE plpgsql;

-- изменение даты записи
CREATE OR REPLACE PROCEDURE update_appointment_date(
    a_id INTEGER,
    new_record_date TIMESTAMP
)
AS $$
BEGIN
    UPDATE appointment
    SET record_date = new_record_date
    WHERE id_appointment = a_id;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Запись не найдена';
    END IF;
    RAISE NOTICE 'Запись успешно изменена.';
END;
$$ LANGUAGE plpgsql;