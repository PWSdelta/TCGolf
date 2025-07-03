# Database Connection Troubleshooting Guide

We're seeing a strange situation where:
1. Django reports "No migrations to apply" when running `python manage.py migrate`
2. But accessing the site still gives: "OperationalError: no such table: destinations_destination"

You have both `db.sqlite3` and `db_production.sqlite3` files on the server. This suggests Django might be configured to use one file but is actually using the other when serving requests.

## 1. Verify Database Path in Settings

First, check what database file Django is configured to use:

```bash
ssh root@159.223.94.36
cd /root/TCGolf

# Use Django shell to check the database path
python manage.py shell -c "from django.conf import settings; print(settings.DATABASES['default']['NAME'])"

# Look at the database configuration
grep -n "DATABASES" golfplex/settings.py -A 10

# Check both database files and their sizes
ls -lh db*.sqlite3
```

This will output the path to the database file Django is trying to use.

## 2. Check if the Database File Exists

Once you know the path, check if the file exists:

```bash
ls -la /path/to/your/db.sqlite3  # Replace with the actual path
```

If the file doesn't exist, this is the problem.

## 3. Check Database File Permissions

Check the permissions for both database files:

```bash
ls -la db*.sqlite3
```

The database files should be readable and writable by the user running Gunicorn (often www-data or the user you set in the systemd service).

Fix permissions if needed:
```bash
sudo chown www-data:www-data db.sqlite3 db_production.sqlite3
sudo chmod 664 db.sqlite3 db_production.sqlite3
```

## 4. Solution 1: Set Django to Use db_production.sqlite3

If your production data is in `db_production.sqlite3`:

1. Edit your Django settings:
   ```bash
   nano golfplex/settings.py
   ```

2. Find the DATABASES section and modify it to use db_production.sqlite3:
   ```python
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.sqlite3',
           'NAME': BASE_DIR / 'db_production.sqlite3',
       }
   }
   ```

3. Save the file (Ctrl+O, Enter, Ctrl+X) and restart Gunicorn:
   ```bash
   sudo systemctl restart gunicorn
   ```

## 5. Solution 2: Use a Symbolic Link

Alternative approach using a symbolic link (if you don't want to modify settings):

```bash
# First, backup any existing database
if [ -f /path/to/your/db.sqlite3 ]; then
    cp /path/to/your/db.sqlite3 /path/to/your/db.sqlite3.bak
fi

# Create a new empty database
touch /path/to/your/db.sqlite3
chown www-data:www-data /path/to/your/db.sqlite3
chmod 664 /path/to/your/db.sqlite3

# Run migrations on the new database
python manage.py migrate

# Restart Gunicorn
sudo systemctl restart gunicorn
```

## 6. Check Django Debug Output

Temporarily enable detailed debug output:

1. Edit your settings.py:
   ```bash
   nano golfplex/settings.py
   ```

2. Make sure DEBUG is set to True:
   ```python
   DEBUG = True
   ```

3. Save and restart Gunicorn:
   ```bash
   sudo systemctl restart gunicorn
   ```

4. Visit the site to see detailed error information

## 7. Check the Django Settings for Multiple Database Configurations

Sometimes projects have different database settings for different environments:

```bash
grep -r "DATABASES" --include="*.py" /root/TCGolf
```

Look for any production-specific settings files like `settings_production.py` that might be overriding the main settings.

## 8. Force Recreate Tables for a Specific App

If migrations exist but tables aren't being created, you can try to force it:

```bash
# First try running migrations for just the destinations app
python manage.py migrate destinations

# If that doesn't work, try this method to recreate migrations
python manage.py makemigrations destinations --empty --name recreate_tables
```

Then edit the newly created migration file to include CreateModel operations for your models. This is advanced and should be done carefully.

## 9. Transfer Your Local Database

If all else fails, transferring your local database might be the fastest solution:

```bash
# On your local machine
scp db.sqlite3 root@159.223.94.36:/root/TCGolf/

# On the server
ssh root@159.223.94.36
cd /root/TCGolf
chown www-data:www-data db.sqlite3
chmod 664 db.sqlite3
sudo systemctl restart gunicorn
```

## After Fixing

Once you've identified and fixed the issue, don't forget to set DEBUG back to False for production:

```bash
nano golfplex/settings.py
# Set DEBUG = False
sudo systemctl restart gunicorn
```
