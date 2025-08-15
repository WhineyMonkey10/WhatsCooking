from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.messaging import Messaging
from appwrite.id import ID
from appwrite.query import Query
import os
import dotenv

dotenv.load_dotenv()


# note: due to me not figuring out a way to send all emails all in one batch with a custom footer for each email
# this code will loop trhough all subscribers to generate their unsubscribe token
# just incase they want to unsubscribe.
# of course this isn't the most efficient way to do it but for now it works
def main(context):
    client = Client()
    client.set_endpoint(os.getenv('APPWRITE_ENDPOINT'))
    client.set_project(os.getenv('APPWRITE_PROJECT'))
    client.set_key(context.req.headers.get('x-appwrite-key'))
    
    databases = Databases(client)
    messaging = Messaging(client)

    # 1: identifiy the list of people.
    subscribers = databases.list_documents(os.getenv('APPWRITE_DATABASE'), os.getenv('APPWRITE_SUBSCRIBERS_COLLECTION'))
    
    # Initialize content string for each tracked branch
    branch_contents = {}
    tracked_branches = os.getenv('GITHUB_REPO_TRACKED_BRANCHES').split(',')
    
    # Get latest analysis for each tracked branch
    for branch in tracked_branches:
        branch = branch.strip()
        try:
            latest_analysis = databases.list_documents(
                os.getenv('APPWRITE_DATABASE'), 
                os.getenv('APPWRITE_ANALYSIS_COLLECTION'), 
                queries=[
                    Query.equal("trackedVersion", branch),
                    Query.order_desc("$createdAt"),
                    Query.limit(1)
                ]
            )
            
            if latest_analysis['documents']:
                branch_contents[branch] = latest_analysis['documents'][0]['newFeaturesAnalysis']
            else:
                branch_contents[branch] = "No recent updates available for this branch."
        except Exception as e:
            branch_contents[branch] = f"Error retrieving updates: {str(e)}"
    
    for subscriber in subscribers['documents']:
        # 2: get a unique unssubsribe token for each
        token = subscriber['accountDeletionVerificationCode']

        # Build email content with all branch updates
        email_content = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>What's Cooking? - {repo_name} Updates</title>
</head>
<body style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; line-height: 1.6; color: #1f2937; background-color: #f5f7fa; margin: 0; padding: 0;">
    <div style="max-width: 600px; margin: 0 auto; background-color: white; border-radius: 0.75rem; box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1); padding: 2rem; margin-top: 2rem;">
        <div style="text-align: center; margin-bottom: 1.5rem;">
            <div style="font-size: 2.5rem; margin-bottom: 1rem;">👨‍🍳</div>
            <h1 style="font-size: 1.75rem; color: #9333ea; margin-bottom: 0.5rem;">What's Cooking?</h1>
            <p style="font-size: 1.1rem; color: #4b5563; margin-top: 0;">Your {frequency} {repo_name} Feature Update</p>

            <!-- See More button -->
            <div style="margin-top: 1rem;">
                <a href="{site_url}"
                   style="display: inline-block; background-color: #9333ea; color: white; text-decoration: none; font-weight: 600; padding: 0.75rem 1.25rem; border-radius: 0.5rem;">
                   See More
                </a>
            </div>
        </div>

        <div style="padding: 1.5rem; background-color: #f9fafb; border-radius: 0.5rem; margin-bottom: 1.5rem; border: 1px solid #e5e7eb;">
            <h2 style="font-size: 1.25rem; color: #1f2937; margin-top: 0;">Hello!</h2>
            <p style="color: #4b5563;">Here is your {frequency} update on upcoming {repo_name} features:</p>

            {branch_sections}
        </div>

        <div style="text-align: center; margin-top: 2rem; padding-top: 1.5rem; border-top: 1px solid #e5e7eb;">
            <p style="color: #6b7280; font-size: 0.875rem;">
                Want to unsubscribe? 
                <a href="https://whatscooking.appwrite.network/?unsubscribeToken={token}" style="color: #9333ea; text-decoration: none; font-weight: 500;">Click here</a>
                to delete your account and stop receiving these updates.
            </p>
            <p style="color: #6b7280; font-size: 0.875rem; margin-top: 0.5rem;">
                Made with ❤️ using Appwrite • 
                <a href="https://whatscooking.appwrite.network/" style="color: #9333ea; text-decoration: none; font-weight: 500;">Make your own website like this</a>
            </p>
        </div>
    </div>
</body>
</html>
"""
        # Build branch sections
        branch_sections = []
        for branch, content in branch_contents.items():
            branch_section = f"""
            <!-- {branch} Section -->
            <div style="margin: 1.25rem 0; padding: 1rem; background-color: white; border-radius: 0.5rem; border: 1px solid #e5e7eb;">
                <h3 style="margin: 0 0 0.5rem 0; font-size: 1.1rem; color: #1f2937;">{os.getenv('TRACKED_REPO_NAME')} {branch}</h3>
                <div style="color: #4b5563;">
                    {content}
                </div>
            </div>
            """
            branch_sections.append(branch_section)
        
        # Join all branch sections with newlines
        all_branch_sections = "\n".join(branch_sections)
        
        # Format the email with all the variables
        formatted_email = email_content.format(
            repo_name=os.getenv('TRACKED_REPO_NAME'),
            frequency=os.getenv('EMAIL_FREQUENCY').capitalize(),
            site_url=os.getenv('APPWRITE_SITE_URL'),
            branch_sections=all_branch_sections,
            token=token
        )

        messaging.create_email(
            ID.unique(),
            f"Your {os.getenv('EMAIL_FREQUENCY').capitalize()} {os.getenv('TRACKED_REPO_NAME')} Upcoming Feature Update",
            formatted_email,
            users=[subscriber['$id']],
            html=True
        )
        
    return context.res.empty()

