#! /usr/bin/bash

cd /var/www/twitter-to-telegram

. venv/bin/activate

ts=`date +%s`
python3 main.py > "log/log-$ts.out" 2>&1 &