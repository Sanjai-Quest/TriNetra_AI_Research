-- TriNetra PostgreSQL / SQL DDL Schema Definition
DROP TABLE IF EXISTS verdicts CASCADE;
DROP TABLE IF EXISTS investigations CASCADE;
DROP TABLE IF EXISTS custody_events CASCADE;
DROP TABLE IF EXISTS audit_events CASCADE;
DROP TABLE IF EXISTS checkpoints CASCADE;
DROP TABLE IF EXISTS verifications CASCADE;
DROP TABLE IF EXISTS serialized_units CASCADE;
DROP TABLE IF EXISTS evidence CASCADE;
DROP TABLE IF EXISTS claims CASCADE;

-- 1. Claims Table
CREATE TABLE claims (
    claim_id VARCHAR(64) PRIMARY KEY,
    merchant_id VARCHAR(64) NOT NULL,
    customer_id VARCHAR(64) NOT NULL,
    order_id VARCHAR(64) NOT NULL,
    outbound_sku VARCHAR(128) NOT NULL,
    outbound_weight_grams DOUBLE PRECISION NOT NULL,
    return_sku VARCHAR(128) NOT NULL,
    return_weight_grams DOUBLE PRECISION NOT NULL,
    outbound_timestamp TIMESTAMP NOT NULL,
    return_timestamp TIMESTAMP NOT NULL,
    delivery_timestamp TIMESTAMP NOT NULL,
    status VARCHAR(32) NOT NULL
);

