@echo off
path %path%;%~dp0/../python
@echo
python manage.py runserver
pause
