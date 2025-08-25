import appwrite
import requests
import os
import dotenv

dotenv.load_dotenv()

def main(context):
    # first, fetch the current appwrite configuration
    response = requests.get(f'https://raw.githubusercontent.com/{os.getenv('UPDATES_GITHUB_USERNAME')}/{os.getenv('UPDATES_GITHUB_RESPOSITORY')}/{os.getenv('UPDATES_GITHUB_BRANCH')}/appwrite.json')
    if response.status_code == 200:
        file_content = response.text
        print(file_content)
    else:
        print(f"Failed to fetch file: {response.status_code}")
        

main(context=None)