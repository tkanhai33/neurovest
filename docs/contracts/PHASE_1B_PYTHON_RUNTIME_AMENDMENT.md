# Phase 1B Python Runtime Amendment

## Development Runtime

Primary runtime:

Python 3.14

## Fallback Runtime

Python 3.12 may be used later if a required dependency proves incompatible with Python 3.14.

## Reason

The current development machine:

- Ubuntu 26.04
- System Python: 3.14.4

Using the system Python avoids:

- maintaining multiple Python installations
- custom repositories
- unnecessary complexity

## Contract Rule

Development proceeds on Python 3.14 unless package compatibility requires reverting to Python 3.12.
