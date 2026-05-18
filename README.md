# FSD Student Enrollment System

Language versions:

- [English](./README.md)
- [中文](./README.zh.md)
- [Tiếng Việt](./README.vi.md)

Student enrollment platform with both a Tkinter desktop client and a web client.
The system supports student registration, login, subject enrollment, grade display, and DeepSeek-powered study advice/chat.

## Features

- Student login and registration
- Subject enrollment and removal
- Grade and mean mark calculation
- AI study advice and chat using DeepSeek
- Desktop GUI version
- Web version with synchronous and async implementations
- Admin dashboard in the async web app

## Project Structure

- `GUI.py` - Tkinter desktop entry point
- `WebApp.py` - synchronous HTTP server entry point
- `AsyncWebApp.py` - FastAPI async web entry point
- `Services.py` - portal and AI service layer
- `Database.py` - database access helpers
- `models.py` - SQLAlchemy models and SQLite setup
- `migrate_csv_to_orm.py` - migrate CSV data into SQLite
- `students_data.csv` - seed/demo data
- `run_gui.sh` - launch the desktop app
- `run_web.sh` - launch the synchronous web app
- `run_async_web.sh` - launch the async web app

## Requirements

- Python 3.10+
- `pip`
- macOS for the provided shell scripts, because they use `open`
- A valid `DEEPSEEK_API_KEY` for AI chat/advice features

## Installation

Create and activate a virtual environment, then install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

If you want to use the Tkinter launcher scripts on macOS, the repo expects a separate environment named `.venv-tk`:

```bash
python -m venv .venv-tk
source .venv-tk/bin/activate
pip install -r requirements.txt
```

## DeepSeek API Key

The AI features read `DEEPSEEK_API_KEY` from either:

- your shell environment, or
- a local `.env` file in the project root

Copy `.env.example` to `.env` and replace the placeholder value with your real key.

Example `.env` entry:

```env
DEEPSEEK_API_KEY=your_api_key_here
```

## Running the Apps

### Desktop GUI

```bash
./run_gui.sh
```

### Synchronous web app

```bash
./run_web.sh
```

This script now forwards to the async web app launcher so admin login works.

Open:

```text
http://127.0.0.1:8001/login
```

### Async web app

```bash
./run_async_web.sh
```

This is the canonical web launcher and supports both student and admin login.

Open:

```text
http://127.0.0.1:8001/login
```

## Demo Credentials

- Admin: `admin` / `admin`
- Demo student: `zhuhang.li@university.com` / `Zhuhangli123`

## Database

The app uses SQLite and creates `students.db` automatically from the SQLAlchemy models.
If you want to import the CSV seed data into the database, run:

```bash
python migrate_csv_to_orm.py
```

To batch login all student accounts against the running web app, run:

```bash
.venv-tk/bin/python batch_login_students.py --base-url http://127.0.0.1:8001
```

To run a page-login concurrency test against the running web app:

```bash
.venv-tk/bin/python load_test.py --base-url http://127.0.0.1:8001 --mode page --concurrency 10 30 60
```

To test the FastAPI app in-process without using a socket:

```bash
.venv-tk/bin/python load_test.py --transport asgi --mode page --concurrency 10 30 60
```

## Notes

- The desktop UI is intentionally built with buttons because of Tk rendering constraints on this machine.
- The web app stores sessions in memory, so restarting the process clears active sessions.
- If you run on Linux or Windows, start the Python entry points directly instead of using the `.sh` scripts.
