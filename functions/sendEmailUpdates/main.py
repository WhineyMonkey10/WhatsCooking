from appwrite.client import Client
from appwrite.services.databases import Databases
from appwrite.services.messaging import Messaging
from appwrite.id import ID
from appwrite.query import Query
import os
import dotenv
import datetime
# Replace direct Gemini import with Langchain imports
from langchain.chat_models import init_chat_model
from langchain_core.messages import HumanMessage, SystemMessage
import json


# Configure Gemini

dotenv.load_dotenv()

# Initialize the LLM using Langchain instead of direct Gemini API
llm = init_chat_model("gemini-2.5-flash", model_provider="google_genai")

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
    
    # Parse the tracked branches properly - convert from JSON string to list
    tracked_branches_raw = os.getenv('GITHUB_REPO_TRACKED_BRANCHES', '[]')
    try:
        # Try to parse as JSON
        tracked_branches = json.loads(tracked_branches_raw)
    except json.JSONDecodeError:
        # If JSON parsing fails, fallback to splitting by comma
        tracked_branches = [branch.strip() for branch in os.getenv('GITHUB_REPO_TRACKED_BRANCHES', '').split(',')]
    
    # Calculate the time range based on email frequency
    # Determine time period based on frequency
    frequency = os.getenv('EMAIL_FREQUENCY', 'weekly').lower()
    current_time = datetime.datetime.now()
    
    if frequency == 'daily':
        # Past 24 hours
        time_limit = current_time - datetime.timedelta(days=1)
    elif frequency == 'weekly':
        # Past 7 days
        time_limit = current_time - datetime.timedelta(days=7)
    elif frequency == 'monthly':
        # Past 30 days
        time_limit = current_time - datetime.timedelta(days=30)
    else:
        # Default to weekly if unknown frequency
        time_limit = current_time - datetime.timedelta(days=7)
    
    # Format the time for Appwrite query
    time_limit_iso = time_limit.strftime('%Y-%m-%dT%H:%M:%S.%fZ')
    
    # Get latest analysis for each tracked branch
    for branch in tracked_branches:
        # Clean the branch name to remove any quotes or brackets
        branch = branch.strip('[]"\' ')
        
        try:
            latest_analysis = databases.list_documents(
                database_id=os.getenv('APPWRITE_DATABASE'), 
                collection_id=os.getenv('APPWRITE_PUBLIC_COLLECTION'), 
                queries=[
                    Query.equal("trackedVersion", branch),
                    Query.greater_than("$createdAt", time_limit_iso),
                    Query.order_desc("$createdAt"),
                    ]
            )
            if latest_analysis['documents']:
                # Collect all analyses from the time period for Gemini to process
                analyses_text = []
                dates = []
                
                for doc in latest_analysis['documents']:
                    # Only include if it has content
                    if doc['newFeaturesAnalysis'] and len(doc['newFeaturesAnalysis'].strip()) > 0:
                        analyses_text.append(doc['newFeaturesAnalysis'])
                        dates.append(doc['$createdAt'])
                
                if analyses_text:
                    # Use Langchain to process content instead of direct Gemini API
                    try:
                        # Create a system message with instructions
                        system_prompt = f"""You are an expert technical analyst summarizing Appwrite feature developments for branch {branch}.
You're creating a summary of multiple analysis reports from the past {frequency} period.

Create a concise summary that:
1. Highlights the most important potential features or changes
2. Groups related changes together
3. Shows progression of features over time if applicable
4. Provides a clear, organized overview suitable for an email newsletter

Your response should use HTML formatting (just basic tags like <h3>, <p>, <ul>, <li>) as it will be displayed in an email.
Be informative but concise."""

                        # Create the human message with the analyses data
                        analyses_content = "\n\n".join([f"ANALYSIS {i+1} (Date: {dates[i]}):\n{text}" for i, text in enumerate(analyses_text)])
                        human_prompt = f"Here are {len(analyses_text)} analyses to summarize, listed from newest to oldest:\n\n{analyses_content}"
                        
                        # Use Langchain to generate content
                        response = llm.invoke([
                            SystemMessage(system_prompt),
                            HumanMessage(human_prompt)
                        ])
                        
                        # Extract the text content from the response
                        summarized_analysis = response.content
                        
                        # Use the Langchain-generated summary
                        branch_contents[branch] = summarized_analysis
                        
                    except Exception as e:
                        # If Langchain processing fails, use the most recent analysis with error note
                        branch_contents[branch] = analyses_text[0]
                        branch_contents[branch] = f"Note: Automatic summary unavailable. Here's the most recent analysis:\n\n{branch_contents[branch]}"
                        print(f"Error using Langchain/Gemini API: {str(e)}")
                else:
                    branch_contents[branch] = "No meaningful updates found for this branch in the specified time period."
            else:
                # Fall back to just getting the most recent document without time filtering
                fallback_analysis = databases.list_documents(
                    database_id=os.getenv('APPWRITE_DATABASE'), 
                    collection_id=os.getenv('APPWRITE_PUBLIC_COLLECTION'), 
                    queries=[
                        Query.equal("trackedVersion", branch),
                        Query.order_desc("$createdAt"),
                        Query.limit(1)
                    ]
                )
                
                if fallback_analysis['documents']:
                    branch_contents[branch] = fallback_analysis['documents'][0]['newFeaturesAnalysis']
                    branch_contents[branch] = "No recent updates available for this branch in the past " + frequency + " period. Here's the latest update: \n\n" + branch_contents[branch]
                else:
                    branch_contents[branch] = "No updates available for this branch."
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
            # Remove any square brackets or quotes from the branch name
            clean_branch = branch.strip('[]"\' ')
            
            branch_section = f"""
            <!-- {clean_branch} Section -->
            <div style="margin: 1.25rem 0; padding: 1rem; background-color: white; border-radius: 0.5rem; border: 1px solid #e5e7eb;">
                <h3 style="margin: 0 0 0.5rem 0; font-size: 1.1rem; color: #1f2937;">{os.getenv('TRACKED_REPO_NAME')} {clean_branch}</h3>
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

