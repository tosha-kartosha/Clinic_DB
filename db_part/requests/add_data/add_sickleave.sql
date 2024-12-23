-- Добавление больничного листа пациенту

CREATE OR REPLACE PROCEDURE add_sickleave(
    new_SNILS VARCHAR(14),
    new_begin_time DATE,
    new_end_time DATE
)
AS $$
BEGIN
    INSERT INTO sickleave (SNILS, begin_time, end_time)
    VALUES (new_SNILS, new_begin_time, new_end_time);
    
    RAISE NOTICE 'Больничный лист был успешно добавлен в базу.';
END;
$$ LANGUAGE plpgsql;
