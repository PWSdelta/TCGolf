# Sitemap Generation Guide

This guide explains how to generate and download a sitemap for the GolfPlex website without needing to transfer the entire database.

## 1. On the server

SSH into your server and navigate to the GolfPlex directory:

```bash
cd /home/golfplex/golfplex  # Adjust if your path is different
```

Generate the sitemap using the new script:

```bash
python generate_and_download_sitemap.py --generate
```

This will create a `sitemap.xml` file in the current directory.

## 2. Serve and download the sitemap

### Option A: Serve the sitemap from the server

On the server, run:

```bash
python generate_and_download_sitemap.py --generate --serve
```

This will generate the sitemap and start a simple HTTP server that only serves the sitemap.xml file.

Then, on your local machine, download the sitemap:

```powershell
python generate_and_download_sitemap.py --download SERVER_IP:PORT
```

Replace `SERVER_IP:PORT` with your server's IP address and port (default is 8000).

### Option B: Using SCP (Secure Copy)

You can download the sitemap directly using SCP:

```powershell
# On Windows with OpenSSH client
scp username@SERVER_IP:/home/golfplex/golfplex/sitemap.xml ./sitemap.xml

# On Windows with PuTTY's PSCP
pscp username@SERVER_IP:/home/golfplex/golfplex/sitemap.xml ./sitemap.xml
```

## 3. Verify the sitemap

After downloading, check that the sitemap.xml file contains all your destinations:

```powershell
# Count the number of URLs in the sitemap
Select-String -Path sitemap.xml -Pattern "<loc>" | Measure-Object | Select-Object -ExpandProperty Count
```

## 4. Deploy the sitemap

Once you've verified the sitemap, you can commit it to your repository:

```powershell
git add sitemap.xml
git commit -m "Update sitemap.xml"
git push
```

Then deploy it to your server:

```bash
# On the server
cd /home/golfplex/golfplex
git pull
```

## Additional Tips

- Make sure your Django settings include the correct base URL for your website
- If you need to regenerate the sitemap regularly, consider setting up a cron job on the server
- Remember to submit your sitemap to search engines like Google Search Console
