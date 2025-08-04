import feedparser
import requests
import re
import time
from appwrite.client import Client
from openai import OpenAI
import os

client = OpenAI(api_key=os.getenv("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com")


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

def main(context):
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
        
    # now we send this stuff into deepseek to anayalse for any possible new features coming up
    res = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "You are a helpful assistant which is given the past 10 commits and new lines of the Appwrite GitHub respository. THe Appwrite team sometimes adds new features in the code but prevent users from using them by using feature flags. Your job is to look at these commits and if you recognise that a new potential feature has been added (something that isn't yet in Appwrite), you must summarise the changes which made you notice this and give your best guess as to what it could be."},
        {"role": "user", "content": f"Last 10 commits of appwrite: {data}"},
    ],
    stream=False
    )

    anaylsis_response = res.choices[0].message.content
    
    res = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": ""},
        {"role": "user", "content": f"Last 10 commits of appwrite: {data}"},
    ],
    stream=False
    )

    
        
    context.res.json({
        "status": "success",
        "data": data
    })



        
        