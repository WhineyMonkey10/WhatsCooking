from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.databases import Databases
from appwrite.query import Query
import os
import dotenv

dotenv.load_dotenv()

def main(context):
    client = Client()
    client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
    client.set_project(os.getenv('APPWRITE_PROJECT'))
    client.set_key(context.req.headers.get('x-appwrite-key'))
    
    users = Users(client)
    databases = Databases(client)
    userId = context.req.headers.get('x-appwrite-user-id')
    if userId == None:
        userId = databases.list_documents(os.getenv('APPWRITE_DATABASE'), os.getenv('APPWRITE_SUBSCRIBERS_COLLECTION'), queries=[Query.equal("accountDeletionVerificationCode", str(context.req.body))])['documents'][0]['$id']
    
    users.delete(
        user_id = userId
    )
        
    #email = users.get(userId).get('email')
    try:
        databases.delete_document(os.getenv('APPWRITE_DATABASE'), os.getenv('APPWRITE_SUBSCRIBERS_COLLECTION'), userId)
    except:
        pass

    
    
    return context.res.empty()
