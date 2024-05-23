import jwt
import requests
import time
from pathlib import Path
import sys  # Import sys module

# Configuration
PRIVATE_KEY_PATH = sys.argv[1]  # First argument is the path to the private key
APP_ID = sys.argv[2]  # Second argument is the GitHub App ID
INSTALLATION_ID = sys.argv[3]  # Third argument is the Installation ID

# Function to create a JWT token
def create_jwt(app_id, private_key_path):
    # Read the private key
    with open(private_key_path, 'r') as key_file:
        private_key = key_file.read()
    
    # Generate the JWT payload
    payload = {
        # issued at time, 60 seconds in the past to allow for clock drift
        'iat': int(time.time()) - 60,
        # JWT expiration time (10 minute maximum)
        'exp': int(time.time()) + (10 * 60),
        # GitHub App's identifier
        'iss': app_id
    }

    # Create JWT token
    jwt_token = jwt.encode(payload, private_key, algorithm='RS256')
    return jwt_token

# Function to get the GitHub access token using the JWT token
def get_github_token(jwt_token, installation_id):
    headers = {
        'Authorization': f'Bearer {jwt_token}',
        'Accept': 'application/vnd.github.v3+json'
    }

    url = f'https://api.github.com/app/installations/{installation_id}/access_tokens'

    response = requests.post(url, headers=headers)
    response.raise_for_status()  # Raise an exception for HTTP errors

    access_token = response.json()['token']
    return access_token

# Main script execution
if __name__ == '__main__':
    try:
        # Step 1: Create a JWT token
        jwt_token = create_jwt(APP_ID, PRIVATE_KEY_PATH)
        #print("JWT Token created successfully")

        # Step 2: Use the JWT token to get a GitHub access token
        github_token = get_github_token(jwt_token, INSTALLATION_ID)
        print(github_token)

    except Exception as e:
        print(f"An error occurred: {e}")
