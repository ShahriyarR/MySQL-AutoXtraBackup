create database alter_enc_inc;
use alter_enc_inc;


CREATE TABLE t1 (id INT NOT NULL PRIMARY KEY, a VARCHAR(255)) ENGINE=InnoDB ENCRYPTION='y';
CREATE TABLE t2 (id INT NOT NULL PRIMARY KEY, a VARCHAR(255)) ENGINE=InnoDB;
CREATE TABLE t3 (id INT, a VARCHAR(255)) ENGINE=InnoDB ENCRYPTION='y';
CREATE TABLE t4 (id INT, a VARCHAR(255)) ENGINE=InnoDB;
CREATE TABLE t5 (id INT NOT NULL PRIMARY KEY, a TEXT(500), b VARCHAR(255), FULLTEXT(b)) ENGINE=InnoDB ENCRYPTION='y';
CREATE TABLE t6 (id INT, a TEXT(500), b VARCHAR(255), FULLTEXT(b)) ENGINE=InnoDB;
CREATE TABLE t7 (id INT NOT NULL PRIMARY KEY, a VARCHAR(255)) ENGINE=InnoDB ROW_FORMAT=COMPRESSED ENCRYPTION='y';

DELIMITER //
CREATE PROCEDURE innodb_insert_proc (repeat_count INT)
BEGIN
  DECLARE current_num INT;
  SET current_num = 0;
  WHILE current_num < repeat_count DO
    INSERT INTO t1 VALUES (current_num, REPEAT('foobar', 42));
    INSERT INTO t2 VALUES (current_num, REPEAT('temp', 42));
    INSERT INTO t3 VALUES (current_num, REPEAT('barfoo', 42));
    INSERT INTO t4 VALUES (current_num, REPEAT('repeat', 42));
    INSERT INTO t5 VALUES (current_num, SUBSTRING('A BC DEF GHIJ KLM NOPQRS TUV WXYZ 012 3456789', RAND() * 36 + 1, 100), REPEAT('author new', 22));
    INSERT INTO t6 VALUES (current_num, SUBSTRING('A BC DEF GHIJ KLM NOPQRS TUV WXYZ 012 3456789', RAND() * 36 + 1, 100), REPEAT('mangled old', 22));
    INSERT INTO t7 VALUES (current_num, REPEAT('mysql', 42));
    SET current_num = current_num + 1;
  END WHILE;
END//
DELIMITER ;
COMMIT;

SET autocommit=0;
CALL innodb_insert_proc(15000);
COMMIT;
SET autocommit=1;