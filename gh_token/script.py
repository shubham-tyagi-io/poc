import jwt
import requests
import time
import argparse
from pathlib import Path

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
    parser = argparse.ArgumentParser(description='Generate a GitHub token using a JWT.')
    parser.add_argument('private_key_path', type=str, help='Path to the private key file')
    parser.add_argument('app_id', type=str, help='GitHub App ID')
    parser.add_argument('installation_id', type=str, help='GitHub App Installation ID')

    args = parser.parse_args()

    try:
        # Step 1: Create a JWT token
        jwt_token = create_jwt(args.app_id, args.private_key_path)
        # print("JWT Token created successfully")

        # Step 2: Use the JWT token to get a GitHub access token
        github_token = get_github_token(jwt_token, args.installation_id)
        print(github_token)

    except Exception as e:
        print(f"An error occurred: {e}")
