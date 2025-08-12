from appwrite.client import Client
from appwrite.services.users import Users
from appwrite.services.databases import Databases
from appwrite.query import Query

def main(context):
    client = Client()
    client.set_endpoint('https://fra.cloud.appwrite.io/v1')
    client.set_project('6890d2c90034c3369acd')
    client.set_key(context.req.headers.get('x-appwrite-key'))
    
    users = Users(client)
    databases = Databases(client)
    userId = context.req.headers.get('x-appwrite-user-id')
    if userId == None:
        userId = databases.list_documents("6890ded500064cf8b023", "689791b100072ce22e05", queries=[Query.equal("accountDeletionVerificationCode", str(context.req.body))['documents'][0]])
    
    users.delete(
        user_id = userId
    )
        
    #email = users.get(userId).get('email')
    try:
        databases.delete_document("6890ded500064cf8b023", "689791b100072ce22e05", userId)
    except:
        pass

    
    
    return context.res.empty()
