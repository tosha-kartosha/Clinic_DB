-- SELECT
-- (d.surname || ' ' || d.name || ' ' || d.patronymic) AS "ФИО врача",
-- (p.surname || ' ' || p.name || ' ' || p.patronymic) AS "ФИО пациента",
-- p.birth_date AS "Д/Р пациента",
-- a.record_date AS "Дата приема",
-- a.ICD AS "Код заболевания",
-- p.medical_consent AS "Согл. на мед. вмешательство"
-- FROM appointment a
-- JOIN doctor d ON a.id_doctor = d.id_doctor
-- JOIN patient p ON a.id_patient = p.id_patient;

-- Вывод всех записей
CREATE OR REPLACE FUNCTION get_schedule() 
RETURNS TABLE (
    "ID записи" INTEGER,
    "Специальность" VARCHAR(20),
    "ФИО врача" text,
    "ФИО пациента" text,
    "Д/Р пациента" DATE,
    "Дата приема" TIMESTAMP,
    "Код заболевания" VARCHAR(5),  
    "Согл. на мед. вмешательство" VARCHAR(3)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id_appointment,
        d.specialization,
        (d.surname || ' ' || d.name || ' ' || d.patronymic),
        (p.surname || ' ' || p.name || ' ' || p.patronymic),
        p.birth_date,
        a.record_date,
        a.ICD,
        p.medical_consent
    FROM appointment a
    JOIN doctor d ON a.id_doctor = d.id_doctor
    JOIN patient p ON a.SNILS_patient = p.SNILS
    ORDER BY a.record_date;
END;
$$ LANGUAGE plpgsql;


-- Поиск записей по ФИО врача
CREATE OR REPLACE FUNCTION get_schedule(doc_surname VARCHAR(35), doc_name VARCHAR(30), doc_patronymic VARCHAR(35)) 
RETURNS TABLE (
    "ID записи" INTEGER,
    "Специальность" VARCHAR(20),
    "ФИО врача" text,
    "ФИО пациента" text,
    "Д/Р пациента" DATE,
    "Дата приема" TIMESTAMP,
    "Код заболевания" VARCHAR(5),  
    "Согл. на мед. вмешательство" VARCHAR(3)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id_appointment,
        d.specialization,
        (d.surname || ' ' || d.name || ' ' || d.patronymic),
        (p.surname || ' ' || p.name || ' ' || p.patronymic),
        p.birth_date,
        a.record_date,
        a.ICD,
        p.medical_consent 
    FROM appointment a
    JOIN doctor d ON a.id_doctor = d.id_doctor
    JOIN patient p ON a.SNILS_patient = p.SNILS
    WHERE d.surname = doc_surname AND d.name = doc_name AND d.patronymic = doc_patronymic
    ORDER BY a.record_date;
END;
$$ LANGUAGE plpgsql;

-- Поиск записей по ФИО конкретного пациента и его дате рождения
CREATE OR REPLACE FUNCTION get_schedule(pat_surname VARCHAR(35), pat_name VARCHAR(30), pat_patronymic VARCHAR(35), pat_birth_date DATE) 
RETURNS TABLE (
    "ID записи" INTEGER,
    "Специальность" VARCHAR(20),
    "ФИО врача" text,
    "ФИО пациента" text,
    "Д/Р пациента" DATE,
    "Дата приема" TIMESTAMP,
    "Код заболевания" VARCHAR(5),  
    "Согл. на мед. вмешательство" VARCHAR(3)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id_appointment,
        d.specialization,
        (d.surname || ' ' || d.name || ' ' || d.patronymic),
        (p.surname || ' ' || p.name || ' ' || p.patronymic),
        p.birth_date,
        a.record_date,
        a.ICD,
        p.medical_consent
    FROM appointment a
    JOIN doctor d ON a.id_doctor = d.id_doctor
    JOIN patient p ON a.SNILS_patient = p.SNILS
    WHERE p.surname = pat_surname AND p.name = pat_name AND p.patronymic = pat_patronymic AND p.birth_date = pat_birth_date
    ORDER BY a.record_date;
END;
$$ LANGUAGE plpgsql;

-- Поиск записей по специальности врача
CREATE OR REPLACE FUNCTION get_schedule(doctor_spec VARCHAR(20)) 
RETURNS TABLE (
    "ID записи" INTEGER,
    "Специальность" VARCHAR(20),
    "ФИО врача" text,
    "ФИО пациента" text,
    "Д/Р пациента" DATE,
    "Дата приема" TIMESTAMP,
    "Код заболевания" VARCHAR(5),  
    "Согл. на мед. вмешательство"  VARCHAR(3)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        a.id_appointment,
        d.specialization,
        (d.surname || ' ' || d.name || ' ' || d.patronymic),
        (p.surname || ' ' || p.name || ' ' || p.patronymic),
        p.birth_date,
        a.record_date,
        a.ICD,
        p.medical_consent
    FROM appointment a
    JOIN doctor d ON a.id_doctor = d.id_doctor
    JOIN patient p ON a.SNILS_patient = p.SNILS
    WHERE d.specialization = doctor_spec
    ORDER BY a.record_date;
END;
$$ LANGUAGE plpgsql;