-- Вывод всех врачей
CREATE OR REPLACE FUNCTION get_doctor() 
RETURNS TABLE (
    "ID врача" INTEGER,
    "ФИО врача" text,
    "Специальность" VARCHAR(20)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id_doctor, 
        (d.surname || ' ' || d.name || ' ' || d.patronymic),
        d.specialization
    FROM doctor d
    ORDER BY d.specialization;
END;
$$ LANGUAGE plpgsql;


-- Поиск врачей по специальности
CREATE OR REPLACE FUNCTION get_doctor(doctor_spec VARCHAR(20)) 
RETURNS TABLE (
    "ID врача" INTEGER,
    "ФИО врача" text,
    "Специальность" VARCHAR(20)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id_doctor, 
        (d.surname || ' ' || d.name || ' ' || d.patronymic),
        d.specialization
    FROM doctor d
    WHERE d.specialization = doctor_spec
    ORDER BY d.specialization;
END;
$$ LANGUAGE plpgsql;

-- Поиск врачей по ФИО врача
CREATE OR REPLACE FUNCTION get_doctor(doc_surname VARCHAR(35), doc_name VARCHAR(30), doc_patronymic VARCHAR(35)) 
RETURNS TABLE (
    "ID врача" INTEGER,
    "ФИО врача" text,
    "Специальность" VARCHAR(20)
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        d.id_doctor, 
        (d.surname || ' ' || d.name || ' ' || d.patronymic),
        d.specialization
    FROM doctor d
    WHERE d.surname = doc_surname AND d.name = doc_name AND d.patronymic = doc_patronymic
    ORDER BY d.specialization;
END;
$$ LANGUAGE plpgsql;