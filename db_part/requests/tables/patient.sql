CREATE TABLE IF NOT EXISTS patient (
    SNILS VARCHAR(14) PRIMARY KEY,
    surname VARCHAR(35) NOT NULL,
    name VARCHAR(30) NOT NULL,
    patronymic VARCHAR(35) NOT NULL,
    birth_date DATE NOT NULL, 
    address text,
    medical_consent VARCHAR(3) CHECK (medical_consent IN ('Да', 'Нет'))
);