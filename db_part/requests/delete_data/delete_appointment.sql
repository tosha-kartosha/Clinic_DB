-- удаление записи по ID
CREATE OR REPLACE PROCEDURE delete_appointment(
    delete_id_appointment INTEGER
)
AS $$
BEGIN
    DELETE FROM appointment where id_appointment = delete_id_appointment;
    IF NOT FOUND THEN
        RAISE EXCEPTION 'Записи с ID "%" не существует в базе', delete_id_appointment;
    END IF;

    RAISE NOTICE 'Запись с ID "%" была удалена.', delete_id_appointment;
END;
$$ LANGUAGE plpgsql;