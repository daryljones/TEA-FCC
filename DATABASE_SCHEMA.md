# FCC ULS Database Schema Documentation

This document describes the complete database schema for the FCC ULS (Universal Licensing System) Land Mobile database downloader.

## Overview

The database stores comprehensive data from the FCC ULS system, including license information, entity details, frequency assignments, locations, antenna specifications, and application purposes. The database uses SQLite and is designed to handle daily updates from the FCC's data feeds.

## Tables

### 1. `download_history`
Tracks all download attempts and their outcomes.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| download_date | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | When the download occurred |
| file_type | TEXT | | Type of file downloaded (e.g., 'LM') |
| file_size | INTEGER | | Size of downloaded file in bytes |
| records_processed | INTEGER | | Number of records processed |
| success | BOOLEAN | | Whether the download was successful |
| error_message | TEXT | | Error message if download failed |

### 2. `licenses`
Contains license records from the FCC ULS system.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| unique_system_identifier | TEXT | | ULS unique system identifier |
| uls_file_number | TEXT | | ULS file number |
| ebf_number | TEXT | | Electronic Batch Filing number |
| call_sign | TEXT | | FCC call sign |
| license_status | TEXT | | Current license status |
| radio_service_type | TEXT | | Type of radio service |
| grant_date | TEXT | | Date license was granted |
| expired_date | TEXT | | License expiration date |
| cancellation_date | TEXT | | Date license was cancelled (if applicable) |
| eligibility_rule_num | TEXT | | Eligibility rule number |
| applicant_type_code | TEXT | | Code for applicant type |
| alien | TEXT | | Alien ownership indicator |
| alien_government | TEXT | | Alien government control indicator |
| alien_corporation | TEXT | | Alien corporation control indicator |
| alien_officer | TEXT | | Alien officer control indicator |
| alien_control | TEXT | | Other alien control indicator |
| revoked | TEXT | | License revocation indicator |
| convicted | TEXT | | Conviction indicator |
| adjudged | TEXT | | Adjudication indicator |
| involved_reserved | TEXT | | Reserved frequency involvement |
| common_carrier | TEXT | | Common carrier indicator |
| non_common_carrier | TEXT | | Non-common carrier indicator |
| private_comm | TEXT | | Private communication indicator |
| fixed | TEXT | | Fixed service indicator |
| mobile | TEXT | | Mobile service indicator |
| radiolocation | TEXT | | Radiolocation service indicator |
| satellite | TEXT | | Satellite service indicator |
| developmental_or_sta | TEXT | | Developmental/STA indicator |
| interconnected_service | TEXT | | Interconnected service indicator |
| certifier_first_name | TEXT | | Certifier's first name |
| certifier_mi | TEXT | | Certifier's middle initial |
| certifier_last_name | TEXT | | Certifier's last name |
| certifier_suffix | TEXT | | Certifier's name suffix |
| certifier_title | TEXT | | Certifier's title |
| gender | TEXT | | Gender designation |
| african_american | TEXT | | African American designation |
| native_american | TEXT | | Native American designation |
| hawaiian | TEXT | | Hawaiian designation |
| asian | TEXT | | Asian designation |
| white | TEXT | | White designation |
| ethnicity | TEXT | | Ethnicity designation |
| effective_date | TEXT | | Effective date |
| last_action_date | TEXT | | Date of last action |
| auction_id | TEXT | | Auction identifier |
| reg_stat_broad_serv | TEXT | | Regulatory status for broadcast service |
| band_manager | TEXT | | Band manager indicator |
| type_serv_broad_serv | TEXT | | Type of service for broadcast |
| alien_ruling | TEXT | | Alien ruling indicator |
| licensee_name_change | TEXT | | Licensee name change indicator |
| whitespace_ind | TEXT | | Whitespace indicator |
| additional_cert_choice | TEXT | | Additional certification choice |
| additional_cert_answer | TEXT | | Additional certification answer |
| discontinuation_ind | TEXT | | Discontinuation indicator |
| regulatory_compliance_ind | TEXT | | Regulatory compliance indicator |
| eligibility_cert_900 | TEXT | | 900 MHz eligibility certification |
| transition_plan_cert_900 | TEXT | | 900 MHz transition plan certification |
| return_spectrum_cert_900 | TEXT | | 900 MHz spectrum return certification |
| payment_cert_900 | TEXT | | 900 MHz payment certification |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### 3. `entities`
Contains entity (licensee) information.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| unique_system_identifier | TEXT | FOREIGN KEY → licenses | ULS unique system identifier |
| uls_file_number | TEXT | | ULS file number |
| ebf_number | TEXT | | Electronic Batch Filing number |
| call_sign | TEXT | | FCC call sign |
| entity_type | TEXT | | Type of entity (licensee, applicant, etc.) |
| licensee_id | TEXT | | Licensee identifier |
| entity_name | TEXT | | Name of entity/organization |
| first_name | TEXT | | Individual's first name |
| mi | TEXT | | Middle initial |
| last_name | TEXT | | Last name |
| suffix | TEXT | | Name suffix |
| phone | TEXT | | Phone number |
| fax | TEXT | | Fax number |
| email | TEXT | | Email address |
| street_address | TEXT | | Street address |
| city | TEXT | | City |
| state | TEXT | | State/province |
| zip_code | TEXT | | ZIP/postal code |
| po_box | TEXT | | PO Box |
| attention_line | TEXT | | Attention line |
| sgin | TEXT | | SGIN identifier |
| frn | TEXT | | FCC Registration Number |
| applicant_type_code | TEXT | | Applicant type code |
| applicant_type_other | TEXT | | Other applicant type |
| status_code | TEXT | | Status code |
| status_date | TEXT | | Status date |
| lic_category_code | TEXT | | License category code |
| linked_license_id | TEXT | | Linked license identifier |
| linked_callsign | TEXT | | Linked call sign |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### 4. `frequencies`
Contains frequency assignment data for each license.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| unique_system_identifier | TEXT | FOREIGN KEY → licenses | ULS unique system identifier |
| uls_file_number | TEXT | | ULS file number |
| ebf_number | TEXT | | Electronic Batch Filing number |
| call_sign | TEXT | | FCC call sign |
| frequency_assigned | REAL | | Assigned frequency in MHz |
| frequency_upper_band | REAL | | Upper band frequency in MHz |
| frequency_carrier | REAL | | Carrier frequency in MHz |
| frequency_offset | REAL | | Frequency offset in kHz |
| emission_designator | TEXT | | Emission designator code |
| power_output | REAL | | Output power in watts |
| power_erp | REAL | | Effective radiated power in watts |
| tolerance | REAL | | Frequency tolerance |
| frequency_number | REAL | | Frequency number |
| frequency_seq_id | REAL | | Frequency sequence ID |
| status_code | TEXT | | Status code |
| status_date | TEXT | | Status date |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### 5. `locations`
Contains location data for transmitter sites and service areas.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| unique_system_identifier | TEXT | FOREIGN KEY → licenses | ULS unique system identifier |
| uls_file_number | TEXT | | ULS file number |
| ebf_number | TEXT | | Electronic Batch Filing number |
| call_sign | TEXT | | FCC call sign |
| location_action_performed | TEXT | | Action performed on location |
| location_type_code | TEXT | | Type of location |
| location_class_code | TEXT | | Location class code |
| location_number | TEXT | | Location number |
| site_status | TEXT | | Site status |
| corresponding_fixed_location | TEXT | | Corresponding fixed location |
| location_address | TEXT | | Street address of location |
| location_city | TEXT | | City |
| location_county | TEXT | | County |
| location_state | TEXT | | State |
| radius_of_operation | REAL | | Radius of operation in km |
| area_of_operation_code | TEXT | | Area of operation code |
| clearance_indicator | TEXT | | Clearance indicator |
| ground_elevation | REAL | | Ground elevation in meters |
| lat_degrees | INTEGER | | Latitude degrees |
| lat_minutes | INTEGER | | Latitude minutes |
| lat_seconds | REAL | | Latitude seconds |
| lat_direction | TEXT | | Latitude direction (N/S) |
| long_degrees | INTEGER | | Longitude degrees |
| long_minutes | INTEGER | | Longitude minutes |
| long_seconds | REAL | | Longitude seconds |
| long_direction | TEXT | | Longitude direction (E/W) |
| max_lat_degrees | INTEGER | | Maximum latitude degrees |
| max_lat_minutes | INTEGER | | Maximum latitude minutes |
| max_lat_seconds | REAL | | Maximum latitude seconds |
| max_lat_direction | TEXT | | Maximum latitude direction |
| max_long_degrees | INTEGER | | Maximum longitude degrees |
| max_long_minutes | INTEGER | | Maximum longitude minutes |
| max_long_seconds | REAL | | Maximum longitude seconds |
| max_long_direction | TEXT | | Maximum longitude direction |
| nepa | TEXT | | NEPA requirement indicator |
| quiet_zone_notification_date | TEXT | | Quiet zone notification date |
| tower_registration_number | TEXT | | Tower registration number |
| height_of_support_structure | REAL | | Height of support structure in meters |
| overall_height_of_structure | REAL | | Overall height of structure in meters |
| structure_type | TEXT | | Type of structure |
| airport_id | TEXT | | Airport identifier |
| location_name | TEXT | | Location name |
| units_hand_held | REAL | | Number of hand-held units |
| units_mobile | REAL | | Number of mobile units |
| units_temp_fixed | REAL | | Number of temporary fixed units |
| units_aircraft | REAL | | Number of aircraft units |
| units_itinerant | REAL | | Number of itinerant units |
| status_code | TEXT | | Status code |
| status_date | TEXT | | Status date |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### 6. `antennas`
Contains antenna specifications and configurations.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| unique_system_identifier | TEXT | FOREIGN KEY → licenses | ULS unique system identifier |
| uls_file_number | TEXT | | ULS file number |
| ebf_number | TEXT | | Electronic Batch Filing number |
| call_sign | TEXT | | FCC call sign |
| antenna_action_performed | TEXT | | Action performed on antenna |
| antenna_number | INTEGER | | Antenna number |
| location_number | INTEGER | | Associated location number |
| receiver_number | INTEGER | | Associated receiver number |
| antenna_type_code | TEXT | | Antenna type code |
| height_to_tip | REAL | | Height to antenna tip in meters |
| height_to_center_raat | REAL | | Height to center RAAT in meters |
| antenna_make | TEXT | | Antenna manufacturer |
| antenna_model | TEXT | | Antenna model |
| tilt_toward | REAL | | Tilt toward azimuth in degrees |
| tilt_angle | REAL | | Tilt angle in degrees |
| polarization_code | TEXT | | Polarization code |
| beamwidth_horiz | REAL | | Horizontal beamwidth in degrees |
| beamwidth_vert | REAL | | Vertical beamwidth in degrees |
| gain | REAL | | Antenna gain in dBi |
| azimuth | REAL | | Azimuth in degrees |
| height_above_avg_terrain | REAL | | Height above average terrain in meters |
| diversity_height | REAL | | Diversity antenna height in meters |
| diversity_gain | REAL | | Diversity antenna gain in dBi |
| diversity_beam | REAL | | Diversity beam pattern |
| reflector_height | REAL | | Reflector height in meters |
| reflector_width | REAL | | Reflector width in meters |
| reflector_separation | REAL | | Reflector separation in meters |
| repeater_height | REAL | | Repeater height in meters |
| repeater_width | REAL | | Repeater width in meters |
| repeater_separation | REAL | | Repeater separation in meters |
| commanded_azimuth | REAL | | Commanded azimuth in degrees |
| commanded_elevation | REAL | | Commanded elevation in degrees |
| twist | REAL | | Antenna twist in degrees |
| settle_time | REAL | | Settle time in seconds |
| comment_text | TEXT | | Additional comments |
| status_code | TEXT | | Status code |
| status_date | TEXT | | Status date |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

