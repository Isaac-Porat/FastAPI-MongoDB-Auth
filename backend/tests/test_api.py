import requests

def register_test_api():
    try:
        register_attempt = requests.post("http://localhost:8000/register", data={"username": "testuser5", "password": "testpassword"})
        register_attempt.raise_for_status()
        print(register_attempt.json())
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

def login_test_api():
    try:
        login_attempt = requests.post("http://localhost:8000/login", data={"username": "testuser2", "password": "testpassword"})
        login_attempt.raise_for_status()
        print(login_attempt.json())
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred: {err}")
    except Exception as err:
        print(f"An error occurred: {err}")

if __name__ == "__main__":
    register_test_api()
    # login_test_api()