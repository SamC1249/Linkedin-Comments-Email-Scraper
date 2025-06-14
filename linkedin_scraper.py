#!/usr/bin/env python3
"""
LinkedIn Comments Email Scraper

A tool to scrape emails from LinkedIn post comments.
Note: This tool requires proper authentication and respects LinkedIn's terms of service.
"""

import re
import requests
import time
import json
import argparse
from typing import List, Set
from urllib.parse import urlparse, parse_qs
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from bs4 import BeautifulSoup


class LinkedInCommentsScraper:
    def __init__(self, headless=True, wait_time=10):
        """
        Initialize the LinkedIn Comments Scraper
        
        Args:
            headless (bool): Run browser in headless mode
            wait_time (int): Maximum wait time for elements to load
        """
        self.wait_time = wait_time
        self.driver = None
        self.setup_driver(headless)
        
    def setup_driver(self, headless=True):
        """Setup Chrome WebDriver with appropriate options"""
        chrome_options = Options()
        if headless:
            chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--window-size=1920,1080")
        chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        
        try:
            self.driver = webdriver.Chrome(options=chrome_options)
        except Exception as e:
            print(f"Error setting up Chrome driver: {e}")
            print("Please ensure ChromeDriver is installed and in PATH")
            raise
    
    def extract_emails_from_text(self, text: str) -> Set[str]:
        """
        Extract email addresses from text using regex
        
        Args:
            text (str): Text to search for emails
            
        Returns:
            Set[str]: Set of unique email addresses found
        """
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        emails = re.findall(email_pattern, text)
        return set(emails)
    
    def validate_linkedin_url(self, url: str) -> bool:
        """
        Validate if the URL is a LinkedIn post URL
        
        Args:
            url (str): URL to validate
            
        Returns:
            bool: True if valid LinkedIn post URL
        """
        parsed_url = urlparse(url)
        return (
            'linkedin.com' in parsed_url.netloc and
            ('/posts/' in parsed_url.path or '/feed/update/' in parsed_url.path)
        )
    
    def login_to_linkedin(self, email: str, password: str) -> bool:
        """
        Login to LinkedIn (required for accessing comments)
        
        Args:
            email (str): LinkedIn email
            password (str): LinkedIn password
            
        Returns:
            bool: True if login successful
        """
        try:
            self.driver.get("https://www.linkedin.com/login")
            
            # Wait for and fill email
            email_field = WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((By.ID, "username"))
            )
            email_field.send_keys(email)
            
            # Fill password
            password_field = self.driver.find_element(By.ID, "password")
            password_field.send_keys(password)
            
            # Click login button
            login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            login_button.click()
            
            # Wait for successful login (check for feed or dashboard)
            WebDriverWait(self.driver, self.wait_time).until(
                EC.any_of(
                    EC.url_contains("/feed/"),
                    EC.url_contains("/dashboard/"),
                    EC.presence_of_element_located((By.CLASS_NAME, "global-nav"))
                )
            )
            
            print("Successfully logged in to LinkedIn")
            return True
            
        except TimeoutException:
            print("Login failed: Timeout waiting for login to complete")
            return False
        except Exception as e:
            print(f"Login failed: {e}")
            return False
    
    def load_all_comments(self) -> None:
        """
        Load all comments by clicking 'Show more comments' buttons and scrolling
        """
        last_height = 0
        retries = 3  # Number of retries when no new content is loaded
        attempts = 0
        
        try:
            while attempts < retries:
                # Scroll down to load more comments
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)  # Wait for any lazy-loaded content
                
                # Check if we've reached the bottom
                new_height = self.driver.execute_script("return document.body.scrollHeight")
                if new_height == last_height:
                    attempts += 1
                    continue
                    
                last_height = new_height
                attempts = 0  # Reset attempts if we found new content
                
                # Look for "Show more comments" or similar buttons
                show_more_selectors = [
                    "button[aria-label*='more comments']",
                    "button:contains('Show more comments')",
                    "button:contains('Show previous comments')",
                    "button.comments-comments-list__load-more-comments-button",
                    "button.comments-comments-list__load-more-comments",
                    "button.comments-comments-list__load-more-replies",
                    "button.comments-comment-social-bar__replies-count",
                    "button.comments-comment-social-bar__replies-count--multiple",
                    "button.comments-comment-social-bar__replies-count--single"
                ]
                
                for selector in show_more_selectors:
                    try:
                        buttons = self.driver.find_elements(By.CSS_SELECTOR, selector)
                        for btn in buttons:
                            try:
                                if btn.is_displayed():
                                    self.driver.execute_script("arguments[0].click();", btn)
                                    time.sleep(1)  # Wait for comments to load
                            except Exception:
                                continue
                    except Exception:
                        continue
                        
        except Exception as e:
            print(f"Error in load_all_comments: {e}")
                        
        except Exception as e:
            print(f"Error in load_all_comments: {e}")

    def scrape_comments(self, post_url: str) -> Set[str]:
        """
        Scrape comments from a LinkedIn post and extract emails
        
        Args:
            post_url (str): LinkedIn post URL
            
        Returns:
            Set[str]: Set of unique email addresses found in comments
        """
        if not self.validate_linkedin_url(post_url):
            raise ValueError("Invalid LinkedIn post URL")
        
        all_emails = set()
        
        try:
            # Navigate to the post
            self.driver.get(post_url)
            
            # Wait for the page to load
            WebDriverWait(self.driver, self.wait_time).until(
                EC.presence_of_element_located((By.TAG_NAME, "body"))
            )
            
            # Load all comments
            self.load_all_comments()
            
            # Get page source and parse with BeautifulSoup
            page_source = self.driver.page_source
            soup = BeautifulSoup(page_source, 'html.parser')
            
            # Find comment sections - LinkedIn uses various class names
            comment_selectors = [
                '.comments-comment-item',
                '.feed-shared-update-v2__commentary',
                '.comments-comment-item__main-content',
                '[data-test-id="comments-comment-item"]',
                '.comment',
                '.social-details-social-activity'
            ]
            
            comments_found = False
            
            for selector in comment_selectors:
                comments = soup.select(selector)
                if comments:
                    comments_found = True
                    print(f"Found {len(comments)} comment elements with selector: {selector}")
                    
                    for comment in comments:
                        comment_text = comment.get_text(strip=True)
                        emails = self.extract_emails_from_text(comment_text)
                        all_emails.update(emails)
            
            # Also search the entire page content as fallback
            if not comments_found:
                print("Specific comment selectors not found, searching entire page...")
                page_text = soup.get_text()
                emails = self.extract_emails_from_text(page_text)
                all_emails.update(emails)
            
            # Additional search in script tags (sometimes data is in JSON)
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string:
                    emails = self.extract_emails_from_text(script.string)
                    all_emails.update(emails)
            
            print(f"Total emails found: {len(all_emails)}")
            return all_emails
            
        except TimeoutException:
            print("Timeout: Page took too long to load")
            return set()
        except Exception as e:
            print(f"Error scraping comments: {e}")
            return set()
    
    def save_emails_to_file(self, emails: Set[str], filename: str = "scraped_emails.txt") -> None:
        """
        Save scraped emails to a file
        
        Args:
            emails (Set[str]): Set of email addresses
            filename (str): Output filename
        """
        try:
            with open(filename, 'w', encoding='utf-8') as f:
                for email in sorted(emails):
                    f.write(f"{email}\n")
            print(f"Emails saved to {filename}")
        except Exception as e:
            print(f"Error saving emails to file: {e}")
    
    def close(self):
        """Close the web driver and clean up resources"""
        if self.driver:
            self.driver.quit()
            self.driver = None
    
    def __enter__(self):
        """Enter the runtime context related to this object."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Exit the runtime context and perform cleanup."""
        self.close()
        return False  # Don't suppress any exceptions


