

import requests
from version import __version__

# The GitHub repository for the tool
GITHUB_REPO = "your_github_username/your_repo_name" # <-- IMPORTANT: Change this!

def check_for_updates():
    """Checks for a new version of the tool on GitHub."""
    try:
        api_url = f"https://api.github.com/repos/{GITHUB_REPO}/releases/latest"
        response = requests.get(api_url, timeout=5)
        response.raise_for_status()
        latest_version = response.json()["tag_name"].lstrip('v')
        current_version = __version__

        if latest_version > current_version:
            print("\n" + "="*50)
            print(f"  A new version ({latest_version}) is available!")
            print(f"  You are currently using version {current_version}.")
            print(f"  Please download the latest release from:")
            print(f"  https://github.com/{GITHUB_REPO}/releases/latest")
            print("="*50 + "\n")

    except requests.exceptions.RequestException as e:
        # It's okay if this fails, we don't want to block the user
        # print(f"\n[INFO] Could not check for updates: {e}")
        pass
    except Exception as e:
        # print(f"\n[INFO] An unexpected error occurred while checking for updates: {e}")
        pass

