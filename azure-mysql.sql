CREATE TABLE users (
  id INT PRIMARY KEY IDENTITY(1,1),
  email VARCHAR(50) NOT NULL,
  password VARCHAR(50) NOT NULL,
);

CREATE TABLE entries (
  id INT PRIMARY KEY IDENTITY(1,1),
  title VARCHAR(255) NOT NULL,
  content TEXT NOT NULL,
  date DATETIME,
  email VARCHAR(50)
);

INSERT INTO users (email, password)
VALUES 
  ('saurabh@ficticious.com', '1122'),
  ('dakshata@ficticious.com', '12345'),
  ('bill@ficticious.com', '123'),
  ('kiansh@ficticious.com', '801256');


DROP TABLE users;

SELECT * FROM users;

SELECT * FROM entries;
