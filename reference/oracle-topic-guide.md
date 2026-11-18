# Oracle SQL & PL/SQL Topic Guide

Based on `Simar_Sabharwal_Oracle_Unitwise_SPOOL_Transcript_ERP-0251BCA022.docx` (Lab on Oracle):

## 1. Unit Breakdown
- **Unit I: Basic SQL Queries (15 Practicals)**
  - EMP & DEPT table queries
  - SELECT *, specific columns, DISTINCT jobs/departments
  - Column aliases, arithmetic expressions (annual salary, commissions)
  - Handling NULL values with `NVL()`
  - Ordering results (`ORDER BY ASC/DESC`, multi-column ordering)

- **Unit II: DDL, DML, DCL, TCL & Constraints (15 Practicals)**
  - DDL: `CREATE TABLE`, `ALTER TABLE` (`ADD`, `MODIFY`, `DROP COLUMN`, `RENAME`), `DROP TABLE`, `TRUNCATE TABLE`
  - DML: `INSERT INTO`, `UPDATE ... SET`, `DELETE FROM`
  - Constraints: `PRIMARY KEY`, `FOREIGN KEY (REFERENCES)`, `UNIQUE`, `NOT NULL`, `CHECK`
  - TCL: `COMMIT`, `ROLLBACK`, `SAVEPOINT`

- **Unit III: Operators, Searching & Set Operators (15 Practicals)**
  - Comparison & Logical: `=`, `!=` / `<>`, `>`, `<`, `>=`, `<=`, `AND`, `OR`, `NOT`
  - Range & List: `BETWEEN ... AND ...`, `NOT BETWEEN`, `IN (...)`, `NOT IN (...)`
  - Pattern Matching: `LIKE '%abc%'`, `LIKE '_a%'` (wildcards `%` and `_`)
  - Null Checking: `IS NULL`, `IS NOT NULL`
  - Set Operators: `UNION`, `UNION ALL`, `INTERSECT`, `MINUS`

- **Unit IV: Group Functions, Subqueries & Joins (15 Practicals)**
  - Aggregate Functions: `COUNT(*)`, `COUNT(col)`, `SUM()`, `AVG()`, `MIN()`, `MAX()`
  - Grouping: `GROUP BY col`, `HAVING` clause
  - Joins: Equi-join / Inner Join, Cartesian (Cross) Join, Self Join, Outer Joins (`LEFT OUTER JOIN`, `RIGHT OUTER JOIN`, `FULL OUTER JOIN`, Oracle `(+)` syntax)
  - Subqueries: Single-row (`=`, `>`, `<`), Multi-row (`IN`, `ANY`, `ALL`), Correlated subqueries

- **Unit V: Views, Sequences & Indexes (15 Practicals)**
  - Views: `CREATE VIEW`, `WITH CHECK OPTION`, `WITH READ ONLY`, `DROP VIEW`, DML through views
  - Sequences: `CREATE SEQUENCE ... START WITH ... INCREMENT BY ...`, `.NEXTVAL`, `.CURRVAL`, `ALTER SEQUENCE`, `DROP SEQUENCE`
  - Indexes: `CREATE INDEX`, `CREATE UNIQUE INDEX`, `DROP INDEX`

- **PL/SQL Extension (Practicals & Exam questions)**
  - Anonymous PL/SQL blocks (`DECLARE`, `BEGIN`, `EXCEPTION`, `END; /`)
  - Explicit & Implicit Cursors (`%FOUND`, `%NOTFOUND`, `%ROWCOUNT`)
  - Stored Procedures, Functions, and Triggers
