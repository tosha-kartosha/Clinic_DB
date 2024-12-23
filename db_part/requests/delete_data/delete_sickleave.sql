-- удаление больничного листа по снилсу
CREATE OR REPLACE PROCEDURE delete_sickleave(
    delete_snils VARCHAR(14)
)
AS $$
BEGIN
    DELETE FROM sickleave WHERE delete_snils = SNILS;

    IF NOT FOUND THEN
        RAISE EXCEPTION 'Больничный лист не найден';
    END IF;

    RAISE NOTICE 'Больничный лист удален';
END;
$$ LANGUAGE plpgsql;