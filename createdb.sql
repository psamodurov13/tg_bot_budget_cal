CREATE TABLE groups (
    group_id VARCHAR(255) PRIMARY KEY,
    group_name VARCHAR(255),
)

CREATE TABLE operations (
    operation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation_price INTEGER,
    operation_name VARCHAR(255),
    operation_group INTEGER,
    operation_data DATE,
    operation_user INTEGER
)