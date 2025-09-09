# django-ecommerce
A very simple and noob-friendly E-Commerce shop created using django. This is a very simple web application, so 
please report any issues or inconsistencies that you encounter.

## Features
Even though this shop project is very simple, it has some interesting functionalities:
- The ability to add, remove, and update items in the admin panel
- User signup, sign in, and logout
- A session-based cart, with the ability to add and remove items
- The ability to finalize your purchase
- The ability to search and filter items

## Installation
Clone the repository by typing the following command:
```
git clone https://github.com/S4mpl3r/django-ecommerce.git
```
Then create a python virtual environment for this project and activate it.
Then cd into the project directory and run the following command to install the requirements:
```
pip install -r requirements.txt
```
After this, you can apply the database migrations and start the server:
```
python manage.py migrate
python manage.py runserver
```
