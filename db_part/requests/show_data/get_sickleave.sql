-- Поиск больничного листа по снилсу пациента
CREATE OR REPLACE FUNCTION get_sickleave(pat_SNILS VARCHAR(14)) 
RETURNS TABLE (
    "Номер больничного листа" INTEGER,
    "ФИО" text,
    "Дата открытия" DATE,
    "Дата закрытии" DATE
)
AS $$
BEGIN
    RETURN QUERY
    SELECT
        s.id_sheet,
        (p.surname || ' ' || p.name || ' ' || p.patronymic),
        s.begin_time, s.end_time
    FROM sickleave s
    JOIN patient p ON s.SNILS = p.SNILS
    WHERE p.SNILS = pat_SNILS;
END;
$$ LANGUAGE plpgsql;