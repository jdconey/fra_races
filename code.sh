#!/bin/sh

eval `keychain --noask --eval id_ed25519`
TOD=$(date +%Y-%m-%d)

cd /home/pi/fra_races
git pull

python3 /home/pi/fra_races/fra_races.py

git add *
git commit -m pi_$TOD
git push

