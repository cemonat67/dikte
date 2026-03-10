INSERT INTO processes (category, stage_group, stage, process_name, unit, description, applied_products)
VALUES
('Fiber', 'Raw Material', 'Fiber Input', 'Cotton Fiber Production', 'kg', 'Primary cotton fiber input stage', 'T-shirt, Hoodie, Sweatshirt'),
('Yarn', 'Spinning', 'Ring Spinning', 'Ring Spinning', 'kg', 'Conversion of fiber to yarn', 'Knits, Jerseys, Basics'),
('Fabric', 'Knitting', 'Single Jersey', 'Single Jersey Knitting', 'kg', 'Knitting process for jersey fabric', 'T-shirt, Activewear'),
('Wet Processing', 'Dyeing', 'Reactive Dyeing', 'Reactive Dyeing', 'kg', 'Fabric dyeing process', 'Garment dyed fabrics'),
('Wet Processing', 'Finishing', 'Compacting', 'Compacting / Finishing', 'kg', 'Final finishing and stabilization', 'All knit fabrics'),
('Garment', 'Cutting & Sewing', 'Assembly', 'Cutting & Sewing', 'piece', 'Garment assembly stage', 'T-shirt, Polo, Hoodie'),
('Logistics', 'Packaging', 'Packing', 'Packaging', 'piece', 'Final packaging before shipment', 'All products');
