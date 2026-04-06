--
-- PostgreSQL database dump
--

\restrict 7iMiofKaaveb1NblddaJPpdWdLxXB465hs57JL77pdIN5e65WMI99JMf0fdHByh

-- Dumped from database version 17.6
-- Dumped by pg_dump version 18.3

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: facilities; Type: TABLE; Schema: zerocare_operational; Owner: postgres
--

CREATE TABLE zerocare_operational.facilities (
    facility_id uuid DEFAULT gen_random_uuid() NOT NULL,
    group_id uuid NOT NULL,
    facility_code text NOT NULL,
    facility_name text NOT NULL,
    facility_type text NOT NULL,
    city text NOT NULL,
    district text,
    address text,
    latitude numeric,
    longitude numeric,
    opened_year integer,
    bed_count integer,
    gross_area_m2 numeric,
    operating_hours_per_day integer DEFAULT 24 NOT NULL,
    owner_operator text,
    grid_connection_type text,
    notes text,
    is_active boolean DEFAULT true NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL
);


ALTER TABLE zerocare_operational.facilities OWNER TO postgres;

--
-- Name: hospital_intake_requests; Type: TABLE; Schema: zerocare_operational; Owner: postgres
--

CREATE TABLE zerocare_operational.hospital_intake_requests (
    intake_id uuid DEFAULT gen_random_uuid() NOT NULL,
    facility_code text DEFAULT 'bazekol'::text NOT NULL,
    hospital_name text NOT NULL,
    contact_name text,
    contact_title text,
    contact_email text,
    contact_phone text,
    facility_type text,
    bed_count integer,
    employee_count integer,
    daily_patient_count integer,
    requested_modules text[] DEFAULT '{}'::text[] NOT NULL,
    current_systems text,
    priority_level text DEFAULT 'normal'::text NOT NULL,
    notes text,
    intake_status text DEFAULT 'new'::text NOT NULL,
    source_channel text DEFAULT 'dashboard'::text NOT NULL,
    created_at timestamp with time zone DEFAULT now() NOT NULL,
    updated_at timestamp with time zone DEFAULT now() NOT NULL,
    CONSTRAINT chk_bed_count CHECK (((bed_count IS NULL) OR (bed_count >= 0))),
    CONSTRAINT chk_daily_patient_count CHECK (((daily_patient_count IS NULL) OR (daily_patient_count >= 0))),
    CONSTRAINT chk_employee_count CHECK (((employee_count IS NULL) OR (employee_count >= 0))),
    CONSTRAINT chk_intake_status CHECK ((intake_status = ANY (ARRAY['new'::text, 'qualified'::text, 'in_review'::text, 'approved'::text, 'rejected'::text]))),
    CONSTRAINT chk_priority_level CHECK ((priority_level = ANY (ARRAY['low'::text, 'normal'::text, 'high'::text, 'critical'::text])))
);


ALTER TABLE zerocare_operational.hospital_intake_requests OWNER TO postgres;

--
-- Data for Name: facilities; Type: TABLE DATA; Schema: zerocare_operational; Owner: postgres
--

