FROM php:8.1.8-apache

RUN a2enmod rewrite

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    zip \
    unzip
# Clear cache
RUN apt-get clean && rm -rf /var/lib/apt/lists/*
# Install PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd
# Get latest Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Set working directory

COPY ./www/composer.json /var/www

WORKDIR /var/www
RUN composer install --prefer-source --no-interaction
RUN composer dump-autoload -o
