# List Management App

A Django-based application for organizing personal to-do and shopping lists. Each user can register, log in, and manage
their own lists with complete privacy.

## Features

* User Registration and Login: Secure user accounts for list creation and management.
* Create Lists: Users can set up personalized to-do or shopping lists.
* Add/Remove Items: Effortlessly add or remove items in each list.
* Item Completion: Mark items as complete to track progress.

### Prerequisites

1. Python: Version 3.10 or above
2. Virtual Environment: Recommended for dependency management

### Notes

* Database: This project uses SQLite, included by default with Django.

## Setup

1. Clone the repository

2. Create and activate a virtual environment:
    ```
    python -m venv {env_name}
    source {env_name}/bin/activate
    ```

3. Create `.env` file in root directly and add values for keys from `.env.sample` 

4. Install dependencies:
   `pip install -r requirements.txt`

5. Run migrations and start the server:
    ```
    python manage.py migrate
    python manage.py runserver
    ```
   Access the app at http://127.0.0.1:8000/.

### Import Data format

Refer to import format provided in CSV file `import-format.csv`
