import requests
import pandas as pd
import sys
from retrying import retry

# GitHub API endpoint for updating repository settings
GITHUB_API_URL = "https://api.github.com/repos/{}/{}"

# Retry decorator to handle connection issues
@retry(stop_max_attempt_number=3, wait_fixed=2000)  # Retry 3 times with a 2-second delay between retries
def archive_repo(token, organization, repo_name):
    url = GITHUB_API_URL.format(organization, repo_name)
    headers = {
        "Authorization": f"token {token}",
        "Accept": "application/vnd.github.v3+json"
    }

    # Data to update the repository (set archived to true)
    data = {
        "archived": True
    }

    response = requests.patch(url, headers=headers, json=data)

    if response.status_code == 200:
        print(f"Successfully archived {repo_name}")
    else:
        print(f"Failed to archive {repo_name}. Status code: {response.status_code}")

def main():
    if len(sys.argv) != 4:
        print("Usage: python archive.py <GitHub Token> <Organization Name> <Excel File Path>")
        sys.exit(1)

    github_token = sys.argv[1]
    organization = sys.argv[2]
    excel_file_path = sys.argv[3]

    try:
        # Read the Excel file using pandas
        df = pd.read_excel(excel_file_path, sheet_name="Filtered Repos")

        # Extract the 'Repo Name' column as a list
        repo_names = df['Repo Name'].tolist()

        for repo_name in repo_names:
            archive_repo(github_token, organization, repo_name)

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
