# python-lms
Python Learning Management System

## TO setup the project locally
python -m venv myvenv

myvenv\Scripts\activate

pip install -r requirements.txt

python manage.py makemigrations

python manage.py migrate

python manage.py runserver