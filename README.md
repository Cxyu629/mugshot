# MUGSHOT: Mouse Using GestureS and Head Orientation Tracker

Hack&Roll 2025 Submission

This project uses CV methods to detect and track facial features in real time, and uses the positions and changes in these features to trigger mouse events.

Essentially, your face becomes a mouse.

## Prerequisites

Requires python version >= 3.12.

Requires familiarity with using Git (alternatively, use only clone, commit, push, pull, and fetch).

Requires [CMAKE](https://cmake.org/download/) (for building the dlib package).

## Development

0. Ensure that your GitHub account is set up properly, following [this guide from GitHub](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/about-authentication-to-github).

1. Open your preferred directory in a command line.

   - Run `git clone https://github.com/Cxyu629/hacknroll-2025.git`
   - Alternatively, clone the repository in any way you prefer.

2. Create a virtual environment in the `/.venv/` directory for the project:

   `<python path> -m venv .venv`

   - `<python path>` is the path to a python installation (or just `py`/`python`/`python.exe` if it's already in your PATH).

3. Activate the virtual environment.

   - In PowerShell (PS):
     `.venv/Scripts/activate`
   - In Command Prompt (CMD):
     `".venv/Scripts/activate"`
   - In Bash:
     `source .venv/Scripts/activate`

4. Update pip to the latest version:
   `<python path> -m pip install -U pip`

5. Install all development dependencies

   - In PS/CMD:
     `pip install -U -e .[dev]`
   - In Bash:
     `<python path> -m pip install -U -e .[dev]`

6. To deactivate the virtual environment:
   `deactivate`

### Tools

For the following development-specific commands, try prepending `python.exe -m ` if it doesn't work.

- `black ./src` to **format files** in `./src` .
- `pytest` to **run tests** in `./tests` , or use `pytest tests/test_<functionality>.py` to run specific test files.
  - Replace `<functionality>` with the rest of the filename

### Adding Dependencies

In `pyproject.toml`, locate the `[project]` table.

Under the `dependencies` key, add to the list of package dependencies as stated in [PEP 508](https://peps.python.org/pep-0508)

## Building

1. Set up the development environment as written above.
2. Run `<python path> -m build` . The built package will be stored in the `/dist/` directory.

## Running

After installing the package, run `<python path> -m mugshot` .
