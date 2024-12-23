CREATE OR REPLACE FUNCTION get_doctor_statistic()
RETURNS TABLE(
    "ФИО врача" text,
    "Должность врача" VARCHAR(20),
    "Количество записей" INT
) AS $$
BEGIN
    RETURN QUERY
    SELECT (surname || ' ' || name || ' ' || patronymic),
           specialization,
           appointment_count
    FROM doctor
    ORDER BY appointment_count DESC;
END;
$$ LANGUAGE plpgsql;