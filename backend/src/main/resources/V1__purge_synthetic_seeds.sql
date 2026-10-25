-- Idempotent cleanup: remove synthetic complaint seeds from V3 logistics tables.
-- Safe to run multiple times; DELETE WHERE is a no-op if rows don't exist.
DELETE FROM audit_events    WHERE audit_event_id   IN ('AUD-CMP-00001','AUD-CMP-00002','AUD-CMP-00003');
DELETE FROM investigations  WHERE investigation_id IN ('INV-CMP-00001','INV-CMP-00002','INV-CMP-00003');
DELETE FROM custody_events  WHERE custody_event_id IN ('CUST-CMP-00001','CUST-CMP-00002','CUST-CMP-00003');
DELETE FROM checkpoints     WHERE checkpoint_id    IN ('CHK-CMP-00001','CHK-CMP-00002','CHK-CMP-00003');
DELETE FROM verifications   WHERE verification_id  IN ('VERIF-CMP-00001','VERIF-CMP-00002','VERIF-CMP-00003');
DELETE FROM serialized_units WHERE unit_id          IN ('XS-CMP-00001','XS-CMP-00002','XS-CMP-00003');
