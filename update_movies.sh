#!/bin/bash
cd ~/scalper/digital_dreamers
source .venv/bin/activate
python start.py

git add -A
git commit -m "update_movies : $(date)"
git push origin main
git pull