#!/usr/bin/env bash
# exit on error
set -o errexit

# 1. Sabse pehle sari Python libraries install hongi (Flask, Playwright etc.)
pip install -r requirements.txt

# 2. Playwright ka browser (Chromium) download hoga
playwright install chromium

# 3. Browser ko chalane ke liye jo Linux ki extra files chahiye wo install hongi
playwright install-deps chromium
