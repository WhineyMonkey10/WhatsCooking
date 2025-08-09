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
    client.set_endpoint('https://fra.cloud.appwrite.io/v1')
    client.set_project('6890d2c90034c3369acd')
    client.set_key(context.req.headers.get('x-appwrite-key'))
    
    #messaging = Messaging(client)
    users = Users(client)
    databases = Databases(client)
    email = users.get(context.req.headers.get('x-appwrite-user-id')).get('email')
    databases.create_document("6890ded500064cf8b023",
                              "689791b100072ce22e05",
                              context.req.headers.get('x-appwrite-user-id'),  
                              {
                               "email": email,
                               "accountDeletionVerificationCode": jwt.encode({"userId": context.req.headers.get('x-appwrite-user-id')}, os.getenv('JWTSECRET'), algorithm="HS256"),
                              })
    # instead we will add a user's email to a db as it is currently not possible to programatically list all topic targets
    
    # get the user
    #targetid = users.get(user_id = context.req.headers.get('x-appwrite-user-id')).get('targets')[0].get('$id')
    #
#
#
    #messaging.create_subscriber(
    #    topic_id = '6893e43200176f6008bf', 
    #    subscriber_id = ID.unique(), 
    #    target_id = targetid
    #)
    
    return context.res.empty()
