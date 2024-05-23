import sys
import requests

def fetch_repos(token, username):
    url = f"https://api.github.com/users/{username}/repos"
    headers = {
        "Authorization": f"token {token}"
    }
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        repos = response.json()
        for repo in repos:
            print(f"Repository Name: {repo['name']}")
            print(f"Repository URL: {repo['html_url']}")
            print("-" * 40)
    else:
        print(f"Failed to fetch repositories. Status code: {response.status_code}")
        print(response.json())

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python test.py <personal_access_token> <username>")
        sys.exit(1)
    
    personal_access_token = sys.argv[1]
    username = sys.argv[2]
    fetch_repos(personal_access_token, username)
