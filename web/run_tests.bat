@echo off
cd /d %~dp0
path %path% ; ../python
..\python\python.exe manage.py test
pause
