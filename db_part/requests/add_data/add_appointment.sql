-- добавление записи от врача
CREATE OR REPLACE PROCEDURE add_appointment_doctor(
    new_id_doctor INTEGER,
    new_SNILS_patient VARCHAR(14),
    new_record_date TIMESTAMP,
    new_ICD VARCHAR(5)
)
AS $$
BEGIN
    INSERT INTO appointment (id_doctor, SNILS_patient, record_date, ICD)
    VALUES (new_id_doctor, new_SNILS_patient, new_record_date, new_ICD);
    RAISE NOTICE 'Запись успешно добавлена.';
END;
$$ LANGUAGE plpgsql;

-- добавление записи из регистратуры
CREATE OR REPLACE PROCEDURE add_appointment_regist(
    new_id_doctor INTEGER,
    new_SNILS_patient VARCHAR(14),
    new_record_date TIMESTAMP
)
AS $$
BEGIN
    INSERT INTO appointment (id_doctor, SNILS_patient, record_date)
    VALUES (new_id_doctor, new_SNILS_patient, new_record_date);
    RAISE NOTICE 'Запись успешно добавлена.';
END;
$$ LANGUAGE plpgsql;