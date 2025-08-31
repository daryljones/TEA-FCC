-- Database Performance Indexes for FCC ULS Database
-- These indexes optimize queries used by the enhanced lookup tool

-- Primary lookup indexes for call signs
CREATE INDEX IF NOT EXISTS idx_licenses_call_sign ON licenses(call_sign);
CREATE INDEX IF NOT EXISTS idx_entities_call_sign ON entities(call_sign);
CREATE INDEX IF NOT EXISTS idx_frequencies_call_sign ON frequencies(call_sign);
CREATE INDEX IF NOT EXISTS idx_locations_call_sign ON locations(call_sign);

-- Indexes for joining tables by ULS file number
CREATE INDEX IF NOT EXISTS idx_licenses_uls_file_number ON licenses(uls_file_number);
CREATE INDEX IF NOT EXISTS idx_entities_uls_file_number ON entities(uls_file_number);
CREATE INDEX IF NOT EXISTS idx_frequencies_uls_file_number ON frequencies(uls_file_number);
CREATE INDEX IF NOT EXISTS idx_locations_uls_file_number ON locations(uls_file_number);

-- Indexes for name searches (entities table)
CREATE INDEX IF NOT EXISTS idx_entities_entity_name ON entities(entity_name);
CREATE INDEX IF NOT EXISTS idx_entities_first_last_name ON entities(first_name, last_name);

-- Indexes for frequency searches
CREATE INDEX IF NOT EXISTS idx_frequencies_frequency_assigned ON frequencies(frequency_assigned);
CREATE INDEX IF NOT EXISTS idx_frequencies_freq_callsign ON frequencies(frequency_assigned, call_sign);

-- Indexes for license status filtering
CREATE INDEX IF NOT EXISTS idx_licenses_status ON licenses(license_status);
CREATE INDEX IF NOT EXISTS idx_frequencies_status ON frequencies(status_code);

-- Indexes for geographic searches
CREATE INDEX IF NOT EXISTS idx_entities_city_state ON entities(city, state);
CREATE INDEX IF NOT EXISTS idx_locations_city_state ON locations(location_city, location_state);

-- Composite indexes for common query patterns
CREATE INDEX IF NOT EXISTS idx_licenses_callsign_status ON licenses(call_sign, license_status);
CREATE INDEX IF NOT EXISTS idx_entities_callsign_name ON entities(call_sign, entity_name);
CREATE INDEX IF NOT EXISTS idx_frequencies_callsign_freq ON frequencies(call_sign, frequency_assigned);

-- Index for ordering frequency results
CREATE INDEX IF NOT EXISTS idx_frequencies_freq_ordered ON frequencies(frequency_assigned, call_sign, status_code);

-- Performance statistics
CREATE INDEX IF NOT EXISTS idx_licenses_service_type ON licenses(radio_service_type);
CREATE INDEX IF NOT EXISTS idx_entities_state ON entities(state);
