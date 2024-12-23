-- продление больничного листа
CREATE OR REPLACE PROCEDURE update_sickleave_end_date(
    p_SNILS VARCHAR(14),
    new_end_time DATE
)
AS $$
BEGIN
    UPDATE sickleave
    SET end_time = new_end_time
    WHERE SNILS = p_SNILS;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Больничный лист не найден';
    END IF;
    RAISE NOTICE 'Больничный лист продлен до %.', new_end_time;
END;
$$ LANGUAGE plpgsql;