### 7. `application_purpose`
Contains application purpose codes and descriptions.

| Column | Type | Constraints | Description |
|--------|------|-------------|-------------|
| id | INTEGER | PRIMARY KEY AUTOINCREMENT | Unique identifier |
| unique_system_identifier | TEXT | FOREIGN KEY → licenses | ULS unique system identifier |
| uls_file_number | TEXT | | ULS file number |
| ebf_number | TEXT | | Electronic Batch Filing number |
| call_sign | TEXT | | FCC call sign |
| purpose_code | TEXT | | Purpose code |
| status_code | TEXT | | Status code |
| status_date | TEXT | | Status date |
| created_at | TIMESTAMP | DEFAULT CURRENT_TIMESTAMP | Record creation timestamp |

## Relationships

- All tables are linked to the `licenses` table via `unique_system_identifier`
- Each license can have multiple:
  - Entities (licensees, applicants, contacts)
  - Frequencies (frequency assignments)
  - Locations (transmitter sites, service areas)
  - Antennas (antenna configurations)
  - Application purposes (multiple purpose codes)

## Data Sources

The data comes from the following FCC ULS data files:
- **LM.dat** - Land Mobile license data → `licenses` table
- **HD.dat** - Alternative license data → `licenses` table  
- **EN.dat** - Entity data → `entities` table
- **FR.dat** - Frequency data → `frequencies` table
- **LO.dat** - Location data → `locations` table
- **AN.dat** - Antenna data → `antennas` table
- **AP.dat** - Application purpose data → `application_purpose` table

