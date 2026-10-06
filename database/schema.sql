CREATE DATABASE IF NOT EXISTS smart_cng CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE smart_cng;

CREATE TABLE IF NOT EXISTS users (
    user_id       INT AUTO_INCREMENT PRIMARY KEY,
    name          VARCHAR(100) NOT NULL,
    email         VARCHAR(150) NOT NULL UNIQUE,
    password_hash VARCHAR(255) NOT NULL,
    role          ENUM('user','admin') NOT NULL DEFAULT 'user',
    created_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS stations (
    station_id      INT AUTO_INCREMENT PRIMARY KEY,
    name            VARCHAR(150) NOT NULL,
    address         VARCHAR(255) NOT NULL,
    latitude        DECIMAL(9,6) NOT NULL,
    longitude       DECIMAL(9,6) NOT NULL,
    phone           VARCHAR(20),
    operating_hours VARCHAR(60) DEFAULT '06:00-22:00',
    status          ENUM('open','closed','maintenance') NOT NULL DEFAULT 'open',
    CONSTRAINT chk_lat CHECK (latitude  BETWEEN -90  AND 90),
    CONSTRAINT chk_lon CHECK (longitude BETWEEN -180 AND 180)
);

CREATE TABLE IF NOT EXISTS station_status (
    status_id     INT AUTO_INCREMENT PRIMARY KEY,
    station_id    INT NOT NULL,
    availability  ENUM('High','Medium','Low') NOT NULL,
    queue_length  INT NOT NULL DEFAULT 0,
    waiting_time  INT NOT NULL DEFAULT 0,
    traffic_level ENUM('Low','Medium','High') NOT NULL DEFAULT 'Medium',
    updated_at    TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(station_id) ON DELETE CASCADE,
    INDEX idx_status_station_time (station_id, updated_at)
);

CREATE TABLE IF NOT EXISTS prediction_history (
    prediction_id          INT AUTO_INCREMENT PRIMARY KEY,
    station_id             INT NOT NULL,
    predicted_availability ENUM('High','Medium','Low') NOT NULL,
    predicted_waiting_time INT NOT NULL,
    prediction_time        TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (station_id) REFERENCES stations(station_id) ON DELETE CASCADE,
    INDEX idx_pred_station_time (station_id, prediction_time)
);
