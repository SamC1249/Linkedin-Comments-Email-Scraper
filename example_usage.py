#!/usr/bin/env python3
"""
Example usage of the LinkedIn Comments Email Scraper
"""

'''run virtual env:    .\linkedin_scraper_env\Scripts\Activate.ps1'''

from linkedin_scraper import LinkedInCommentsScraper
import getpass

def main():
    # Example LinkedIn post URL
    post_url = input("Enter LinkedIn post URL: ")
    
    # Get login credentials securely
    email = input("Enter your LinkedIn email: ")
    password = getpass.getpass("Enter your LinkedIn password: ")
    
    # Create scraper instance
    with LinkedInCommentsScraper(headless=False, wait_time=15) as scraper:
        # Login
        print("Logging in to LinkedIn...")
        if not scraper.login_to_linkedin(email, password):
            print("Failed to login. Please check your credentials.")
            return
        
        # Scrape comments
        print(f"Scraping comments from: {post_url}")
        emails = scraper.scrape_comments(post_url)
        
        # Display results
        if emails:
            print(f"\nFound {len(emails)} unique email addresses:")
            for email_addr in sorted(emails):
                print(f"  📧 {email_addr}")
            
            # Save to file
            output_file = "found_emails.txt"
            scraper.save_emails_to_file(emails, output_file)
            print(f"\nEmails saved to: {output_file}")
        else:
            print("\nNo email addresses found in the comments.")

if __name__ == "__main__":
    main()

