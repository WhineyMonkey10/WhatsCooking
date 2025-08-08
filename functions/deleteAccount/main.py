from appwrite.client import Client
from appwrite.services.users import Users


def main(context):
    client = Client()
    client.set_endpoint('https://fra.cloud.appwrite.io/v1')
    client.set_project('6890d2c90034c3369acd')
    client.set_key(context.req.headers.get('x-appwrite-key'))
    
    users = Users(client)

    users.delete(
        user_id = context.req.headers.get('x-appwrite-user-id')
    )
    
    return context.res.empty()
