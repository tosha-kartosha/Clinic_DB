-- очистка все таблиц
CREATE OR REPLACE PROCEDURE delete_all()
AS $$
BEGIN
    DELETE FROM appointment;
    DELETE FROM sickleave;
    DELETE FROM doctor;
    DELETE FROM patient;
    RAISE NOTICE 'Информация из всех таблиц БД была очищена';
END;
$$ LANGUAGE plpgsql;