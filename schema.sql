-- FCC ULS Database Schema
-- Generated: 2025-08-17 15:29:50
-- Source: fcc_uls.db

-- Enable foreign key constraints
PRAGMA foreign_keys = ON;

-- TABLES
--------------------------------------------------
-- antennas
CREATE TABLE antennas (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        antenna_action_performed TEXT,
                        antenna_number INTEGER,
                        location_number INTEGER,
                        receiver_number INTEGER,
                        antenna_type_code TEXT,
                        height_to_tip REAL,
                        height_to_center_raat REAL,
                        antenna_make TEXT,
                        antenna_model TEXT,
                        tilt_toward REAL,
                        tilt_angle REAL,
                        polarization_code TEXT,
                        beamwidth_horiz REAL,
                        beamwidth_vert REAL,
                        gain REAL,
                        azimuth REAL,
                        height_above_avg_terrain REAL,
                        diversity_height REAL,
                        diversity_gain REAL,
                        diversity_beam REAL,
                        reflector_height REAL,
                        reflector_width REAL,
                        reflector_separation REAL,
                        repeater_height REAL,
                        repeater_width REAL,
                        repeater_separation REAL,
                        commanded_azimuth REAL,
                        commanded_elevation REAL,
                        twist REAL,
                        settle_time REAL,
                        comment_text TEXT,
                        status_code TEXT,
                        status_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (unique_system_identifier) REFERENCES licenses (unique_system_identifier)
                    );

-- application_purpose
CREATE TABLE application_purpose (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        purpose_code TEXT,
                        status_code TEXT,
                        status_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (unique_system_identifier) REFERENCES licenses (unique_system_identifier)
                    );

-- download_history
CREATE TABLE download_history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        download_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        file_type TEXT,
                        file_size INTEGER,
                        records_processed INTEGER,
                        success BOOLEAN,
                        error_message TEXT
                    );

-- entities
CREATE TABLE entities (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        entity_type TEXT,
                        licensee_id TEXT,
                        entity_name TEXT,
                        first_name TEXT,
                        mi TEXT,
                        last_name TEXT,
                        suffix TEXT,
                        phone TEXT,
                        fax TEXT,
                        email TEXT,
                        street_address TEXT,
                        city TEXT,
                        state TEXT,
                        zip_code TEXT,
                        po_box TEXT,
                        attention_line TEXT,
                        sgin TEXT,
                        frn TEXT,
                        applicant_type_code TEXT,
                        applicant_type_other TEXT,
                        status_code TEXT,
                        status_date TEXT,
                        lic_category_code TEXT,
                        linked_license_id TEXT,
                        linked_callsign TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (unique_system_identifier) REFERENCES licenses (unique_system_identifier)
                    );

-- frequencies
CREATE TABLE frequencies (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        frequency_assigned REAL,
                        frequency_upper_band REAL,
                        frequency_carrier REAL,
                        frequency_offset REAL,
                        emission_designator TEXT,
                        power_output REAL,
                        power_erp REAL,
                        tolerance REAL,
                        frequency_number INTEGER,
                        frequency_seq_id INTEGER,
                        status_code TEXT,
                        status_date TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (unique_system_identifier) REFERENCES licenses (unique_system_identifier)
                    );