-- 2. Evidence Table (base columns only; V3 columns added via ALTER TABLE below)
CREATE TABLE evidence (
    evidence_id VARCHAR(64) PRIMARY KEY,
    claim_id VARCHAR(64) REFERENCES claims(claim_id) ON DELETE CASCADE,
    source VARCHAR(64) NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

-- 3. Verdicts Table
CREATE TABLE verdicts (
    verdict_id VARCHAR(64) PRIMARY KEY,
    claim_id VARCHAR(64) NOT NULL REFERENCES claims(claim_id) ON DELETE CASCADE,
    conflict_type VARCHAR(64) NOT NULL,
    decision VARCHAR(16) NOT NULL,
    reasoning TEXT NOT NULL,
    generated_at TIMESTAMP NOT NULL
);

-- Database Seeding: 5 Test Scenarios for Hackathon Verification

-- Scenario 1: Clean Claim (CONSISTENT)
INSERT INTO claims VALUES (
    'c0000000-0000-0000-0000-000000000001', 'MCH-ZARA', 'CUST-101', 'ORD-9001',
    'NK-RN-FLY-12', 650.0, 'NK-RN-FLY-12', 642.0,
    '2026-09-01 10:00:00', '2026-09-03 14:00:00', '2026-09-02 12:00:00', 'PENDING'
);
INSERT INTO evidence VALUES (
    'e0000000-0000-0000-0000-000000000001', 'c0000000-0000-0000-0000-000000000001',
    'WAREHOUSE_SCALE', '{"scale_id":"SCALE-01","weight":650.0}', '2026-09-01 10:00:00'
);
INSERT INTO evidence VALUES (
    'e0000000-0000-0000-0000-000000000002', 'c0000000-0000-0000-0000-000000000001',
    'COURIER_VOICE', '{"seal_status":"INTACT","weight_assessment":"NORMAL"}', '2026-09-03 14:00:00'
);

INSERT INTO claims VALUES (
    'CLAIM-001', 'MERCHANT-A', 'CUST-101', 'ORD-9001',
    'NIKE-RN-FLY-12', 242.0, 'NIKE-RN-FLY-12', 242.0,
    '2026-09-01 10:00:00', '2026-09-05 14:32:00', '2026-09-02 18:00:00', 'PENDING'
);
INSERT INTO evidence VALUES (
    'e-claim-001-a', 'CLAIM-001', 'WAREHOUSE_SCALE', '{"weight":242.0}', '2026-09-01 10:00:00'
);
INSERT INTO evidence VALUES (
    'e-claim-001-b', 'CLAIM-001', 'COURIER_VOICE', '{"seal_status":"INTACT"}', '2026-09-05 14:32:00'
);

-- Scenario 2: Weight Anomaly (>5% drop)
INSERT INTO claims VALUES (
    'c0000000-0000-0000-0000-000000000002', 'MCH-APPLE', 'CUST-102', 'ORD-9002',
    'APL-IPHONE-15', 450.0, 'APL-IPHONE-15', 120.0,
    '2026-09-01 11:00:00', '2026-09-04 15:00:00', '2026-09-02 13:00:00', 'PENDING'
);
INSERT INTO evidence VALUES (
    'e0000000-0000-0000-0000-000000000003', 'c0000000-0000-0000-0000-000000000002',
    'WAREHOUSE_SCALE', '{"scale_id":"SCALE-02","weight":450.0}', '2026-09-01 11:00:00'
);
INSERT INTO evidence VALUES (
    'e0000000-0000-0000-0000-000000000004', 'c0000000-0000-0000-0000-000000000002',
    'CARRIER_HUB', '{"hub_scale":"HUB-04","weight":120.0}', '2026-09-04 15:00:00'
);

INSERT INTO claims VALUES (
    'CLAIM-002', 'MERCHANT-B', 'CUST-102', 'ORD-9002',
    'APPLE-IPHONE-15', 642.0, 'APPLE-IPHONE-15', 410.0,
    '2026-09-01 10:00:00', '2026-09-04 12:15:00', '2026-09-02 18:00:00', 'PENDING'
);
INSERT INTO evidence VALUES (
    'e-claim-002-a', 'CLAIM-002', 'WAREHOUSE_SCALE', '{"weight":642.0}', '2026-09-01 10:00:00'
);
INSERT INTO evidence VALUES (
    'e-claim-002-b', 'CLAIM-002', 'CARRIER_HUB', '{"weight":410.0}', '2026-09-04 12:15:00'
);

-- Scenario 3: Identity Mismatch (SKU Swap)
INSERT INTO claims VALUES (
    'c0000000-0000-0000-0000-000000000003', 'MCH-NIKE', 'CUST-103', 'ORD-9003',
    'NK-RN-FLY-12', 650.0, 'FAKE-PUMA-99', 650.0,
    '2026-09-01 09:00:00', '2026-09-05 10:00:00', '2026-09-02 11:00:00', 'PENDING'
);
INSERT INTO evidence VALUES (
    'e0000000-0000-0000-0000-000000000005', 'c0000000-0000-0000-0000-000000000003',
    'WAREHOUSE_SCALE', '{"scale_id":"SCALE-01","weight":650.0}', '2026-09-01 09:00:00'
);
INSERT INTO evidence VALUES (
    'e0000000-0000-0000-0000-000000000006', 'c0000000-0000-0000-0000-000000000003',
    'CONSUMER_VIDEO', '{"unboxing_hash":"a1b2c3d4"}', '2026-09-05 10:00:00'
);

INSERT INTO claims VALUES (
    'CLAIM-003', 'MERCHANT-C', 'CUST-103', 'ORD-9003',
    'ADIDAS-ULTRABOOST', 380.0, 'ADIDAS-ULTRABOOST-FAKE', 380.0,
    '2026-09-01 10:00:00', '2026-09-05 09:00:00', '2026-09-02 18:00:00', 'PENDING'
);
INSERT INTO evidence VALUES (
    'e-claim-003-a', 'CLAIM-003', 'WAREHOUSE_SCALE', '{"weight":380.0}', '2026-09-01 10:00:00'
);
INSERT INTO evidence VALUES (
    'e-claim-003-b', 'CLAIM-003', 'CONSUMER_VIDEO', '{"hash":"fake123"}', '2026-09-05 09:00:00'
);

-- Scenario 4: Temporal Violation (Return before delivery)
INSERT INTO claims VALUES (
    'c0000000-0000-0000-0000-000000000004', 'MCH-SAMSUNG', 'CUST-104', 'ORD-9004',
    'SAM-GAL-S24', 380.0, 'SAM-GAL-S24', 380.0,
    '2026-09-01 08:00:00', '2026-09-02 09:00:00', '2026-09-02 18:00:00', 'PENDING'
);
INSERT INTO evidence VALUES (
    'e0000000-0000-0000-0000-000000000007', 'c0000000-0000-0000-0000-000000000004',
    'WAREHOUSE_SCALE', '{"scale_id":"SCALE-03","weight":380.0}', '2026-09-01 08:00:00'
);
INSERT INTO evidence VALUES (
    'e0000000-0000-0000-0000-000000000008', 'c0000000-0000-0000-0000-000000000004',
    'COURIER_VOICE', '{"return_requested":true}', '2026-09-02 09:00:00'
);

INSERT INTO claims VALUES (
    'CLAIM-004', 'MERCHANT-D', 'CUST-104', 'ORD-9004',
    'LEVI-JEANS', 450.0, 'LEVI-JEANS', 450.0,
    '2026-09-01 10:00:00', '2026-09-01 09:00:00', '2026-09-05 18:00:00', 'PENDING'
);
INSERT INTO evidence VALUES (
    'e-claim-004-a', 'CLAIM-004', 'WAREHOUSE_SCALE', '{"weight":450.0}', '2026-09-01 10:00:00'
);
INSERT INTO evidence VALUES (
    'e-claim-004-b', 'CLAIM-004', 'COURIER_VOICE', '{"requested":true}', '2026-09-01 09:00:00'
);

-- Canonical phone-to-dashboard demo case: ORD-98402 / TRN-PKG-7729-A.
INSERT INTO claims VALUES (
    'CASE-ORD-98402', 'MCH-DEMO-MERCHANT', 'CUST-ORD-98402', 'ORD-98402',
    'SMARTPHONE-RETURN-SKU', 642.0, 'SMARTPHONE-RETURN-SKU', 210.0,
    '2026-09-01 11:00:00', '2026-09-06 12:00:00', '2026-09-02 13:00:00', 'INVESTIGATING'
);
INSERT INTO evidence VALUES (
    'e-demo-ord-98402-scale', 'CASE-ORD-98402', 'WAREHOUSE_SCALE',
    '{"caseId":"CASE-ORD-98402","orderId":"ORD-98402","packageId":"TRN-PKG-7729-A","productName":"Smartphone","weight":642.0,"scaleMode":"DEMO_GATT_SCALE"}',
    '2026-09-01 11:00:00'
);
INSERT INTO evidence VALUES (
    'e-demo-ord-98402-voice', 'CASE-ORD-98402', 'COURIER_VOICE',
    '{"rawTranscript":"Box phata hua hai, seal intact hai, weight bahut light hai.","parserMode":"LOCAL_CPU_PARSER"}',
    '2026-09-06 12:00:00'
);

-- Scenario 5: Missing Evidence (Single source only)
INSERT INTO claims VALUES (
    'c0000000-0000-0000-0000-000000000005', 'MCH-SONY', 'CUST-105', 'ORD-9005',
    'SNY-WH1000-XM5', 500.0, 'SNY-WH1000-XM5', 500.0,
    '2026-09-01 12:00:00', '2026-09-04 16:00:00', '2026-09-02 14:00:00', 'PENDING'
);
INSERT INTO evidence VALUES (
    'e0000000-0000-0000-0000-000000000009', 'c0000000-0000-0000-0000-000000000005',
    'WAREHOUSE_SCALE', '{"scale_id":"SCALE-01","weight":500.0}', '2026-09-01 12:00:00'
);

INSERT INTO claims VALUES (
    'CLAIM-005', 'MERCHANT-E', 'CUST-105', 'ORD-9005',
    'SAMSUNG-WATCH', 200.0, 'SAMSUNG-WATCH', 200.0,
    '2026-09-01 10:00:00', '2026-09-05 14:32:00', '2026-09-02 18:00:00', 'PENDING'
);
INSERT INTO evidence VALUES (
    'e-claim-005-a', 'CLAIM-005', 'WAREHOUSE_SCALE', '{"weight":200.0}', '2026-09-01 10:00:00'
);

-- The active dataset is the three serialized units below; legacy claim fixtures are cleared.
DELETE FROM evidence;
DELETE FROM claims;

-- V3 identity, workflow, condition, and custody fields. These are added after
-- legacy seed rows so the existing seed data remains readable during migration.
ALTER TABLE claims ADD COLUMN expected_serial VARCHAR(128);
ALTER TABLE claims ADD COLUMN observed_serial VARCHAR(128);
ALTER TABLE claims ADD COLUMN expected_imei VARCHAR(128);
ALTER TABLE claims ADD COLUMN observed_imei VARCHAR(128);
ALTER TABLE claims ADD COLUMN condition_status VARCHAR(32);
ALTER TABLE claims ADD COLUMN continuity_broken BOOLEAN NOT NULL DEFAULT FALSE;
ALTER TABLE claims ADD COLUMN mandatory_evidence_complete BOOLEAN NOT NULL DEFAULT TRUE;
ALTER TABLE claims ADD COLUMN custody_valid BOOLEAN NOT NULL DEFAULT TRUE;

CREATE TABLE serialized_units (
    unit_id VARCHAR(64) PRIMARY KEY,
    order_id VARCHAR(64) NOT NULL,
    product VARCHAR(128) NOT NULL,
    expected_serial VARCHAR(128) NOT NULL,
    expected_imei VARCHAR(128),
    source_case_id VARCHAR(64),
    source_platform VARCHAR(64),
    source_complaint_type VARCHAR(128),
    source_summary TEXT
);

CREATE TABLE verifications (
    verification_id VARCHAR(64) PRIMARY KEY,
    unit_id VARCHAR(64) NOT NULL REFERENCES serialized_units(unit_id),
    operator_id VARCHAR(64) NOT NULL,
    state VARCHAR(32) NOT NULL,
    created_at TIMESTAMP NOT NULL,
    updated_at TIMESTAMP NOT NULL
);

CREATE TABLE checkpoints (
    checkpoint_id VARCHAR(64) PRIMARY KEY,
    verification_id VARCHAR(64) NOT NULL REFERENCES verifications(verification_id),
    sequence_number INTEGER NOT NULL,
    checkpoint_type VARCHAR(32) NOT NULL,
    location VARCHAR(128),
    operator_id VARCHAR(64) NOT NULL,
    captured_at TIMESTAMP NOT NULL,
    expected_serial VARCHAR(128) NOT NULL,
    observed_serial VARCHAR(128) NOT NULL,
    expected_imei VARCHAR(128),
    observed_imei VARCHAR(128),
    condition_status VARCHAR(32),
    identity_result VARCHAR(32) NOT NULL,
    decision VARCHAR(16) NOT NULL,
    client_event_id VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE custody_events (
    custody_event_id VARCHAR(64) PRIMARY KEY,
    verification_id VARCHAR(64) NOT NULL REFERENCES verifications(verification_id),
    checkpoint_id VARCHAR(64) NOT NULL REFERENCES checkpoints(checkpoint_id),
    from_actor VARCHAR(64),
    to_actor VARCHAR(64) NOT NULL,
    location VARCHAR(128),
    action VARCHAR(32) NOT NULL,
    occurred_at TIMESTAMP NOT NULL,
    client_event_id VARCHAR(64) NOT NULL UNIQUE
);

CREATE TABLE audit_events (
    audit_event_id VARCHAR(64) PRIMARY KEY,
    verification_id VARCHAR(64) NOT NULL REFERENCES verifications(verification_id),
    event_type VARCHAR(64) NOT NULL,
    actor_id VARCHAR(64) NOT NULL,
    payload_json TEXT NOT NULL,
    created_at TIMESTAMP NOT NULL
);

ALTER TABLE evidence ADD COLUMN verification_id VARCHAR(64);
ALTER TABLE evidence ADD COLUMN checkpoint_id VARCHAR(64);
ALTER TABLE evidence ADD COLUMN type VARCHAR(32);
ALTER TABLE evidence ADD COLUMN storage_reference VARCHAR(512);
ALTER TABLE evidence ADD COLUMN captured_by VARCHAR(64);
ALTER TABLE evidence ADD COLUMN file_hash VARCHAR(128);
ALTER TABLE evidence ADD COLUMN client_event_id VARCHAR(64) UNIQUE;

ALTER TABLE evidence ADD CONSTRAINT fk_evidence_verification
    FOREIGN KEY (verification_id) REFERENCES verifications(verification_id);
ALTER TABLE evidence ADD CONSTRAINT fk_evidence_checkpoint
    FOREIGN KEY (checkpoint_id) REFERENCES checkpoints(checkpoint_id);

CREATE TABLE investigations (
    investigation_id VARCHAR(64) PRIMARY KEY,
    verification_id VARCHAR(64) NOT NULL REFERENCES verifications(verification_id),
    unit_id VARCHAR(64) NOT NULL REFERENCES serialized_units(unit_id),
    status VARCHAR(16) NOT NULL,
    reason VARCHAR(64) NOT NULL,
    expected_serial VARCHAR(128) NOT NULL,
    observed_serial VARCHAR(128) NOT NULL,
    last_matching_checkpoint_id VARCHAR(64),
    first_divergence_checkpoint_id VARCHAR(64),
    created_at TIMESTAMP NOT NULL
);

INSERT INTO serialized_units VALUES
    ('UNIT-SN001', 'ORD-98402', 'Smartphone', 'SN001', 'IMEI001', NULL, NULL, NULL, NULL),
    ('UNIT-SN002', 'ORD-98403', 'Smartphone', 'SN002', 'IMEI002', NULL, NULL, NULL, NULL),
    ('UNIT-SN003', 'ORD-98404', 'Smartphone', 'SN003', 'IMEI003', NULL, NULL, NULL, NULL),
    -- Clean V3 test fixtures (pre-delivery physical verification scenarios)
    -- These units have no complaint ID, no complaint text, and no platform attribution.
    ('UNIT-TEST-001', 'ORD-TEST-001', 'Electronics', 'SN-ALPHA-01', 'IMEI-ALPHA-01', NULL, NULL, NULL, NULL),
    ('UNIT-TEST-002', 'ORD-TEST-002', 'Electronics', 'SN-BETA-02',  'IMEI-BETA-02',  NULL, NULL, NULL, NULL),
    ('UNIT-TEST-003', 'ORD-TEST-003', 'Footwear',    'SN-GAMMA-03', NULL,             NULL, NULL, NULL, NULL);

