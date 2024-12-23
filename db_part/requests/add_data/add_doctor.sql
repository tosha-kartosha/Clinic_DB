-- Добавление врача в базу
CREATE OR REPLACE PROCEDURE app.add_doctor(
    new_surname VARCHAR(35),
    new_name VARCHAR(30),
    new_patronymic VARCHAR(35),
    new_specialization VARCHAR(20)
)
SECURITY DEFINER
AS $$
BEGIN
    INSERT INTO doctor (id_doctor, surname, name, patronymic, specialization)
    VALUES (new_surname, new_name, new_patronymic, new_specialization);
    RAISE NOTICE 'Доктор "%" был успешно добавлен в базу.', new_surname || ' ' || new_name || ' ' || new_patronymic;
END;
$$ LANGUAGE plpgsql;



CREATE OR REPLACE PROCEDURE add_doctor(
    new_surname VARCHAR(35),
    new_name VARCHAR(30),
    new_patronymic VARCHAR(35),
    new_specialization VARCHAR(20)
)
AS $$
BEGIN
    INSERT INTO doctor (surname, name, patronymic, specialization)
    VALUES (new_surname, new_name, new_patronymic, new_specialization);
    RAISE NOTICE 'Доктор "%" был успешно добавлен в базу.', new_surname || ' ' || new_name || ' ' || new_patronymic;
END;
$$ LANGUAGE plpgsql;