#!/usr/bin/expect -f
. /srv/extractor_v3/venv/bin/activate
python /srv/extractor_v3/app/controller.py
python /srv/extractor_v3/app/auto_domains_update.py
