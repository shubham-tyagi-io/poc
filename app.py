import requests
import sys
from retrying import retry
import pandas as pd
from datetime import datetime

# Retry decorator to handle connection issues
@retry(stop_max_attempt_number=3, wait_fixed=2000)  # Retry 3 times with a 2-second delay between retries
def fetch_url(url, headers, params=None):
    response = requests.get(url, headers=headers, params=params)
    response.raise_for_status()
    return response

def fetch_archived_repos(token, organization_name):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Using Github Api
    url = f"https://api.github.com/orgs/{organization_name}/repos?type=all"
    
    archived_repos = []
    page = 1
    while True:
        try:
            response = fetch_url(url, headers=headers, params={"page": page})
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch repositories. Error: {e}")
            sys.exit(1)
        
        if response.status_code == 200:
            repos = response.json()
            if not repos:
                break
            # Grep repo name and pushed at to get archive repos and its dates and time
            archived_repos.extend([(repo["name"], repo["updated_at"]) for repo in repos if repo["archived"]])
            page += 1
        else:
            print(f"Failed to fetch repositories. Status code: {response.status_code}")
            sys.exit(1)
    
    return archived_repos

def fetch_all_repos(token, organization_name):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Using Github Api
    url = f"https://api.github.com/orgs/{organization_name}/repos?type=all"
    
    all_repos = []
    page = 1
    while True:
        try:
            response = fetch_url(url, headers=headers, params={"page": page})
        except requests.exceptions.RequestException as e:
            print(f"Failed to fetch repositories. Error: {e}")
            sys.exit(1)
        
        if response.status_code == 200:
            repos = response.json()
            if not repos:
                break
            # Grep repo name and pushed at to get archive repos and its dates and time
            all_repos.extend([(repo["name"], repo["pushed_at"], datetime.now() - datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ")) for repo in repos ])
                                                   
            page += 1
        else:
            print(f"Failed to fetch repositories. Status code: {response.status_code}")
            sys.exit(1)
    
    return all_repos

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python app.py <GitHub Token> <Organization Name>")
        sys.exit(1)
    
    github_token = sys.argv[1]
    organization_name = sys.argv[2]
    
    archived_repos = fetch_archived_repos(github_token, organization_name)
    all_repos = fetch_all_repos(github_token, organization_name)

    # Create a DataFrame
    df_archive = pd.DataFrame(archived_repos, columns=["Archived Repo", "Archive Date"])
    df_all = pd.DataFrame(all_repos, columns=["Repo Name", "Last Updated", "Time Since Last Update"])
    
    # Save the DataFrame to an Excel file
    excel_filename = f"{organization_name}_archived_repos.xlsx"
    with pd.ExcelWriter(excel_filename) as writer:
      df_archive.to_excel(writer, sheet_name="Archive Repos", index=False)
      df_all.to_excel(writer, sheet_name="All Repos", index=False)
    print(f"Data exported to {excel_filename}")
