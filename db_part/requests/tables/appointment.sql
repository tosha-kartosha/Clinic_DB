CREATE TABLE IF NOT EXISTS appointment (
    id_appointment SERIAL PRIMARY KEY,
    id_doctor INTEGER NOT NULL,
    SNILS_patient VARCHAR(14) NOT NULL,
    record_date TIMESTAMP NOT NULL,
    ICD VARCHAR(5) DEFAULT NULL CHECK (ICD IS NULL OR ICD ~ '^[A-Z][0-9]{2}\.[0-9]$'),
    UNIQUE (id_doctor, record_date),
    UNIQUE(SNILS_patient, record_date),
    FOREIGN KEY (id_doctor) REFERENCES doctor(id_doctor) ON DELETE CASCADE,
    FOREIGN KEY (SNILS_patient) REFERENCES patient(SNILS) ON DELETE CASCADE
);