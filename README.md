# linkedin-to-google-sheets-scraper

A Python script that automates the scraping of LinkedIn profiles using the ScrapIn.io API and uploads the scraped data to a Google Sheet using Google's Sheets API.

## Features
- Input LinkedIn profile URLs into a Google Sheet.
- Automatically scrape LinkedIn profiles using the ScrapIn.io API.
- Upload the scraped data to a specified tab in the same Google Sheet.

## Prerequisites
- Python 3.x
- A Google Cloud project with the Sheets API enabled
- ScrapIn.io API key
- OAuth 2.0 credentials for accessing Google Sheets

## Installation
1. Clone the repository:
    ```bash
    git clone https://github.com/your-username/linkedin-to-google-sheets-scraper.git
    cd linkedin-to-google-sheets-scraper
    ```

2. Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

3. Set up Google Sheets API credentials:
    - Follow the instructions [here](https://developers.google.com/sheets/api/quickstart/python) to create OAuth 2.0 credentials and download the `credentials.json` file.
    - Place the `credentials.json` file in the root directory of the project.

4. Set up ScrapIn.io API credentials:
    - Get your ScrapIn.io API key from [here](https://scrapin.io/).
    - Add your API key to the script.

## Usage
1. Update the `config.py` file with your Google Sheet ID and ScrapIn.io API key.

2. Run the script:
    ```bash
    python scraper.py
    ```

3. Input the desired LinkedIn profile URLs into the specified column in your Google Sheet.

4. The script will automatically scrape each profile and fill in the results on another tab within the Google Sheet.

## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
