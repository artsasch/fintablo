# Email Transaction Processor README

## Introduction
This Python script is designed to automatically process and categorize email transactions using IMAP. It fetches emails, extracts transaction details, and interacts with an external API to manage transaction data.

## Features
- Email fetching using IMAP.
- Parsing emails with BeautifulSoup.
- Categorization of transactions.
- API interactions to manage transaction data.
- Continuous monitoring for new emails with idle support.

## Requirements
- Python 3.x
- Libraries: `bs4`, `imapclient`, `requests`, `imaplib`, `email`, `time`, `json`, `ssl`, `re`
- A JSON file (`email_credentials.json`) containing email credentials.
- A JSON file (`headers.json`) for API headers.

## Installation
1. Ensure Python 3.x is installed.
2. Install required packages: `pip install bs4 imapclient requests`.
3. Place `email_credentials.json` and `headers.json` in the same directory as the script.

## Usage
1. Update `email_credentials.json` with your email credentials.
2. Run the script: `python [script_name].py`.
3. The script will continuously monitor the inbox for new emails.

## email_credentials.json Format
```json
{
  "EMAIL": "your-email@example.com",
  "PASSWORD": "your-password",
  "IMAP_SERVER": "imap.example.com"
}
```

## headers.json Format
Provide necessary headers for API requests in JSON format.

## Important Functions
- `process_email`: Processes each email, extracts transaction details, and makes API requests.
- `idle_and_wait_for_email`: Keeps the script running and checks for new emails.
- `find_or_create_partner`: Finds or creates a new partner based on the transaction details.

## Error Handling
The script includes basic error handling for connection issues and re-attempts connections if necessary.

## Notes
- Ensure proper security measures for handling email credentials.
- The script is configured for a specific email structure and API. Modifications might be necessary for different use cases.

## Disclaimer
Use this script responsibly and ensure compliance with email provider's terms of service and relevant laws/regulations.
