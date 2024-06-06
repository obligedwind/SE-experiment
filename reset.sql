\c postgres

drop database software ;

drop role u123;

drop role u345;

drop role u456;

create database software;

\c software

create table global_merge (id VARCHAR(20), i int, oprand VARCHAR(6), val_1 VARCHAR(20), val_2 VARCHAR(100));

GRANT SELECT ON global_merge TO PUBLIC;

GRANT INSERT ON global_merge TO PUBLIC;

GRANT DELETE ON global_merge TO PUBLIC;

create table global_view (id VARCHAR(20) PRIMARY KEY, name VARCHAR(100), page VARCHAR(100), phone INT);

GRANT SELECT ON global_view TO PUBLIC;

GRANT INSERT ON global_view TO PUBLIC;

GRANT DELETE ON global_view TO PUBLIC;

GRANT UPDATE ON global_view TO public;


CREATE TABLE global_relation (id_t VARCHAR(20) , id_s VARCHAR(20) , time VARCHAR(20), PRIMARY KEY (id_t, id_s)
,FOREIGN KEY (id_t) REFERENCES global_view(id), FOREIGN KEY (id_s) REFERENCES global_view(id));

GRANT SELECT ON global_relation TO PUBLIC;

GRANT INSERT ON global_relation TO PUBLIC;

GRANT DELETE ON global_relation TO PUBLIC;

GRANT UPDATE ON global_relation TO public;
