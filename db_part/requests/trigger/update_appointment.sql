CREATE OR REPLACE FUNCTION update_appointment_count()
RETURNS TRIGGER AS $$
BEGIN
    IF TG_OP = 'INSERT' THEN
        UPDATE doctor
        SET appointment_count = appointment_count + 1
        WHERE id_doctor = NEW.id_doctor;
    ELSIF TG_OP = 'DELETE' THEN
        UPDATE doctor
        SET appointment_count = appointment_count - 1
        WHERE id_doctor = OLD.id_doctor;
    END IF;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_add_new_appointment
AFTER INSERT ON appointment
FOR EACH ROW EXECUTE FUNCTION update_appointment_count();

CREATE TRIGGER after_delete_appointment
AFTER DELETE ON appointment
FOR EACH ROW EXECUTE FUNCTION update_appointment_count();