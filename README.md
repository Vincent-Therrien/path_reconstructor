# Path Reconstructor
Static source code based log monitoring enhancer.

Logs are character strings produced during the execution of program that
document software behaviors. They are used to monitor systems in DevOps
contexts, among others, to:
- Detect anomalies
- Perform root cause analysis
- Find performance regressions

Most of these applications rely only on **logs themselves** and do not use
additional information to better interpret logs. This project aims at improving
log-based software monitoring with static source code analysis. More precisely,
the execution path of a program is reconstructed from (1) runtime logs and (2)
a statically compiled call graph. This execution path yields a deeper
understanding of the system's behavior.
