from appwrite.client import Client
#from appwrite.services.messaging import Messaging
from appwrite.services.users import Users
from appwrite.services.databases import Databases
from appwrite.id import ID
import jwt
import os
import dotenv

dotenv.load_dotenv()

def main(context):
    client = Client()
    client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
    client.set_project(os.getenv('APPWRITE_PROJECT'))
    client.set_key(context.req.headers.get('x-appwrite-key'))
    
    #messaging = Messaging(client)
    users = Users(client)
    databases = Databases(client)
    email = users.get(context.req.headers.get('x-appwrite-user-id')).get('email')
    databases.create_document(os.getenv('APPWRITE_DATABASE'),
                              os.getenv('APPWRITE_SUBSCRIBERS_COLLECTION'),
                              context.req.headers.get('x-appwrite-user-id'),  
                              {
                               "email": email,
                               "accountDeletionVerificationCode": jwt.encode({"userId": context.req.headers.get('x-appwrite-user-id')}, os.getenv('JWTSECRET'), algorithm="HS256"),
                              })
    
    return context.res.empty()
