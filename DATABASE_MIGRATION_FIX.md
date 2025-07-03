# Database Migration Fix

After adding `tcgplex.com` to `ALLOWED_HOSTS`, we're now encountering a database error:

```
OperationalError: no such table: destinations_destination
```

This indicates that the database tables haven't been created on the server. We need to run Django migrations to create the database schema.

## Solution

### Option 1: Run migrations on the server

1. SSH into your server:
   ```bash
   ssh root@159.223.94.36
   ```

2. Navigate to your project directory:
   ```bash
   cd /root/TCGolf  # Adjust if your path is different
   ```

3. Activate the virtual environment:
   ```bash
   source venv/bin/activate  # or whatever your venv path is
   ```

4. Run Django migrations:
   ```bash
   python manage.py migrate
   ```

5. Restart Gunicorn:
   ```bash
   sudo systemctl restart gunicorn
   ```

### Option 2: Transfer your local database to the server

If you already have a populated database locally that you want to use on the server:

1. First, make sure you have a backup of your local database:
   ```bash
   cp db.sqlite3 db_backup_before_transfer.sqlite3
   ```

2. Use SCP to transfer your local database to the server:
   ```bash
   scp db.sqlite3 root@159.223.94.36:/root/TCGolf/
   ```

3. SSH into your server:
   ```bash
   ssh root@159.223.94.36
   ```

4. Apply the correct permissions:
   ```bash
   cd /root/TCGolf
   chown www-data:www-data db.sqlite3
   chmod 664 db.sqlite3
   ```

5. Restart Gunicorn:
   ```bash
   sudo systemctl restart gunicorn
   ```

## Database Setup with Empty Database

If you want to start with a fresh database and add initial data:

1. Run migrations as described in Option 1 above.

2. Create a superuser for the admin panel:
   ```bash
   python manage.py createsuperuser
   ```

3. If you have any fixtures (pre-defined data), load them:
   ```bash
   python manage.py loaddata fixtures/initial_data.json  # Adjust the path as needed
   ```

## Verification

After applying any of these solutions, visit your website at http://tcgplex.com/ to verify that the database error is resolved.

You should also check that your data is properly showing by:
1. Visiting the homepage to see if destinations are listed
2. Accessing the admin panel at http://tcgplex.com/admin/ and checking if you can log in and see your data
