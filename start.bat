TITLE "RagStack"

@echo off
echo Starting Backend and Frontend...

start cmd /k "A:\curent projects\ragstack\backend-common\tools\start_backend.bat"
timeout /t 1 
start cmd /k "A:\curent projects\ragstack\backend-common\tools\start_frontend.bat"

echo All services started!
exit