-- licenses
CREATE TABLE licenses (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT UNIQUE,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        license_status TEXT,
                        radio_service_type TEXT,
                        grant_date TEXT,
                        expired_date TEXT,
                        cancellation_date TEXT,
                        eligibility_rule_num TEXT,
                        applicant_type_code TEXT,
                        alien TEXT,
                        alien_government TEXT,
                        alien_corporation TEXT,
                        alien_officer TEXT,
                        alien_control TEXT,
                        revoked TEXT,
                        convicted TEXT,
                        adjudged TEXT,
                        involved_reserved TEXT,
                        common_carrier TEXT,
                        non_common_carrier TEXT,
                        private_comm TEXT,
                        fixed TEXT,
                        mobile TEXT,
                        radiolocation TEXT,
                        satellite TEXT,
                        developmental_or_sta TEXT,
                        interconnected_service TEXT,
                        certifier_first_name TEXT,
                        certifier_mi TEXT,
                        certifier_last_name TEXT,
                        certifier_suffix TEXT,
                        certifier_title TEXT,
                        gender TEXT,
                        african_american TEXT,
                        native_american TEXT,
                        hawaiian TEXT,
                        asian TEXT,
                        white TEXT,
                        ethnicity TEXT,
                        effective_date TEXT,
                        last_action_date TEXT,
                        auction_id TEXT,
                        reg_stat_broad_serv TEXT,
                        band_manager TEXT,
                        type_serv_broad_serv TEXT,
                        alien_ruling TEXT,
                        licensee_name_change TEXT,
                        whitespace_ind TEXT,
                        additional_cert_choice TEXT,
                        additional_cert_answer TEXT,
                        discontinuation_ind TEXT,
                        regulatory_compliance_ind TEXT,
                        eligibility_cert_900 TEXT,
                        transition_plan_cert_900 TEXT,
                        return_spectrum_cert_900 TEXT,
                        payment_cert_900 TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    );

-- locations
CREATE TABLE locations (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        unique_system_identifier TEXT,
                        uls_file_number TEXT,
                        ebf_number TEXT,
                        call_sign TEXT,
                        location_action_performed TEXT,
                        location_type_code TEXT,
                        location_class_code TEXT,
                        location_number INTEGER,
                        site_status TEXT,
                        corresponding_fixed_location INTEGER,
                        location_address TEXT,
                        location_city TEXT,
                        location_county TEXT,
                        location_state TEXT,
                        radius_of_operation REAL,
                        area_of_operation_code TEXT,
                        clearance_indicator TEXT,
                        ground_elevation REAL,
                        lat_degrees INTEGER,
                        lat_minutes INTEGER,
                        lat_seconds REAL,
                        lat_direction TEXT,
                        long_degrees INTEGER,
                        long_minutes INTEGER,
                        long_seconds REAL,
                        long_direction TEXT,
                        max_lat_degrees INTEGER,
                        max_lat_minutes INTEGER,
                        max_lat_seconds REAL,
                        max_lat_direction TEXT,
                        max_long_degrees INTEGER,
                        max_long_minutes INTEGER,
                        max_long_seconds REAL,
                        max_long_direction TEXT,
                        nepa TEXT,
                        quiet_zone_notification_date TEXT,
                        tower_registration_number TEXT,
                        height_of_support_structure REAL,
                        overall_height_of_structure REAL,
                        structure_type TEXT,
                        airport_id TEXT,
                        location_name TEXT,
                        units_hand_held TEXT,
                        units_mobile TEXT,
                        units_temp_fixed TEXT,
                        units_aircraft TEXT,
                        units_itinerant TEXT,
                        status_code TEXT,
                        status_date TEXT,
                        earth_station_agreement TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        FOREIGN KEY (unique_system_identifier) REFERENCES licenses (unique_system_identifier)
                    );

-- sqlite_sequence
CREATE TABLE sqlite_sequence(name,seq);

-- INDEXS
--------------------------------------------------
-- idx_download_history_date
CREATE INDEX idx_download_history_date ON download_history(download_date);

-- idx_download_history_success
CREATE INDEX idx_download_history_success ON download_history(success);

-- idx_entities_name
CREATE INDEX idx_entities_name ON entities(entity_name);

-- idx_entities_state
CREATE INDEX idx_entities_state ON entities(state);

-- idx_entities_type
CREATE INDEX idx_entities_type ON entities(entity_type);

-- idx_licenses_call_sign
CREATE INDEX idx_licenses_call_sign ON licenses(call_sign);

-- idx_licenses_expired_date
CREATE INDEX idx_licenses_expired_date ON licenses(expired_date);

-- idx_licenses_grant_date
CREATE INDEX idx_licenses_grant_date ON licenses(grant_date);

-- idx_licenses_service_type
CREATE INDEX idx_licenses_service_type ON licenses(radio_service_type);

-- idx_licenses_status
CREATE INDEX idx_licenses_status ON licenses(license_status);
