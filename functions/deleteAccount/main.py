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
    
    email = users.get(context.req.headers.get('x-appwrite-user-id')).get('email')

    databases.delete_document("6890ded500064cf8b023", "6890dee0000a5ecd829e", databases.get_document("6890ded500064cf8b023", "6890dee0000a5ecd829e", queries=[Query.equal("$id", [context.req.headers.get('x-appwrite-user-id')])]))
    
    users.delete(
        user_id = context.req.headers.get('x-appwrite-user-id')
    )
    
    
    
    return context.res.empty()
