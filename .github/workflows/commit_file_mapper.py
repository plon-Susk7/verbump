import os
import sys
import json
import requests
import toml
import subprocess

def get_github_token():
    github_token = os.environ.get('GITHUB_TOKEN')
    if not github_token:
        print("Error: GITHUB_TOKEN environment variable not set")
        sys.exit(1)
    return github_token

def run_command(command):
    """
    Run a shell command and return its output.
    
    Args:
        command (list): Command to run as a list of strings
    
    Returns:
        tuple: (return_code, stdout, stderr)
    """
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=False)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        print(f"Error running command: {e}")
        return 1, "", str(e)

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

def change_toml_version(commit_message, changed_files):
    """
    Change version in pyproject.toml and prepare for commit.
    
    Returns:
        tuple: (path_to_updated_toml, new_version)
    """
    commit_type = commit_message.split(':')[0].strip()
    
    for changed_file in changed_files:
        # Construct potential pyproject.toml path
        path_parts = changed_file.split('/')
        final_path = '/'.join(path_parts[0:-1]) + '/pyproject.toml'
        
        # Check if pyproject.toml exists
        if os.path.exists(final_path):
            # Load existing toml
            with open(final_path, 'r') as file:
                data = toml.load(file)
            
            # Get current version
            current_version = data['project']['version']
            version_split = current_version.split('.')
            
            # Bump version based on commit type
            if commit_type == 'feat':
                version_split[0] = str(int(version_split[0]) + 1)
                version_split[1] = '0'
                version_split[2] = '0'
            elif commit_type == 'fix':
                version_split[1] = str(int(version_split[1]) + 1)
                version_split[2] = '0'
            elif commit_type == 'chore':
                version_split[2] = str(int(version_split[2]) + 1)
            
            # Update version
            new_version = '.'.join(version_split)
            data['project']['version'] = new_version
            
            # Write back to file
            with open(final_path, 'w') as file:
                toml.dump(data, file)
            
            return final_path, new_version
    
    return None, None

def configure_git():
    """
    Configure git user for committing changes.
    """
    # Get actor information from GitHub Actions
    actor = os.environ.get('GITHUB_ACTOR', 'GitHub Actions')
    email = f"{actor}@users.noreply.github.com"
    
    # Configure git user
    run_command(['git', 'config', '--global', 'user.name', actor])
    run_command(['git', 'config', '--global', 'user.email', email])

def commit_and_push_changes(toml_path, new_version):
    """
    Commit and push changes to the repository.
    """
    if not toml_path:
        print("No changes to commit")
        return
    
    # Stage the changed file
    returncode, stdout, stderr = run_command(['git', 'add', toml_path])
    if returncode != 0:
        print(f"Error staging file: {stderr}")
        return
    
    # Commit the changes
    commit_message = f"chore: bump version to {new_version}"
    returncode, stdout, stderr = run_command(['git', 'commit', '-m', commit_message])
    if returncode != 0:
        print(f"Error committing changes: {stderr}")
        return
    
    # Push the changes
    returncode, stdout, stderr = run_command(['git', 'push'])
    if returncode != 0:
        print(f"Error pushing changes: {stderr}")
        return
    
    print(f"Successfully bumped version to {new_version}")

def main():
    # Get GitHub token and event data
    github_token = get_github_token()
    event_data = parse_github_event()
    
    # Map commits to their specific files
    commits_file_mapping = map_commits_to_files(event_data, github_token)
    
    # Configure git for committing
    configure_git()
    
    # Process each commit
    for commit in commits_file_mapping:
        commit_message = commit['message']
        changed_files = commit['files']
        
        # Change version in pyproject.toml
        toml_path, new_version = change_toml_version(commit_message, changed_files)
        
        # Commit and push changes
        if toml_path and new_version:
            commit_and_push_changes(toml_path, new_version)

if __name__ == "__main__":
    main()