FROM php:8.1.8-apache

RUN apt-get update && apt-get install -y libpq-dev libgmp-dev && docker-php-ext-configure pgsql && docker-php-ext-install pgsql gmp

RUN useradd obscurity -u 1000

RUN sed -i s'/<VirtualHost \*:80>/<VirtualHost *:3255>/' /etc/apache2/sites-available/000-default.conf
RUN sed -i 's/Listen 80/Listen 127.0.0.1:3255/' /etc/apache2/ports.conf

RUN sed -i 's!/var/www/!/home/obscurity!' /etc/apache2/apache2.conf
RUN sed -i 's!DocumentRoot /var/www/html!DocumentRoot /home/obscurity!' /etc/apache2/sites-available/000-default.conf

USER obscurity

WORKDIR /home/obscurity/
