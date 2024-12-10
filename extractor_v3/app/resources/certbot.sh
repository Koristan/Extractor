#!/usr/bin/expect -f
certbot certonly --noninteractive --agree-tos --webroot -w /var/www -d $1 -d www.$1