## Indexes

For optimal performance, consider creating indexes on frequently queried columns:

```sql
-- Primary lookup indexes
CREATE INDEX IF NOT EXISTS idx_licenses_call_sign ON licenses(call_sign);
CREATE INDEX IF NOT EXISTS idx_licenses_usi ON licenses(unique_system_identifier);

-- Entity indexes
CREATE INDEX IF NOT EXISTS idx_entities_call_sign ON entities(call_sign);
CREATE INDEX IF NOT EXISTS idx_entities_usi ON entities(unique_system_identifier);
CREATE INDEX IF NOT EXISTS idx_entities_name ON entities(entity_name);

-- Frequency indexes
CREATE INDEX IF NOT EXISTS idx_frequencies_call_sign ON frequencies(call_sign);
CREATE INDEX IF NOT EXISTS idx_frequencies_usi ON frequencies(unique_system_identifier);
CREATE INDEX IF NOT EXISTS idx_frequencies_assigned ON frequencies(frequency_assigned);

-- Location indexes
CREATE INDEX IF NOT EXISTS idx_locations_call_sign ON locations(call_sign);
CREATE INDEX IF NOT EXISTS idx_locations_usi ON locations(unique_system_identifier);
CREATE INDEX IF NOT EXISTS idx_locations_coords ON locations(lat_degrees, lat_minutes, long_degrees, long_minutes);

-- Antenna indexes
CREATE INDEX IF NOT EXISTS idx_antennas_call_sign ON antennas(call_sign);
CREATE INDEX IF NOT EXISTS idx_antennas_usi ON antennas(unique_system_identifier);

-- Application purpose indexes
CREATE INDEX IF NOT EXISTS idx_purpose_call_sign ON application_purpose(call_sign);
CREATE INDEX IF NOT EXISTS idx_purpose_usi ON application_purpose(unique_system_identifier);
```

## Usage Examples

### Find all data for a specific call sign
```sql
-- Get license info
SELECT * FROM licenses WHERE call_sign = 'WQXJ123';

-- Get entity info
SELECT * FROM entities WHERE call_sign = 'WQXJ123';

-- Get frequencies
SELECT * FROM frequencies WHERE call_sign = 'WQXJ123';

-- Get locations
SELECT * FROM locations WHERE call_sign = 'WQXJ123';

-- Get antennas
SELECT * FROM antennas WHERE call_sign = 'WQXJ123';
```

### Find frequencies in a specific band
```sql
SELECT DISTINCT call_sign, frequency_assigned, power_erp
FROM frequencies 
WHERE frequency_assigned BETWEEN 450.0 AND 470.0
ORDER BY frequency_assigned;
```

### Find locations near coordinates
```sql
SELECT call_sign, location_city, location_state,
       lat_degrees, lat_minutes, long_degrees, long_minutes
FROM locations 
WHERE lat_degrees = 40 AND long_degrees = -74
  AND lat_minutes BETWEEN 45 AND 55
  AND long_minutes BETWEEN 0 AND 10;
```
