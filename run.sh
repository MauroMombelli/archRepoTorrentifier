#!/bin/sh

cd /home/archie/archRepoTorrentifier/
pipenv install
pipenv run python download.py
