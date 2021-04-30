What is new in 2.0 major version?
=================================

Let me put it concise
---------------------

The whole project was completely rewritten. It is incompatible with previous versions.
Just imagine nearly 6754 lines of code was thrown and only 3200 was added.

Added mypy, black, flake8 and now our project is fully typed and has support with type checkers.
Removed Pipenv, setup.py and added pyproject.yaml with flint support.
There is a scripts folder with helper scripts if you decide to contribute.

We have experimental API based on FastAPI to use Docker container and
it should give the possibility to take and prepare the backups via API calls.(experimental not ready)