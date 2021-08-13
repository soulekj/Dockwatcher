#!/bin/bash

sudo pip3 install pandas
sudo pip3 install sense-hat
sudo pip3 install feedparser
sudo pip3 install ISStreamer

croncmd = "python3 /home/pi/Dockwatcher/Dockwatcher.py"
cronjob = "*/1 * * * * $croncmd"
cat <(fgrep -i -v "$croncmd" <(crontab -l)) <(echo "$cronjob") | crontab -
