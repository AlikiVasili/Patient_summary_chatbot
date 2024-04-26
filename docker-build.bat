@echo off
SETLOCAL

set REGISTRY=docker.io/avasil08
set NAME=ps-chatbot
set IMG=%REGISTRY%/%NAME%:acc.1.0.0
set LATEST=%REGISTRY%/%NAME%:%TAG%

docker build -t %IMG% .

docker push %IMG%

ENDLOCAL
@echo on