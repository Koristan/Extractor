#!/usr/bin/expect -f
certbot delete --non-interactive --cert-name $1 || certbot delete --non-interactive --cert-name $1-001 || certbot delete --non-interactive --cert-name $1-0001