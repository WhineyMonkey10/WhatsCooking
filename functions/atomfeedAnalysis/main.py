import feedparser
import requests
import re
import time
from appwrite.client import Client
from openai import OpenAI
import os
import dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID



dotenv.load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), base_url="https://api.deepseek.com")


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
    client = Client()
    client.set_endpoint('https://fra.cloud.appwrite.io/v1')
    client.set_project('6890d2c90034c3369acd')
    client.set_key(context.req('x-appwrite-key'))
    
    databases = Databases(client)
    
    for entry in feed.entries[:5]:
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
        {"role": "system", "content": "You are a helpful assistant which is given the past 10 commits and new lines of the Appwrite GitHub respository. THe Appwrite team sometimes adds new features in the code but prevent users from using them by using feature flags. Your job is to look at these commits and if you recognise that a new potential feature has been added (something that isn't yet in Appwrite), you must summarise the changes which made you notice this and give your best guess as to what it could be. Your response will be shown on a website, so then don't say stuff like 'Ask me for more info if you want', etc."},
        {"role": "user", "content": f"Last 10 commits of appwrite: {data}"},
    ],
    stream=False
    )

    anaylsis_response = res.choices[0].message.content
    
    res = client.chat.completions.create(
    model="deepseek-chat",
    messages=[
        {"role": "system", "content": "Summarise these GitHub Commits in a clear, concise and beautiful way."},
        {"role": "user", "content": f"Last 10 commits of appwrite: {data}"},
    ],
    stream=False
    )
    
    summary_response = res.choices[0].message.content
    
    documentCreationRes = databases.create_document(
    database_id = '6890ded500064cf8b023',
    collection_id = '6890dee0000a5ecd829e',
    document_id = ID.unique(),
    data = {
        "summary": summary_response,
        "newFeaturesAnalysis": anaylsis_response
        },

    )
    
    context.res.json({
        "status": documentCreationRes
    })
        