import os
import sys
import json
import requests

def get_github_token():
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    return github_token

def parse_github_event():
    event_path = os.environ.get('GITHUB_EVENT_PATH')
    if not event_path:
        print("Error: GITHUB_EVENT_PATH environment variable not set")
        sys.exit(1)
    try:
        with open(event_path, 'r') as event_file:
            event_data = json.load(event_file)
        return event_data
    except Exception as e:
        print(f"Error reading GitHub event file: {e}")
        sys.exit(1)

def get_commit_files(repo, commit_sha, github_token):
    """
    Retrieve files changed in a specific commit using GitHub API.
    
    Args:
        repo (str): Repository in format 'owner/repo'
        commit_sha (str): Commit SHA
        github_token (str): GitHub authentication token
    
    Returns:
        list: Files changed in the commit
    """
    url = f"https://api.github.com/repos/{repo}/commits/{commit_sha}"
    headers = {
        'Authorization': f'token {github_token}',
        'Accept': 'application/vnd.github.v3+json'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        commit_details = response.json()
        
        # Extract file changes
        files = commit_details.get('files', [])
        return [file['filename'] for file in files]

    except requests.RequestException as e:
        print(f"Error fetching commit details: {e}")
        return []

def map_commits_to_files(event_data, github_token):
    """
    Create a detailed mapping of commits to their specific changed files.
    
    Returns:
    - A list of dictionaries with commit details and changed files
    """
    # Extract repository information
    repo = os.environ.get('GITHUB_REPOSITORY')
    if not repo:
        print("Error: GITHUB_REPOSITORY environment variable not set")
        sys.exit(1)
    
    commits_mapping = []
    
    # Handle push event commits
    for commit in event_data.get('commits', []):
        commit_info = {
            'id': commit.get('id', 'Unknown'),
            'message': commit.get('message', 'No message'),
            'files': get_commit_files(repo, commit.get('id', ''), github_token)
        }
        commits_mapping.append(commit_info)
    
    return commits_mapping

def main():
    # Get GitHub token and event data
    github_token = get_github_token()
    event_data = parse_github_event()
    
    # Map commits to their specific files
    commits_file_mapping = map_commits_to_files(event_data, github_token)
    
    # Print detailed mapping
    print("Detailed Commit-to-File Mapping:")
    for commit in commits_file_mapping:
        print("\n--- Commit Details ---")
        print(f"Commit ID: {commit['id']}")
        print(f"Message: {commit['message']}")
        
        print("\nChanged Files:")
        print(commit['files'])
    
    # Save mapping to a JSON file for further processingasdsda
    

if __name__ == "__main__":
    main()