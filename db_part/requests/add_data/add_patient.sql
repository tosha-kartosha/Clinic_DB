CREATE OR REPLACE PROCEDURE add_patient(
    new_SNILS VARCHAR(14),
    new_surname VARCHAR(35),
    new_name VARCHAR(30),
    new_patronymic VARCHAR(35),
    new_birth_date DATE,
    new_address TEXT,
    new_medical_consent VARCHAR(3)
)
AS $$
BEGIN
    INSERT INTO patient (SNILS, surname, name, patronymic, birth_date, address, medical_consent)
    VALUES (new_SNILS, new_surname, new_name, new_patronymic, new_birth_date, new_address, new_medical_consent);
    
    RAISE NOTICE 'Пациент "%" был успешно добавлен в базу.', new_surname || ' ' || new_name || ' ' || new_patronymic;
END;
$$ LANGUAGE plpgsql;