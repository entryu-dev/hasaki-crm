FROM php:8.1-fpm

# Set working directory
WORKDIR /var/www/html

# Install dependencies for PHP
RUN apt-get update && apt-get install -y \
    git \
    curl \
    libpng-dev \
    libonig-dev \
    libxml2-dev \
    libzip-dev \
    zip \
    unzip \
    nano

# Install PHP extensions
RUN docker-php-ext-install pdo_mysql mbstring exif pcntl bcmath gd zip

# Install Composer
COPY --from=composer:latest /usr/bin/composer /usr/bin/composer

# Install Node.js and npm
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
    && apt-get install -y nodejs \
    && npm install -g npm@latest

# Install Angular CLI
RUN npm install -g @angular/cli@18

# Clean up
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# Set environment variables
ENV NODE_ENV=development
ENV PATH="/var/www/html/node_modules/.bin:${PATH}"

# Copy SuiteCRM installation command as a comment for reference
# ./bin/console suitecrm:app:install -u "admin" -p "pass" -U "root" -P "dbpass" -H "mariadb" -N "suitecrm" -S "https://yourcrm.com/" -d "yes"

# Copy application
COPY . /var/www/html

# Use a script as the entrypoint
COPY ./scripts/start.sh /usr/local/bin/start.sh
RUN chmod +x /usr/local/bin/start.sh

CMD ["/usr/local/bin/start.sh"]
