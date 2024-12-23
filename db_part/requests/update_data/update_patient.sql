-- изменение согласия на мед вмешательнство
CREATE OR REPLACE PROCEDURE update_patient_med(
    p_SNILS VARCHAR(14),
    new_medical_consent VARCHAR(3)
)
AS $$
BEGIN
    UPDATE patient
    SET medical_consent = new_medical_consent
    WHERE SNILS = p_SNILS;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Пациент не найден';
    END IF;
    RAISE NOTICE 'Мед. вмешательство изменено на %.', new_medical_consent;
END;
$$ LANGUAGE plpgsql;

-- изменение ФИО пациента
CREATE OR REPLACE PROCEDURE update_patient_med(
    p_SNILS VARCHAR(14),
    new_surname VARCHAR(20),
    new_name VARCHAR(30),
    new_patronymic VARCHAR(35)
)
AS $$
BEGIN
    UPDATE patient
    SET surname = new_surname,
        name = new_name,
        patronymic = new_patronymic
    WHERE SNILS = p_SNILS;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Пациент не найден';
    END IF;
    RAISE NOTICE 'ФИО изменено на % % %.', new_surname, new_name, new_patronymic;
END;
$$ LANGUAGE plpgsql;

-- изменение адреса пациента
CREATE OR REPLACE PROCEDURE update_patient_med(
    p_SNILS VARCHAR(14),
    new_address text
)
AS $$
BEGIN
    UPDATE patient
    SET address = new_address
    WHERE SNILS = p_SNILS;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Пациент не найден';
    END IF;
    RAISE NOTICE 'Адрес изменен на %.', new_address;
END;
$$ LANGUAGE plpgsql;