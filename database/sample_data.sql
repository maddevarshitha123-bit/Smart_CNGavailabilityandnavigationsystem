-- SAMPLE DATA ONLY: names/coordinates are approximate and for demonstration.
-- Replace with real station details before any real use.
USE smart_cng;

INSERT INTO stations (station_id, name, address, latitude, longitude, phone, operating_hours, status) VALUES
(1, 'Sample CNG - Tarnaka',      'Tarnaka, Secunderabad, Hyderabad',        17.428000, 78.531000, '9000000001', '06:00-22:00', 'open'),
(2, 'Sample CNG - Uppal',        'Uppal Ring Road, Hyderabad',              17.401000, 78.559000, '9000000002', '06:00-22:00', 'open'),
(3, 'Sample CNG - Kukatpally',   'Kukatpally Housing Board, Hyderabad',     17.494000, 78.399000, '9000000003', '05:00-23:00', 'open'),
(4, 'Sample CNG - LB Nagar',     'LB Nagar Junction, Hyderabad',            17.347000, 78.552000, '9000000004', '06:00-22:00', 'open'),
(5, 'Sample CNG - Gachibowli',   'Gachibowli, Hyderabad',                   17.440000, 78.349000, '9000000005', '24 hours',    'open'),
(6, 'Sample CNG - Secunderabad', 'Near Secunderabad Railway Station',       17.434000, 78.501000, '9000000006', '06:00-21:00', 'maintenance')
ON DUPLICATE KEY UPDATE name = VALUES(name);

INSERT INTO station_status (station_id, availability, queue_length, waiting_time, traffic_level) VALUES
(1, 'High',   4, 8,  'Medium'),
(2, 'Medium', 9, 20, 'High'),
(3, 'Low',   14, 35, 'High'),
(4, 'High',   3, 6,  'Low'),
(5, 'Medium', 7, 15, 'Medium'),
(6, 'Low',    0, 0,  'Low');
