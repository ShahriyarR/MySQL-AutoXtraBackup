use alter_enc_inc;

ALTER TABLE t1 ADD COLUMN b INT DEFAULT 2;
ALTER TABLE t2 ADD COLUMN b INT DEFAULT 2;
ALTER TABLE t7 ADD COLUMN b INT DEFAULT 2;
ALTER TABLE t1 ADD KEY a(a), ADD KEY b(b);
ALTER TABLE t2 ADD KEY a(a), ADD KEY b(b);
ALTER TABLE t3 ADD COLUMN c INT DEFAULT 5;
ALTER TABLE t4 ADD COLUMN c INT DEFAULT 5;
ALTER TABLE t3 ADD KEY (a), ADD KEY c(c);
ALTER TABLE t4 ADD KEY (a), ADD KEY c(c);
ALTER TABLE t5 ADD FULLTEXT(a);
ALTER TABLE t6 ADD FULLTEXT(a);
ALTER TABLE t7 ADD KEY a(a), ADD KEY b(b);

alter table t1 drop column b;
alter table t2 drop column b;
alter table t7 drop column b;

ALTER TABLE t1 drop KEY a;
ALTER TABLE t1 drop KEY b;
ALTER TABLE t2 drop KEY a;
ALTER TABLE t2 drop KEY b;

ALTER TABLE t3 drop COLUMN c;
ALTER TABLE t4 drop COLUMN c;

ALTER TABLE t3 drop KEY a;
ALTER TABLE t3 drop KEY c;

ALTER TABLE t4 drop KEY a;
ALTER TABLE t4 drop KEY c;
alter table t5 drop key a;
alter table t6 drop key a;

ALTER TABLE t7 drop KEY a;
ALTER TABLE t7 drop KEY c;

