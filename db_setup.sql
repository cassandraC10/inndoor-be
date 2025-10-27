-- Create the database
CREATE DATABASE IF NOT EXISTS inndoor_db
CHARACTER SET utf8mb4
COLLATE utf8mb4_unicode_ci;

-- Create user and grant privileges (change password!)
CREATE USER IF NOT EXISTS 'inndoor_user'@'localhost' 
IDENTIFIED BY 'your_secure_password_here';

-- Grant privileges to the user
GRANT ALL PRIVILEGES ON inndoor_db.* TO 'inndoor_user'@'localhost';

-- Apply privileges
FLUSH PRIVILEGES;