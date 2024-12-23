CREATE TABLE IF NOT EXISTS sickleave (
    id_sheet SERIAL PRIMARY KEY,
    SNILS VARCHAR(14) UNIQUE,
    begin_time DATE NOT NULL,
    end_time DATE NOT NULL,
    CONSTRAINT begin_end_time_check CHECK (begin_time < end_time),
    FOREIGN KEY (SNILS) REFERENCES patient(SNILS) ON DELETE CASCADE
);