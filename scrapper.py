from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import time
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import requests

# Function to set up a proxy with Selenium
def set_up_proxy(proxy_address):
    chrome_options = Options()
    chrome_options.add_argument('--proxy-server=%s' % proxy_address)
    return chrome_options

# LinkedIn login and URL extraction
def scrape_linkedin_posts(linkedin_username, linkedin_password, profile_url, proxy=None):
    # Set up the proxy if provided
    chrome_options = set_up_proxy(proxy) if proxy else None
    driver = webdriver.Chrome(options=chrome_options)
    
    try:
        driver.get("https://www.linkedin.com/login")
        
        # Perform loginsource myenv/bin/activate
        driver.find_element(By.ID, "username").send_keys(linkedin_username)
        driver.find_element(By.ID, "password").send_keys(linkedin_password)
        driver.find_element(By.XPATH, "//button[@type='submit']").click()
        
        time.sleep(3)
        
        # Navigate to the LinkedIn profile or company page
        driver.get(profile_url)
        
        # Scroll to load all posts
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(3)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height
        
        # Extract post URLs
        posts = driver.find_elements(By.CSS_SELECTOR, "a[href*='/posts/']")
        post_urls = [post.get_attribute('href') for post in posts]
    
    finally:
        driver.quit()
    
    return post_urls

# Google Sheets Integration
def add_to_google_sheets(sheet_name, post_urls):
    # Define the scope and credentials for Google Sheets API
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
    creds = ServiceAccountCredentials.from_json_keyfile_name("path_to_credentials.json", scope)
    client = gspread.authorize(creds)
    
    # Open the specified Google Sheet
    sheet = client.open(sheet_name).sheet1
    
    # Append each URL as a new row
    for url in post_urls:
        sheet.append_row([url])

# Main Execution
if __name__ == "__main__":
    linkedin_username = "your_email@example.com"
    linkedin_password = "your_password"
    profile_url = "https://www.linkedin.com/in/your-profile-url/"  # <-- Enter the LinkedIn profile or company page URL here
    proxy_address = "http://your_proxy_here"  # <-- Optional: Enter your proxy address here (if needed)

    # Scrape LinkedIn posts
    post_urls = scrape_linkedin_posts(linkedin_username, linkedin_password, profile_url, proxy=proxy_address)
    
    # Add the scraped URLs to Google Sheets
    sheet_name = "LinkedIn Posts"
    add_to_google_sheets(sheet_name, post_urls)