COPY zerocare_operational.facilities (facility_id, group_id, facility_code, facility_name, facility_type, city, district, address, latitude, longitude, opened_year, bed_count, gross_area_m2, operating_hours_per_day, owner_operator, grid_connection_type, notes, is_active, created_at, updated_at) FROM stdin;
dcb4f794-50c4-4b9e-82de-ce66266352b0	fe5273f8-4216-46d7-bc84-460b9c3492a6	CIGLI_HOSP	Bazekol Çiğli Hastanesi	hospital	İzmir	Çiğli	\N	\N	\N	\N	250	34000	24	\N	distribution	Ana hastane varsayımsal başlangıç	t	2026-04-01 14:53:49.953756+00	2026-04-01 14:53:49.953756+00
e5ea12d8-872a-45bc-ad14-47f9a2699fa4	fe5273f8-4216-46d7-bc84-460b9c3492a6	SADA_HOSP	Bazekol Sada Hastanesi	hospital	İzmir	Bornova	\N	\N	\N	\N	120	18000	24	\N	distribution	Varsayımsal başlangıç	t	2026-04-01 14:53:49.953756+00	2026-04-01 14:53:49.953756+00
0bfa880a-74f4-4979-ab0c-14793db37f3c	fe5273f8-4216-46d7-bc84-460b9c3492a6	EYE_CENTER	Bazekol Göz Tıp Merkezi	eye_center	İzmir	Bornova	\N	\N	\N	\N	\N	4500	24	\N	distribution	Varsayımsal başlangıç	t	2026-04-01 14:53:49.953756+00	2026-04-01 14:53:49.953756+00
7b4f8d89-2e24-4a62-bbe3-4f05fa7524fa	fe5273f8-4216-46d7-bc84-460b9c3492a6	CIGLI_MED	Bazekol Çiğli Tıp Merkezi	medical_center	İzmir	Çiğli	\N	\N	\N	\N	\N	3500	24	\N	distribution	Varsayımsal başlangıç	t	2026-04-01 14:53:49.953756+00	2026-04-01 14:53:49.953756+00
b368469b-2d85-4db9-8f2e-2fbc43b68347	fe5273f8-4216-46d7-bc84-460b9c3492a6	DENTAL_CENTER	Bazekol Ağız ve Diş Sağlığı Merkezi	dental_center	İzmir	Çiğli	\N	\N	\N	\N	\N	3200	24	\N	distribution	Varsayımsal başlangıç	t	2026-04-01 14:53:49.953756+00	2026-04-01 14:53:49.953756+00
c5a238a3-6843-4d39-b7e3-e2fe0bf51069	fe5273f8-4216-46d7-bc84-460b9c3492a6	BALCOVA_MED	Bazekol Balçova Tıp Merkezi	medical_center	İzmir	Balçova	\N	\N	\N	\N	\N	3800	24	\N	distribution	Varsayımsal başlangıç	t	2026-04-01 14:53:49.953756+00	2026-04-01 14:53:49.953756+00
\.


--
-- Data for Name: hospital_intake_requests; Type: TABLE DATA; Schema: zerocare_operational; Owner: postgres
--

COPY zerocare_operational.hospital_intake_requests (intake_id, facility_code, hospital_name, contact_name, contact_title, contact_email, contact_phone, facility_type, bed_count, employee_count, daily_patient_count, requested_modules, current_systems, priority_level, notes, intake_status, source_channel, created_at, updated_at) FROM stdin;
4a2df80e-31b3-4ad4-88b9-77ca999a6db7	bazekol	Demo Hospital	Cem Onat	Founder	cem@example.com	+90 555 000 0000	private_hospital	220	480	950	{dashboard,waste,water,co2}	Excel + manual reporting	high	Demo intake test kaydi	new	dashboard	2026-04-03 09:52:44.993252+00	2026-04-03 09:52:44.993252+00
\.


--
-- Name: facilities facilities_group_id_facility_code_key; Type: CONSTRAINT; Schema: zerocare_operational; Owner: postgres
--

ALTER TABLE ONLY zerocare_operational.facilities
    ADD CONSTRAINT facilities_group_id_facility_code_key UNIQUE (group_id, facility_code);


--
-- Name: facilities facilities_pkey; Type: CONSTRAINT; Schema: zerocare_operational; Owner: postgres
--

ALTER TABLE ONLY zerocare_operational.facilities
    ADD CONSTRAINT facilities_pkey PRIMARY KEY (facility_id);


--
-- Name: hospital_intake_requests hospital_intake_requests_pkey; Type: CONSTRAINT; Schema: zerocare_operational; Owner: postgres
--

ALTER TABLE ONLY zerocare_operational.hospital_intake_requests
    ADD CONSTRAINT hospital_intake_requests_pkey PRIMARY KEY (intake_id);


--
-- Name: idx_facilities_group; Type: INDEX; Schema: zerocare_operational; Owner: postgres
--

CREATE INDEX idx_facilities_group ON zerocare_operational.facilities USING btree (group_id, facility_code);


--
-- Name: facilities facilities_group_id_fkey; Type: FK CONSTRAINT; Schema: zerocare_operational; Owner: postgres
--

ALTER TABLE ONLY zerocare_operational.facilities
    ADD CONSTRAINT facilities_group_id_fkey FOREIGN KEY (group_id) REFERENCES zerocare_operational.groups(group_id) ON DELETE CASCADE;


--
-- PostgreSQL database dump complete
--

\unrestrict 7iMiofKaaveb1NblddaJPpdWdLxXB465hs57JL77pdIN5e65WMI99JMf0fdHByh

