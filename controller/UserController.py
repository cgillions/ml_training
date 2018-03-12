from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError
from utils.response_utils import error, success
from utils.db_utils import get_database
from model.user import User
from flask import request
from uuid import uuid4
from time import time

ADMIN_SECRET = "5dyvo1z6y34so4ogkgksw88ookoows00cgoc488kcs8wk4c40s"


def register():
    # Get the username from the request.
    username = request.form.get("username")

    # Validate the username.
    valid = validate_username(username)
    if valid is not True:
        return valid

    # Get the password from the request.
    password = request.form.get("password")

    # validate the password.
    valid = validate_password(password)
    if valid is not True:
        return valid

    # Get the role of the new user.
    role = request.form.get("role")

    # Validate the role.
    valid = validate_role(role)
    if valid is not True:
        return valid

    # User credentials are valid. Create the user.
    user = create_user(username, password, role)

    # Return the user object.
    return success({"user": user.__dict__})


# Returns a logged in user, or an error.
def login(auth_token, username=None, password=None):

    # Check if the user is authenticated through a token.
    if not is_authenticated(auth_token):

        # Ensure there is a valid username.
        if username is None:
            return error("Username not provided.", "A username must be included in the header.")

        if not isinstance(username, str):
            return error("Username is not valid.", "A username must be constituted of text and numbers.")

        # Check the password validity.
        valid = validate_password(password)
        if valid is not True:
            return valid

        # There's a valid password.
        database_conn = get_database()
        cursor = database_conn.cursor()

        # Get the id and password of the user.
        cursor.execute("""
                        SELECT id, password, role
                        FROM public."User"
                        WHERE username=(%s);
                        """, (username,))
        attrs = cursor.fetchone()

        # Check if there is a user with that username.
        if attrs is None:
            cursor.close()
            database_conn.close()
            return error("User doesn't exist.", "No user exists with that username. You should register an account.")

        idx = attrs[0]
        hashed_pwd = attrs[1]
        role = attrs[2]

        # Verify the passwords match.
        try:
            PasswordHasher().verify(hashed_pwd, password)

        # Handle the passwords not matching.
        except VerifyMismatchError:
            cursor.close()
            database_conn.close()
            return error("Passwords don't match.", "The password supplied doesn't match the one stored.")

        # The passwords match. Create an auth token for the user.
        auth_token, expiry = get_auth_token()

        # Store the auth token.
        cursor.execute("""
                        UPDATE
                        public."User"
                        SET auth_token = %s, 
                            auth_expiry = %s
                        WHERE id = %s;
                        """, (auth_token, expiry, idx))

        # Commit the transaction.
        database_conn.commit()

        # Close the connections.
        cursor.close()
        database_conn.close()

        # Return the logged in user.
        return User(idx, username, auth_token, role)

    # The user is authenticated. Update the expiry date.
    ignore, expiry = get_auth_token()

    database_conn = get_database()
    cursor = database_conn.cursor()

    cursor.execute("""
                    UPDATE
                    public."User"
                    SET auth_expiry = %s
                    WHERE auth_token=(%s)
                    RETURNING id, username, role;
                    """, (expiry, auth_token))

    # Commit the transaction.
    database_conn.commit()

    attrs = cursor.fetchone()
    cursor.close()
    database_conn.close()

    return User(attrs[0], attrs[1], auth_token, attrs[2])


def is_authenticated(auth_token):
    if auth_token is None:
        return False

    database_conn = get_database()
    cursor = database_conn.cursor()

    cursor.execute("""
                    SELECT COUNT(*)
                    FROM public."User"
                    WHERE auth_token=%s
                    AND auth_expiry > %s;
                    """, (auth_token, time()))
    count = cursor.fetchone()[0]

    cursor.close()
    database_conn.close()
    return count > 0


def create_user(username, password, role):
    auth_token, auth_expiry = get_auth_token()

    database_conn = get_database()
    cursor = database_conn.cursor()

    cursor.execute("""
                    INSERT INTO
                    public."User"
                    (username, password, role, auth_token, auth_expiry)
                    VALUES (%s, %s, %s, %s, %s)
                    RETURNING id, username;
                    """, (username, PasswordHasher().hash(password), role, auth_token, auth_expiry))

    # Commit the transaction.
    database_conn.commit()

    # Close connections.
    attrs = cursor.fetchone()[0]
    cursor.close()
    database_conn.close()

    # Return the user object.
    return User(attrs[0], attrs[1], auth_token)


# Auth token valid for two hours.
def get_auth_token():
    return str(uuid4()), time() + 7200


def validate_username(username):
    if username is None:
        return error("Username required.", "No username was provided.")

    if not isinstance(username, str):
        return error("Username is not a string.", "Username must be text, not only numbers.")

    if len(username) < 8:
        return error("Username is not long enough.", "Username must be at least 8 characters.")

    database_conn = get_database()
    cursor = database_conn.cursor()

    cursor.execute("""
                    SELECT COUNT(*) 
                    FROM public."User"
                    WHERE username=(%s);
                    """, (username,))

    count = cursor.fetchone()[0]
    cursor.close()
    database_conn.close()

    if count is not 0:
        return error("Username already exists.", "A user with the username {} already exists.".format(username))

    return True


def validate_password(password):
    if password is None:
        return error("Password required.", "No password was provided in the request.")

    if not isinstance(password, str):
        return error("Password is not a string.", "Password must include text and numbers, e.g. not only numbers.")

    if len(password) < 8:
        return error("Password is not long enough.", "Password must be at least 8 characters.")

    return True


def validate_role(role):
    if role is None:
        return error("Role required.", "Cannot register a user with no role.")

    if role not in ["admin", "developer"]:
        return error("Unknown role.", "Cannot register a user for role {}.".format(role))

    if role == "admin":
        secret = request.form.get("secret")

        # Verify the admin secret is provided.
        valid = validate_admin_secret(secret)
        if valid is not True:
            return valid

    return True


def validate_admin_secret(secret):
    if secret is None:
        return error("Secret required.", "Registering an admin requires knowledge of the admin secret!")

    if secret != ADMIN_SECRET:
        return error("Incorrect secret.", "The secret required for registering an admin is wrong.")

    return True
