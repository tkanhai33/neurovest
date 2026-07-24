
Contributing to NeuroVest
Architecture-first rule

Changes must extend the existing NeuroVest structure.

Do not create duplicate services, parallel runtimes, shadow routes, alternate persistence layers, or new architectural systems when an existing stack already owns the behavior.

Protected capability boundaries

The following remain restricted:

live brokerage execution;
autonomous trading;
autonomous source mutation;
autonomous deployment;
autonomous risk override;
secret or credential exposure;
bypass of identity, approval, audit, or risk controls.

Code presence does not equal runtime approval.

Required workflow

Before modifying a critical boundary:

inspect the exact source and call shape;
identify the canonical owning stack;
archive affected files;
apply the smallest targeted change;
compile changed sources;
run focused tests;
run the affected stack's complete tests;
verify application import or build;
run runtime qualification when behavior changes;
preserve a report and disposition.
Git safety

Do not use destructive cleanup commands to resolve an unfamiliar working tree.

Do not run:

git clean
git reset --hard

unless a separately verified recovery plan explicitly requires it.

Testing

A change is incomplete until relevant tests pass.

Runtime-sensitive changes must test successful and fail-closed behavior.

Pull requests

Every pull request must state:

architecture ownership;
safety impact;
exact verification;
data or migration impact;
release classification;
unresolved risks.

Production, live brokerage, and AI autonomy require separate qualification and approval.
