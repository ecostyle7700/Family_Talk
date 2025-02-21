@echo off
cd /d %~dp0
call venv\Scripts\activate
set FLASK_APP=app.py
set FLASK_ENV=development
pip install -r requirements.txt
flask run
pause


python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
#pip install flask flask-sqlalchemy flask-login flask-wtf
$env:Path += ";C:\sqlite3"
python app.py
