import requests

# Your credentials and other configuration
user_id = "jvqrpit5yo8j"
pat = "da6c272af9f345cb8945fcc48d3a9da5"
app_id = "my-first-application-vr48qs"

# Clarifi API base URL (replace this with the actual URL if available)
base_url = "https://api.clarifi.com"  # Example URL, replace with actual API endpoint

# Authentication URL (check Clarifi's documentation for exact endpoint)
auth_url = f"{base_url}/auth/login"

# Headers for the request (add content type or any other headers Clarifi requires)
headers = {
    "Content-Type": "application/json",
}

# Body of the request (send required fields in JSON format)
payload = {
    "user_id": user_id,
    "pat": pat,
    "app_id": app_id
}

# Send POST request to authenticate
try:
    response = requests.post(auth_url, json=payload, headers=headers)

    # Check if the authentication was successful
    if response.status_code == 200:
        print("Login successful!")
        # If response includes token or other info, you can store it for future requests
        auth_token = response.json().get("auth_token")
        print(f"Authentication Token: {auth_token}")
    else:
        print(f"Login failed: {response.status_code} - {response.text}")
except Exception as e:
    print(f"Error occurred: {str(e)}")
