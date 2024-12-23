CREATE TABLE IF NOT EXISTS doctor (
    id_doctor SERIAL PRIMARY KEY,
    surname VARCHAR(35) NOT NULL,
    name VARCHAR(30) NOT NULL,
    patronymic VARCHAR(35) NOT NULL,
    specialization VARCHAR(20) NOT NULL CHECK (specialization IN ('Терапевт', 'Гастроэнтеролог', 'Офтальмолог', 'Окулист', 'Невролог', 'Отоларинголог', 'Хирург', 'Психиатр')),
    appointment_count INT DEFAULT 0,
    UNIQUE (surname, name, patronymic, specialization)
);

CREATE INDEX IF NOT EXISTS spec ON doctor (specialization);