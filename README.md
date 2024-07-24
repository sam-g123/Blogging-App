# Flask Blog Application

## Overview
This is a Flask application for a blog website that allows users to create accounts, write posts, and interact with other users. The application includes features for user authentication, profile management, and post interactions.

## Features
- **User Accounts**: Users can create accounts with email and password authentication. Email addresses must be confirmed for account activation.
- **Email Confirmation**: Confirmation emails are sent using OAuth2 mechanism to ensure secure and reliable delivery.
- **User Profiles**: Users can update their profiles with real names, usernames, profile pictures, and location information.
- **Posts and Comments**: Users can create, edit, and delete blog posts. They can also comment on posts and follow other users.
- **User Roles**: The application supports regular users and admin users with different access permissions.

## Setting up the Virtual Environment
1. Create the virtual environment:
    ```bash
    python -m venv [venv]
    ```
2. Activate the virtual environment:
    ```bash
    [venv]\Scripts\activate
    ```
   - Replace `[venv]` with your desired path.

## Setting up the Database
1. Initialize the database:
    ```bash
    flask db init
    ```
2. Apply migrations:
    ```bash
    flask db migrate -m "Initial migration."
    flask db upgrade
    ```

## Running the Application
To run the application in different environments (development, production, or testing), set the corresponding environment variables. These variables are defined in the `config.py` file under the `Config` class.

### Development
To run the application in development mode, set the `FLASK_APP` environment variable to `development`:
```bash
(venv) export FLASK_APP="app:create_app('development')"
(venv) flask run
