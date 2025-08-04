import feedparser
import requests
import re
import time

data = []

ATOM_FEED = "https://github.com/appwrite/appwrite/commits.atom"

headers = {
    "Accept": "application/vnd.github.v3+json"
}

def extract_sha(url):
    match = re.search(r'/commit/([0-9a-f]{40})', url)
    return match.group(1) if match else None

def get_new_lines(patch):
    new_lines = []
    for line in patch.splitlines():
        if line.startswith('+') and not line.startswith('+++'):
            new_lines.append(line[1:])
    return new_lines

feed = feedparser.parse(ATOM_FEED)

for entry in feed.entries[:10]:
    api_url = f"https://api.github.com/repos/appwrite/appwrite/commits/{extract_sha(entry.link)}"
    response = requests.get(api_url, headers=headers)
    if response.status_code == 200:
        commit_data = response.json()
        for file in commit_data.get("files", []):
            filename = file.get("filename")
            patch = file.get("patch")
            if patch:
                new_lines = get_new_lines(patch)
                if new_lines:
                        data.append({
                            "title": entry.title,
                            "fileName": filename,
                            "newLines": new_lines,
                            "commitData":
                                {
                                    "link": entry.link,

                                }
                            })
                    
    else:
        print(f"Failed to fetch commit data: {response.status_code}")
    time.sleep(1)
    
print(data)
