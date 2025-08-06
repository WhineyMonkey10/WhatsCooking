import feedparser
import requests
import re
import time
from appwrite.client import Client
from pydantic import BaseModel, Field
import os
import dotenv
from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.id import ID
from langchain.chat_models import init_chat_model
from typing_extensions import Annotated, TypedDict
from langchain_core.messages import HumanMessage, SystemMessage


dotenv.load_dotenv()

data = []

headers = {
    "Accept": "application/vnd.github.v3+json"
}

# ai init stuff

class AnalysisFormat(BaseModel):
    """This is the response format for all AI responses for analysis."""
    analysis: str = Field(description="A short summary of what you believe to be a hidden feature, if no hidden features were found, ensure to make it very clearly stated in this part.")
    foundHiddenFeature: bool = Field(description="Whether or not you have detected a possible hidden feature in the Appwrite codebase commits provided to you.")

llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai") # init gemini
structured_llm = llm.with_structured_output(AnalysisFormat) # init strucuted response gemini that we can invoke later


def extract_sha(url):
    match = re.search(r'/commit/([0-9a-f]{40})', url)
    return match.group(1) if match else None

def get_new_lines(patch):
    new_lines = []
    for line in patch.splitlines():
        if line.startswith('+') and not line.startswith('+++'):
            new_lines.append(line[1:])
    return new_lines


def main(context):
    client = Client()
    client.set_endpoint('https://fra.cloud.appwrite.io/v1')
    client.set_project('6890d2c90034c3369acd')
    client.set_key(context.req.headers.get('x-appwrite-key'))
    
    databases = Databases(client)
    
    """
    Expected request body:
    
    {
        "trackedVersions": ["1.7.x", "1.8.x"] 
    }
    this makes it so that the code can proeprly parse the versions to track and makes it
    so that i dont need to update the code whenver a new version is reelased and i can just
    change the cronjob stuff
    """
    tracked_versions = context.req.body.get('trackedVersions', [])

    for versionToTrack in tracked_versions:
        feed = feedparser.parse(f"https://github.com/appwrite/appwrite/commits/{versionToTrack}.atom")
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
            
        resStructered = structured_llm.invoke([
            SystemMessage("You are a helpful assistant which is given the past 10 commits and new lines of the Appwrite GitHub respository. THe Appwrite team sometimes adds new features in the code but prevent users from using them by using feature flags. Your job is to look at these commits and if you recognise that a new potential feature has been added (something that isn't yet in Appwrite), you must summarise the changes which made you notice this and give your best guess as to what it could be. Your response will be shown on a website, so then don't say stuff like 'Ask me for more info if you want', etc."),
            HumanMessage(f"Here is the data for the previous 10 commits of the Appwrite Github repo: {data}")
        ])
        
        #print(resStructered)

        
        # no strucuted lllm here since it's jisut a summary

        res = llm.invoke([
            SystemMessage("Summarise these GitHub Commits in a clear, concise and beautiful way. Use markdown, however do not use a title. Your format should always be the following (of course with new lines in the appropriate places): Summary Title         Summary Details          Embedded link to the commit"),
            HumanMessage(f"Here is the data for the previous 10 commits of the Appwrite Github repo: {data}")
        ])
        
        #print(res)
        
        summary_response = res.content
        
        #print(summary_response)
        
        documentCreationRes = databases.create_document(
            database_id = '6890ded500064cf8b023',
            collection_id = '6890dee0000a5ecd829e',
            document_id = ID.unique(),
            data = {
                "summary": summary_response,
                "newFeaturesAnalysis": resStructered.analysis, # fetch the potential analysis from the strucuted ai response
                "newFeatureFlag": bool(resStructered.foundHiddenFeature),
                "trackedVersion": versionToTrack
                },

            )
    
    return context.res.empty()
    #print(documentCreationRes)
        
        
main(context=None)