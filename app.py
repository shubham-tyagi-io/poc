import requests
import sys
from retrying import retry
import pandas as pd
from datetime import datetime, timedelta

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
    # Using GitHub API
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
            # Get repo name and updated_at for archived repos
            archived_repos.extend([(repo["name"], repo["updated_at"]) for repo in repos if repo["archived"]])
            page += 1
        else:
            print(f"Failed to fetch repositories. Status code: {response.status_code}")
            sys.exit(1)
    
    return archived_repos

def fetch_filtered_repos(token, organization_name, days_threshold):
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github.v3+json"
    }
    # Using GitHub API
    url = f"https://api.github.com/orgs/{organization_name}/repos?type=all"
    
    filtered_repos = []
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
            # Get repo name, pushed_at, and calculate time since last update for all repos
            current_time = datetime.now()
            filtered_repos.extend([
                (repo["name"], repo["pushed_at"], current_time - datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ"))
                for repo in repos if (current_time - datetime.strptime(repo["pushed_at"], "%Y-%m-%dT%H:%M:%SZ")).days > days_threshold
            ])
            page += 1
        else:
            print(f"Failed to fetch repositories. Status code: {response.status_code}")
            sys.exit(1)
    
    return filtered_repos

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python app.py <GitHub Token> <Organization Name> <Days Threshold>")
        sys.exit(1)
    
    github_token = sys.argv[1]
    organization_name = sys.argv[2]
    days_threshold = int(sys.argv[3])  # Convert the input to an integer
    
    archived_repos = fetch_archived_repos(github_token, organization_name)
    filtered_repos = fetch_filtered_repos(github_token, organization_name, days_threshold)

    # Create a DataFrame for archived repos
    df_archive = pd.DataFrame(archived_repos, columns=["Archived Repo", "Archive Date"])

    # Create a DataFrame for filtered repos
    df_filtered = pd.DataFrame(filtered_repos, columns=["Repo Name", "Last Updated", "Time Since Last Update"])
    
    # Save the DataFrames to an Excel file
    excel_filename = f"{organization_name}_repos.xlsx"
    with pd.ExcelWriter(excel_filename) as writer:
        df_archive.to_excel(writer, sheet_name="Archive Repos", index=False)
        df_filtered.to_excel(writer, sheet_name="Filtered Repos", index=False)

        # Access the Excel workbook and worksheets
        workbook = writer.book
        archive_worksheet = writer.sheets["Archive Repos"]
        filtered_worksheet = writer.sheets["Filtered Repos"]
        
        # Adjust column widths
        for sheet in [archive_worksheet, filtered_worksheet]:
            for column in sheet.columns:
                max_length = 0
                column = list(column)
                for cell in column:
                    try:
                        if len(str(cell.value)) > max_length:
                            max_length = len(cell.value)
                    except:
                        pass
                adjusted_width = (max_length + 2) * 1.2
                sheet.column_dimensions[column[0].column_letter].width = adjusted_width
    
    print(f"Data exported to {excel_filename}")
