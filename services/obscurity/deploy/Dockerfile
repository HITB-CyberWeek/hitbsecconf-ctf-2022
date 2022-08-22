FROM php:8.1.8-apache

RUN apt-get update && apt-get install -y libpq-dev libgmp-dev libcap2-bin && docker-php-ext-configure pgsql && docker-php-ext-install pgsql gmp
RUN setcap cap_net_bind_service=+ep /usr/sbin/apache2

COPY ixed.8.1.lin /usr/local/lib/php/extensions/no-debug-non-zts-20210902/
RUN echo "extension=ixed.8.1.lin" > /usr/local/etc/php/conf.d/10-sourceguardian.ini

RUN useradd obscurity -u 1000

RUN sed -i 's!/var/www/!/home/obscurity!' /etc/apache2/apache2.conf
RUN sed -i 's!DocumentRoot /var/www/html!DocumentRoot /home/obscurity!' /etc/apache2/sites-available/000-default.conf

USER obscurity

WORKDIR /home/obscurity/
