import os
import json
import requests
import subprocess
import time

# Global Variables
SETTINGS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), '../data', 'settings.json')

def load_settings():
  if os.path.exists(SETTINGS_FILE):
    with open(SETTINGS_FILE, 'r') as f:
      settings = json.load(f)
    return settings
  else:
    return None

def save_settings(settings):
  with open(SETTINGS_FILE, 'w') as f:
    json.dump(settings, f, indent=2)

def check_for_updates(repo_owner, repo_name, last_commit):
  api_url = f'https://api.github.com/repos/{repo_owner}/{repo_name}/commits/master'
  
  response = requests.get(api_url)
  
  if response.status_code == 200:
    if last_commit != response.json()['sha']:
      return response.json()['sha']
    return None
  else:
    print(f"Failed to fetch updates. Status code:\r\n{response}")
    return None

def git_pull():
  subprocess.run(['git', 'fetch', '--all'])
  subprocess.run(['git', 'reset', 'hard', 'origin/main'])
  subprocess.run(['git', 'pull'])

def restart_service():
  subprocess.run(['sudo', 'systemctl', 'restart', 'your-service-name'])

if __name__ == "__main__":
  while True:
    settings = load_settings()
    repo_owner = settings.get('github_username', '')
    repo_name = settings.get('repo_name', '')
    last_commit = settings.get('last_commit', '')
    
    latest_commit_sha = check_for_updates(repo_owner, repo_name, last_commit)
    
    if latest_commit_sha:
      git_pull()

      settings['last_commit'] = latest_commit_sha
      save_settings(settings)
    
      #restart_service(settings['service'])

    time.sleep(60)