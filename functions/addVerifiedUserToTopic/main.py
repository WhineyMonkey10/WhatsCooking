from appwrite.client import Client
from appwrite.services.messaging import Messaging
from appwrite.services.users import Users
from appwrite.id import ID



def main(context):
    client = Client()
    client.set_endpoint('https://fra.cloud.appwrite.io/v1')
    client.set_project('6890d2c90034c3369acd')
    client.set_key(context.req.headers.get('x-appwrite-key'))
    
    messaging = Messaging(client)
    users = Users(client)
    
    # get the user
    targetid = users.get(user_id = context.req.headers.get('x-appwrite-user-id')).get('targets')[0].get('$id')
    


    messaging.create_subscriber(
        topic_id = '6893e43200176f6008bf', 
        subscriber_id = ID.unique(), 
        target_id = targetid
    )
    
    return context.res.empty()
