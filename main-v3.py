import os
import asyncio
import aiohttp
import logging
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from backoff import on_exception, expo
from aiohttp import ClientError

# Google Sheets setup
SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SPREADSHEET_ID = os.getenv('GOOGLE_SHEET_ID')
API_KEY = os.getenv('SCRAPIN_API_KEY')

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def authenticate_google_api():
    """ Authenticate and return a Google Sheets API service instance. """
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    else:
        flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
        creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('sheets', 'v4', credentials=creds)

def format_history(items):
    """ Formats the list of history items into a string. """
    if not items:
        return 'N/A'
    lines = []
    for item in items:
        start = item.get('startEndDate', {}).get('start', {})
        end = item.get('startEndDate', {}).get('end', {})
        start_date = f"{start.get('month', '??')}/{start.get('year', '??')}"
        end_date = f"{end.get('month', '??')}/{end.get('year', '??')}" if end else 'Present'
        lines.append(f"{item.get('title', 'N/A')} at {item.get('companyName', 'N/A')} from {start_date} to {end_date}: {item.get('description', 'N/A')}")
    return "\n".join(lines)

async def fetch_linkedin_profile(session, url):
    """ Fetch LinkedIn profile data using the Scrapin.io API, ensuring URL format. """
    if not url.endswith('/'):
        url += '/'

    api_url = f"https://api.scrapin.io/enrichment/profile?apikey={API_KEY}&linkedinUrl={url}"
    try:
        async with session.get(api_url) as response:
            return await response.json(), response.status
    except ClientError as e:
        logging.error(f"Error fetching data for URL {url}: {e}")
        return None, None

@on_exception(expo, ClientError, max_tries=8)
def write_result(service, sheet_name, data):
    """ Write results to the specified sheet based on the status code. """
    person_data = data.get('person', {})
    company_data = data.get('company', {})
    values = [[
        person_data.get('publicIdentifier', 'N/A'),
        person_data.get('firstName', 'N/A'),
        person_data.get('lastName', 'N/A'),
        person_data.get('headline', 'N/A'),
        person_data.get('location', 'N/A'),
        person_data.get('photoUrl', 'N/A'),
        person_data.get('creationDate', {}).get('year', 'N/A'),
        person_data.get('followerCount', 'N/A'),
        person_data.get('connectionCount', 'N/A'),
        format_history(person_data.get('positions', {}).get('positionHistory', [])),
        ', '.join(person_data.get('skills', [])),
        ', '.join(person_data.get('languages', [])),
        company_data.get('name', 'N/A'),
        company_data.get('websiteUrl', 'N/A'),
        company_data.get('description', 'N/A'),
        company_data.get('tagline', 'N/A'),
        company_data.get('industry', 'N/A'),
        ', '.join(company_data.get('specialities', [])),
        company_data.get('linkedInUrl', 'N/A'),
        company_data.get('universalName', 'N/A'),
        company_data.get('headquarter', {}).get('city', 'N/A'),
        company_data.get('headquarter', {}).get('country', 'N/A'),
        company_data.get('employeeCount', 'N/A')
    ]]
    range_name = f'{sheet_name}!A2'
    body = {'values': values}
    try:
        service.spreadsheets().values().append(
            spreadsheetId=SPREADSHEET_ID,
            range=range_name,
            valueInputOption='USER_ENTERED',
            body=body,
            insertDataOption='INSERT_ROWS'
        ).execute()
    except Exception as e:
        logging.error(f'Failed to write data to {sheet_name}:', e)

async def fetch_urls_and_process(service):
    """ Fetch all URLs and process them asynchronously. """
    range_name = 'URLs!A:A'
    result = service.spreadsheets().values().get(spreadsheetId=SPREADSHEET_ID, range=range_name).execute()
    urls = result.get('values', [])
    urls = [url[0] for url in urls if url]

    async with aiohttp.ClientSession() as session:
        tasks = [fetch_linkedin_profile(session, url) for url in urls]
        results = await asyncio.gather(*tasks)
        for result, status_code in results:
            if result and status_code == 200:
                write_result(service, 'Status_200', result)

def main():
    logging.info("Authenticating Google API")
    service = authenticate_google_api()
    asyncio.run(fetch_urls_and_process(service))

if __name__ == '__main__':
    main()
