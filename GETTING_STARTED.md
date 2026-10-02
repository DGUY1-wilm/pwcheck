# Getting Started

A beginner-friendly guide to downloading and running pwcheck on your own computer. No programming experience needed.

## What you need

- A computer (Windows, Mac, or Linux)
- Python 3.9 or newer. Check by opening a terminal and typing `python --version`. If you don't have it, download it from https://www.python.org/downloads/ (on Windows, tick **"Add Python to PATH"** during install).

## Step 1: Download the project

1. Go to https://github.com/DGUY1-wilm/pwcheck
2. Click the green **Code** button
3. Click **Download ZIP**
4. Unzip the file (right-click, then "Extract All" on Windows)

## Step 2: Open a terminal in the project folder

**Windows:** Open the unzipped folder in File Explorer, click the address bar at the top, type `cmd`, and press Enter.

**Mac:** Right-click the folder, then choose **New Terminal at Folder**.

**Linux:** Right-click inside the folder, then choose **Open in Terminal**.

Make sure the folder you're in contains a file called `pyproject.toml`.

## Step 3: Set up a virtual environment

This keeps the project separate from the rest of your computer.

**Windows:**
```
python -m venv .venv
.venv\Scripts\activate
```

**Mac / Linux:**
```
python3 -m venv .venv
source .venv/bin/activate
```

You should now see `(.venv)` at the start of your terminal line.

## Step 4: Install the project

```
pip install -e ".[dev]"
```

## Step 5: Run it

```
pwcheck
```

Type a password and press Enter. Nothing appears as you type. That's normal, because the input is hidden on purpose.

Use a throwaway password for testing, not one you actually use.

## Step 6 (optional): Run the tests

```
pytest -v
```

You should see `11 passed`.

Step 7: Test passwords

Result will look something like this: 
Strength : [####----------------] Very weak
Entropy  : 10.0 bits (pool size 26, length 8)
Crack time (offline, fast hash): instantly
  ! This is a very common password.
  ! Shorter than 12 characters; length matters most.

## Troubleshooting

| Problem | Fix |
|---|---|
| `python` not recognized | Reinstall Python and tick "Add Python to PATH" |
| `source` not recognized (Windows) | Use `.venv\Scripts\activate` instead |
| `pwcheck` not recognized | Activate the virtual environment again (Step 3) |
| "Breach check: unavailable" | Your network or VPN is blocking the lookup. The strength score still works |
