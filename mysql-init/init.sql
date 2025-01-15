-- Drop existing tables to ensure a clean setup
CREATE DATABASE IF NOT EXISTS task_management;
USE task_management;

DROP TABLE IF EXISTS tasks;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS roles;

-- Create the Roles table
CREATE TABLE IF NOT EXISTS roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

-- Create the Users table
CREATE TABLE IF NOT EXISTS users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
	username VARCHAR(100) NOT NULL UNIQUE,
    role_id INT NOT NULL,
    password VARCHAR(100) NOT NULL,
    CONSTRAINT fk_role_id FOREIGN KEY (role_id) REFERENCES roles(role_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    assignee_id INT NULL,
    task_name TEXT NOT NULL,
    task_description TEXT NULL,
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date DATE NULL,
    status ENUM('pending', 'in_progress', 'completed') NOT NULL DEFAULT 'pending',
    CONSTRAINT fk_assignee_id FOREIGN KEY (assignee_id) REFERENCES users(user_id) ON DELETE CASCADE
);

INSERT INTO roles (role_name) VALUES
('Employer'),
('Employee');

INSERT INTO users (username, role_id, password) VALUES
('employer_user', 1, 'hashed_password_employer'),
('employee_user', 2, 'hashed_password_employee');

-- Insert example tasks
INSERT INTO tasks (assignee_id, task_name, task_description, due_date, status) VALUES
(1, 'Task 1', 'Complete the initial report.', '2025-01-20', 'pending'),
(1, 'Task 2', 'Update the client documentation.', '2025-01-25', 'in_progress'),
(2, 'Task 3', 'Prepare for the team meeting.', '2025-01-18', 'completed');
