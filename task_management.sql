-- Drop existing tables to ensure a clean setup
DROP TABLE IF EXISTS Tasks;
DROP TABLE IF EXISTS Users;
DROP TABLE IF EXISTS Roles;

-- Create the Roles table
CREATE TABLE IF NOT EXISTS Roles (
    role_id INT AUTO_INCREMENT PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

-- Create the Users table
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
	username VARCHAR(100) NOT NULL UNIQUE,
    role_id INT NOT NULL,
    password VARCHAR(100) NOT NULL,
    FOREIGN KEY (role_id) REFERENCES Roles(role_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS Tasks (
    task_id INT AUTO_INCREMENT PRIMARY KEY,
    assignee_id INT NULL,
    task_name TEXT NOT NULL,
    task_description TEXT NULL,
    creation_date TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP,
    due_date DATE NULL,
    status ENUM('Pending', 'In Progress', 'Completed') NOT NULL DEFAULT 'Pending',
    FOREIGN KEY (assignee_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

INSERT INTO Roles (role_name) VALUES
('Employer'),
('Employee');

INSERT INTO Users (username, role_id, password) VALUES
('employer_user', 1, 'hashed_password_employer'),
('employee_user', 2, 'hashed_password_employee');

-- Insert example tasks
INSERT INTO Tasks (assignee_id, task_name, task_description, due_date, status) VALUES
(1, 'Task 1', 'Complete the initial report.', '2025-01-20', 'Pending'),
(1, 'Task 2', 'Update the client documentation.', '2025-01-25', 'In Progress'),
(2, 'Task 3', 'Prepare for the team meeting.', '2025-01-18', 'Completed');

-- Query to verify setup
SELECT * FROM Roles;
SELECT * FROM Users;
SELECT * FROM Tasks;