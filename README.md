# LinkedIn Comments Email Scraper

A Python tool that scrapes email addresses from LinkedIn post comments. This tool uses Selenium WebDriver to automate browser interactions and extract emails from comment sections.

## ⚠️ Important Disclaimer

**Use this tool responsibly and ethically:**
- Only scrape posts where you have permission to do so
- Respect LinkedIn's Terms of Service
- Be mindful of privacy and data protection laws (GDPR, CCPA, etc.)
- Use the extracted emails only for legitimate business purposes
- Consider reaching out to post authors for permission first

## Features

- 🔍 Extracts email addresses from LinkedIn post comments
- 🔄 Automatically loads all comments (clicks "Show more" buttons)
- 💾 Saves results to text file
- 🚪 Requires LinkedIn login for access
- 🚀 Command-line interface with options
- 😵‍💫 Headless browser support

## Prerequisites

1. **Python 3.7+**
2. **Google Chrome browser** (latest version recommended)
3. **ChromeDriver** (automatically managed by webdriver-manager)
4. **LinkedIn account** with access to the posts you want to scrape

## Installation

1. **Clone or download this repository**

2. **Install required packages:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Verify Chrome is installed:**
   - The tool uses Chrome WebDriver, so make sure Google Chrome is installed on your system

## Usage

### Command Line Interface

```bash
python linkedin_scraper.py "https://www.linkedin.com/posts/username_activity-id" --email your-email@example.com --password your-password
```

**Options:**
- `--email`: Your LinkedIn login email (required)
- `--password`: Your LinkedIn login password (required)
- `--output` or `-o`: Output file name (default: `scraped_emails.txt`)
- `--headless`: Run browser in headless mode (no GUI)
- `--wait-time`: Maximum wait time for page loads in seconds (default: 10)

### Interactive Example

```bash
python example_usage.py
```

This will prompt you for:
- LinkedIn post URL
- Your LinkedIn credentials
- Run the scraper interactively

### Python Script Usage

```python
from linkedin_scraper import LinkedInCommentsScraper

# Create scraper instance
with LinkedInCommentsScraper(headless=True) as scraper:
    # Login to LinkedIn
    if scraper.login_to_linkedin("your-email@example.com", "your-password"):
        # Scrape comments from a post
        emails = scraper.scrape_comments("https://www.linkedin.com/posts/example-post")
        
        # Print found emails
        for email in emails:
            print(email)
        
        # Save to file
        scraper.save_emails_to_file(emails, "output.txt")
```

## How It Works

1. **Login**: Authenticates with LinkedIn using provided credentials
2. **Navigate**: Goes to the specified LinkedIn post URL
3. **Load Comments**: Automatically clicks "Show more comments" to load all comments
4. **Extract**: Uses regex pattern to find email addresses in comment text
5. **Save**: Outputs unique emails to console and saves to file

## Supported LinkedIn URL Formats

- `https://www.linkedin.com/posts/username_activity-id`
- `https://www.linkedin.com/feed/update/urn:li:activity:id`

## Output

The tool will:
- Display found emails in the console
- Save all unique emails to a text file (one per line)
- Show total count of emails found

## Troubleshooting

### Common Issues

1. **ChromeDriver not found**
   - The tool uses `webdriver-manager` to automatically download ChromeDriver
   - Ensure you have internet connection on first run

2. **Login fails**
   - Check your LinkedIn credentials
   - LinkedIn may require 2FA - try logging in manually first
   - Your account might be temporarily restricted

3. **No comments found**
   - The post might not have comments
   - Comments might be restricted or private
   - LinkedIn's HTML structure may have changed

4. **Timeout errors**
   - Increase `--wait-time` parameter
   - Check your internet connection
   - LinkedIn might be slow to respond
     
5. **It looks like you aren't entering a password**
   - This is purposeful. The program is recording your key strokes but your cursor won't move.

### Debug Mode

Run without `--headless` flag to see the browser automation in action:

```bash
python linkedin_scraper.py "post-url" --email your-email --password your-password
```

## Email Regex Pattern

The tool uses this regex pattern to extract emails:
```regex
\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b
```

This pattern matches most standard email formats but may not catch every edge case.

## Rate Limiting

To avoid being blocked by LinkedIn:
- Don't run the tool too frequently
- Use reasonable wait times between requests
- Respect LinkedIn's robots.txt and terms of service

## Legal and Ethical Considerations

- **Always obtain permission** before scraping someone's content
- **Respect privacy** - don't use extracted emails for spam
- **Follow local laws** regarding data collection and privacy
- **LinkedIn ToS** - Be aware that web scraping may violate LinkedIn's terms
- **Rate limiting** - Don't overload LinkedIn's servers

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is for educational purposes. Use responsibly and at your own risk.

---
