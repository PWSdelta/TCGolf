# Deploy ALLOWED_HOSTS Fix

To fix the DisallowedHost error for `tcgplex.com`, follow these steps:

1. The `ALLOWED_HOSTS` setting in your `settings.py` file has been updated locally to include:
   ```python
   ALLOWED_HOSTS = ['tcgplex.com', 'www.tcgplex.com', '159.223.94.36', 'localhost', '127.0.0.1']
   ```

2. Commit and push this change to your repository:
   ```bash
   git add golfplex/settings.py
   git commit -m "Add tcgplex.com to ALLOWED_HOSTS"
   git push
   ```

3. SSH into your server and update the code:
   ```bash
   ssh root@159.223.94.36
   cd /root/TCGolf  # Adjust if your path is different
   git pull
   ```

4. Restart the Gunicorn service:
   ```bash
   sudo systemctl restart gunicorn
   ```

5. Verify the site is now working by visiting http://tcgplex.com/

## Alternative Quick Fix

If you don't want to wait for a git push/pull cycle, you can directly edit the settings file on the server:

```bash
ssh root@159.223.94.36
cd /root/TCGolf  # Adjust if your path is different
nano golfplex/settings.py
```

Find the `ALLOWED_HOSTS` line and update it to:
```python
ALLOWED_HOSTS = ['tcgplex.com', 'www.tcgplex.com', '159.223.94.36', 'localhost', '127.0.0.1']
```

Save the file (Ctrl+O, then Enter, then Ctrl+X), then restart Gunicorn:
```bash
sudo systemctl restart gunicorn
```

## Verification

After making these changes, verify that the DisallowedHost error is resolved by visiting your website at http://tcgplex.com/
