# PostgreSQL explicit transactions
Source: https://www.postgresql.org/docs/18/tutorial-transactions.html

An explicit transaction groups statements between BEGIN and COMMIT. If a statement error puts the transaction block into the aborted state, issue ROLLBACK or recover with ROLLBACK TO SAVEPOINT before continuing. Do not claim a failed statement automatically commits or independently rolls back the whole explicit transaction.

