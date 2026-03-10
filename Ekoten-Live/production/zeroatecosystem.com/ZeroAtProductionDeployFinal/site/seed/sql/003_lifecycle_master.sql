INSERT INTO lifecycle_master
(upper_category, category, stage_group, stage, process_name, input_material, unit, description, applied_products, min_co2_kg, max_co2_kg, avg_co2_kg, notes, source, source_file)
VALUES
('Material', 'Fiber', 'Raw Material', 'Fiber Input', 'Cotton Fiber Production', 'Raw Cotton', 'kg', 'Primary fiber production', 'T-shirt, Hoodie, Sweatshirt', 1.8000, 2.5000, 2.1000, 'Synthetic baseline', 'Synthetic Seed', '003_lifecycle_master.sql'),
('Material', 'Yarn', 'Spinning', 'Ring Spinning', 'Ring Spinning', 'Cotton Fiber', 'kg', 'Yarn production stage', 'Knits, Jerseys, Basics', 0.4000, 0.9000, 0.6500, 'Synthetic baseline', 'Synthetic Seed', '003_lifecycle_master.sql'),
('Material', 'Fabric', 'Knitting', 'Single Jersey', 'Single Jersey Knitting', 'Cotton Yarn', 'kg', 'Fabric formation stage', 'T-shirt, Activewear', 0.3000, 0.7000, 0.5000, 'Synthetic baseline', 'Synthetic Seed', '003_lifecycle_master.sql'),
('Processing', 'Wet Processing', 'Dyeing', 'Reactive Dyeing', 'Reactive Dyeing', 'Greige Fabric', 'kg', 'Fabric coloration stage', 'Dyed knitwear', 1.2000, 2.4000, 1.7000, 'Synthetic baseline', 'Synthetic Seed', '003_lifecycle_master.sql'),
('Processing', 'Wet Processing', 'Finishing', 'Compacting', 'Compacting / Finishing', 'Dyed Fabric', 'kg', 'Fabric stabilization and finishing', 'All knit fabrics', 0.2000, 0.5000, 0.3500, 'Synthetic baseline', 'Synthetic Seed', '003_lifecycle_master.sql'),
('Manufacturing', 'Garment', 'Cutting & Sewing', 'Assembly', 'Cutting & Sewing', 'Finished Fabric', 'piece', 'Garment manufacturing stage', 'T-shirt, Polo, Hoodie', 0.1500, 0.4000, 0.2500, 'Synthetic baseline', 'Synthetic Seed', '003_lifecycle_master.sql'),
('Distribution', 'Logistics', 'Packaging', 'Packing', 'Packaging', 'Final Garment', 'piece', 'Packaging before shipment', 'All products', 0.0200, 0.0800, 0.0500, 'Synthetic baseline', 'Synthetic Seed', '003_lifecycle_master.sql');
