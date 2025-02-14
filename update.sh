#!/bin/bash
cd /var/www/api.newedu.uz
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart api_newedu
