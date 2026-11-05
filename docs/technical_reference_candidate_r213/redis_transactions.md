# Redis transactions and external databases
Source: https://redis.io/docs/latest/develop/using-commands/transactions/

MULTI and EXEC group Redis commands for isolated sequential execution. WATCH can abort EXEC when watched keys change. A Redis transaction does not create one atomic transaction spanning Redis and a separate SQL database. Cross-store consistency needs an application-level design.

