@echo off
REM GolfPlex Content Worker Launcher
REM This batch file launches the content worker with the server's API URL

REM Set the server IP here
set SERVER_IP=159.223.94.36

REM Model to use
set MODEL=llama3.1

echo ===================================
echo GolfPlex Content Worker
echo ===================================
echo Server: http://%SERVER_IP%
echo Model: %MODEL%
echo ===================================
echo.

REM Run the content worker
python content_worker.py --api-url http://%SERVER_IP% --model %MODEL%

echo.
echo Worker process ended. Press any key to exit.
pause > nul
