from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.messaging import Messaging
from appwrite.id import ID


# note: due to me not figuring out a way to send all emails all in one batch with a custom footer for each email
# this code will loop trhough all subscribers to generate their unsubscribe token
# just incase they want to unsubscribe.
# of course this isn't the most efficient way to do it but for now it works
def main(context):
    client = Client()
    client.set_endpoint('https://fra.cloud.appwrite.io/v1')
    client.set_project('6890d2c90034c3369acd')
    client.set_key(context.req.headers.get('x-appwrite-key'))
    
    databases = Databases(client)
    messaging = Messaging(client)

    # 1: identifiy the list of people.
    subscribers = databases.list_documents("6890ded500064cf8b023", "6890dee0000a5ecd829e")
    
    for subscriber in subscribers:
        # 2: get a unique unssubsribe token for each
        token = subscriber.get('accountDeletionVerificationCode')

        messaging.create_email(
            ID.unique(),
            "Your Daily Appwrite Feature Update",
            f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>What's Cooking? - Appwrite Updates</title>
            </head>
            <body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; background-color: #f5f7fa; margin: 0; padding: 0;">
                <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); padding: 2rem; margin-top: 2rem;">
                    <div style="text-align: center; margin-bottom: 1.5rem;">
                        <div style="font-size: 2.5rem; margin-bottom: 1rem;">👨‍🍳</div>
                        <h1 style="font-size: 1.75rem; color: #9333ea; margin-bottom: 1rem;">What's Cooking?</h1>
                        <p style="font-size: 1.1rem; color: #4b5563;">Your Daily Appwrite Feature Update</p>
                    </div>
                    
                    <div style="padding: 1.5rem; background-color: #f9fafb; border-radius: 0.5rem; margin-bottom: 1.5rem; border: 1px solid #e5e7eb;">
                        <h2 style="font-size: 1.25rem; color: #1f2937; margin-top: 0;">Hello!</h2>
                        <p style="color: #4b5563;">Here is your daily update on upcoming Appwrite features:</p>
                        
                        <div style="margin: 1.5rem 0; padding: 1rem; background-color: white; border-radius: 0.5rem; border: 1px solid #e5e7eb;">
                            {context.req.body}
                        </div>
                    </div>
                    
                    <div style="text-align: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e5e7eb;">
                        <p style="color: #6b7280; font-size: 0.875rem;">
                            Want to unsubscribe? <a href="127.0.0.1:5502/?unsubscribeToken={token}" style="color: #9333ea; text-decoration: none; font-weight: 500;">Click here</a> to delete your account and stop receiving these updates.
                        </p>
                        <p style="color: #6b7280; font-size: 0.875rem; margin-top: 0.5rem;">
                            Made with ❤️ using Appwrite
                        </p>
                    </div>
                </div>
            </body>
            </html>
            """,
            users=[subscriber.get('$id')]
        )
        
        return context.res.empty()

