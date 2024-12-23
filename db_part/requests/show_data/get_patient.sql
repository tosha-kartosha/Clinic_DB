-- Поиск пациента по ФИО конкретного пациента и его дате рождения
CREATE OR REPLACE FUNCTION get_patient(pat_surname VARCHAR(35), pat_name VARCHAR(30), pat_patronymic VARCHAR(35), pat_birth_date DATE) 
RETURNS TABLE (
    "ID пациента" INTEGER,
    "ФИО" text,
    "Д/Р пациента" DATE,
    "СНИЛС" VARCHAR(14),
    "Адрес проживания" text,  
    "Согл. на мед. вмешательство"  VARCHAR(3)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id_patient, 
        (p.surname || ' ' || p.name || ' ' || p.patronymic),
        p.birth_date,
        p.SNILS,
        P.address,
        p.medical_consent
    FROM patient p
    WHERE p.surname = pat_surname AND p.name = pat_name AND p.patronymic = pat_patronymic AND p.birth_date = pat_birth_date
    ORDER BY p.id_patient;
END;
$$ LANGUAGE plpgsql;

-- Поиск пациента по СНИЛС
CREATE OR REPLACE FUNCTION get_patient(pat_SNILS VARCHAR(14)) 
RETURNS TABLE (
    "ID пациента" INTEGER,
    "ФИО" text,
    "Д/Р пациента" DATE,
    "СНИЛС" VARCHAR(14),
    "Адрес проживания" text,  
    "Согл. на мед. вмешательство"  VARCHAR(3)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        p.id_patient, 
        (p.surname || ' ' || p.name || ' ' || p.patronymic),
        p.birth_date,
        p.SNILS,
        P.address,
        p.medical_consent
    FROM patient p
    WHERE p.SNILS = pat_SNILS
    ORDER BY p.id_patient;
END;
$$ LANGUAGE plpgsql;