def main():
    parser = argparse.ArgumentParser(description="Scrape emails from LinkedIn post comments")
    parser.add_argument("url", help="LinkedIn post URL")
    parser.add_argument("--email", help="LinkedIn login email", required=True)
    parser.add_argument("--password", help="LinkedIn login password", required=True)
    parser.add_argument("--output", "-o", help="Output file for emails", default="scraped_emails.txt")
    parser.add_argument("--headless", action="store_true", help="Run in headless mode")
    parser.add_argument("--wait-time", type=int, default=10, help="Wait time for page loads")
    
    args = parser.parse_args()
    
    try:
        with LinkedInCommentsScraper(headless=args.headless, wait_time=args.wait_time) as scraper:
            # Login to LinkedIn
            if not scraper.login_to_linkedin(args.email, args.password):
                print("Failed to login to LinkedIn. Please check your credentials.")
                return
            
            # Scrape comments for emails
            print(f"Scraping comments from: {args.url}")
            emails = scraper.scrape_comments(args.url)
            
            if emails:
                print(f"\nFound {len(emails)} unique email(s):")
                for email in sorted(emails):
                    print(f"  - {email}")
                
                # Save to file
                scraper.save_emails_to_file(emails, args.output)
            else:
                print("No emails found in the comments.")
                
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()

