INSERT INTO emissions (process_id, min_co2_kg, max_co2_kg, avg_co2_kg, source, source_file, notes)
SELECT id, 1.8000, 2.5000, 2.1000, 'Synthetic Seed', '002_emissions.sql', 'Baseline cotton fiber factor'
FROM processes WHERE process_name = 'Cotton Fiber Production';

INSERT INTO emissions (process_id, min_co2_kg, max_co2_kg, avg_co2_kg, source, source_file, notes)
SELECT id, 0.4000, 0.9000, 0.6500, 'Synthetic Seed', '002_emissions.sql', 'Ring spinning factor'
FROM processes WHERE process_name = 'Ring Spinning';

INSERT INTO emissions (process_id, min_co2_kg, max_co2_kg, avg_co2_kg, source, source_file, notes)
SELECT id, 0.3000, 0.7000, 0.5000, 'Synthetic Seed', '002_emissions.sql', 'Knitting factor'
FROM processes WHERE process_name = 'Single Jersey Knitting';

INSERT INTO emissions (process_id, min_co2_kg, max_co2_kg, avg_co2_kg, source, source_file, notes)
SELECT id, 1.2000, 2.4000, 1.7000, 'Synthetic Seed', '002_emissions.sql', 'Dyeing factor'
FROM processes WHERE process_name = 'Reactive Dyeing';

INSERT INTO emissions (process_id, min_co2_kg, max_co2_kg, avg_co2_kg, source, source_file, notes)
SELECT id, 0.2000, 0.5000, 0.3500, 'Synthetic Seed', '002_emissions.sql', 'Finishing factor'
FROM processes WHERE process_name = 'Compacting / Finishing';

INSERT INTO emissions (process_id, min_co2_kg, max_co2_kg, avg_co2_kg, source, source_file, notes)
SELECT id, 0.1500, 0.4000, 0.2500, 'Synthetic Seed', '002_emissions.sql', 'Assembly factor'
FROM processes WHERE process_name = 'Cutting & Sewing';

INSERT INTO emissions (process_id, min_co2_kg, max_co2_kg, avg_co2_kg, source, source_file, notes)
SELECT id, 0.0200, 0.0800, 0.0500, 'Synthetic Seed', '002_emissions.sql', 'Packaging factor'
FROM processes WHERE process_name = 'Packaging';
