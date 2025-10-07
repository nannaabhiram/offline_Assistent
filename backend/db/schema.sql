CREATE TABLE IF NOT EXISTS tasks (
    id INT AUTO_INCREMENT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status ENUM('pending','done') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date DATETIME NULL
);

DROP TABLE IF EXISTS reminders;
CREATE TABLE reminders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    remind_time DATETIME NOT NULL,
    notified TINYINT DEFAULT 0,
    text VARCHAR(255) NOT NULL
);

CREATE TABLE IF NOT EXISTS conversations (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_input TEXT,
    assistant_response TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    action VARCHAR(255) NOT NULL,
    status ENUM('success','fail') DEFAULT 'success',
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Track deleted tasks history
CREATE TABLE IF NOT EXISTS deleted_tasks (
    id INT PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    status ENUM('pending','done') DEFAULT 'pending',
    due_date DATETIME NULL,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);



