@echo off
SETLOCAL

set REGISTRY=docker.io/avasil08
set NAME=ps-chatbot
for /f "delims=" %%a in ('git rev-parse --short HEAD') do set SHORT_SHA=%%a
set IMG=%REGISTRY%/%NAME%:acc.1.0.3
set LATEST=%REGISTRY%/%NAME%:%TAG%

docker build -t %IMG% .

docker push %IMG%

ENDLOCAL
@echo on