@echo off
setlocal enabledelayedexpansion

:: Define the absolute path for mosquitto executable
set MOSQUITTO_PATH=D:\MQTT\mosquitto\mosquitto.exe
set CONFIG_PATH=D:\MQTT\mosquitto\mosquitto.conf

:: Check if port 9001 is occupied
for /f "tokens=5 delims= " %%a in ('netstat -ano ^| findstr 9001') do (
    set pid=%%a
    echo Port 9001 is occupied by PID=!pid!.
    
    :: Kill the process occupying port 9001
    taskkill /F /PID !pid!
    if %errorlevel% equ 0 (
        echo Process PID=!pid! has been successfully terminated.
    ) else (
        echo Failed to terminate process PID=!pid!.
    )
)

:: Start mosquitto service
echo Starting mosquitto service...
if exist "%MOSQUITTO_PATH%" (
    "%MOSQUITTO_PATH%" -c "%CONFIG_PATH%" -v
) else (
    echo Error: mosquitto executable not found at specified path.
)

pause