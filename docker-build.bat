@echo off
SETLOCAL

set REGISTRY=docker.io/avasil08
set NAME=chatbot-server
for /f "delims=" %%i in ('git rev-parse --short HEAD') do set TAG=%%i
set IMG=%REGISTRY%/%NAME%:acc.%TAG%
set LATEST=%REGISTRY%/%NAME%:%TAG%

docker build -t %IMG% .

docker push %IMG%

ENDLOCAL
@echo on