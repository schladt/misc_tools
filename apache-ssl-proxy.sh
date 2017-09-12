#!/bin/bash
#Sets up SSL with self-signed cert and configures apache as a proxy
#Tested on Ubuntu 16.04

#basic apache config

apt-get -y update
apt-get install -y build-essential apache2 libxml2-dev
apt-get install -y libapache2-mod-proxy-html
a2enmod ssl proxy proxy_ajp proxy_http rewrite deflate headers proxy_balancer proxy_connect proxy_html
service apache2 restart

#ssl config
mkdir /etc/apache2/ssl
openssl req -x509 -nodes -days 3650 -newkey rsa:2048 -keyout /etc/apache2/ssl/apache.key -out /etc/apache2/ssl/apache.crt -subj \
"/C=US/ST=Ohio/L=Cincinnati/O=Example Organization/OU=Security Dudes/CN=mysite.example.com"

#set up apache sites
cd /etc/apache2/sites-available/
a2dissite *
rm *
cd -

cat > /etc/apache2/sites-available/default.conf << EndOfMessage
<VirtualHost *:80>
    Redirect "/" "https://34.227.92.13/"
</VirtualHost>

<VirtualHost *:443>
    SSLEngine On
    SSLCertificateFile /etc/apache2/ssl/apache.crt
    SSLCertificateKeyFile /etc/apache2/ssl/apache.key
    ProxyPass / http://127.0.0.1:8000/
    ProxyPassReverse / http://127.0.0.1:8000/
</VirtualHost>

EndOfMessage

#write the ports file
cat > /etc/apache2/ports.conf << EndOfMessage 
Listen 80
Listen 443
Listen 9090

EndOfMessage

#enable the new site
cd /etc/apache2/sites-available/
a2ensite *
cd -

#restart apache
service apache2 restart

echo "Apache has been configured. Please check above messages for errors."
