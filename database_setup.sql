CREATE DATABASE atm_system;

USE atm_system;

CREATE TABLE accounts (
    account_number INT PRIMARY KEY,
    name VARCHAR(100),
    pin VARCHAR(10),
    balance FLOAT
);

CREATE TABLE transactions (
    Id INT AUTO_INCREMENT PRIMARY KEY,
    account_number INT,
    Transaction_type VARCHAR(50),
    Amount FLOAT,
    Transaction_time DATETIME
);