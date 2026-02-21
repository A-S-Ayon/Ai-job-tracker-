from playwright.sync_api import sync_playwright
import time
import random
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

def scrape_jobs(url: str, max_jobs: int = 1000) -> list[dict]:
    """Scrapes dynamic job boards with pagination up to max_jobs."""
    jobs = []
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080}
        )
        page = context.new_page()
        
        logging.info(f"Navigating to {url}...")
        try:
            page.goto(url, wait_until="networkidle", timeout=30000)
            
            # Pagination Loop
            while len(jobs) < max_jobs:
                # Random delay per page to avoid getting blocked
                time.sleep(random.uniform(2.0, 4.0))

                job_rows = page.locator('tr.athing').all()
                logging.info(f"Found {len(job_rows)} jobs on current page. Extracting...")

                for row in job_rows:
                    if len(jobs) >= max_jobs:
                        break # Stop immediately if we hit our target

                    try:
                        title_element = row.locator('span.titleline a').first
                        
                        if title_element.count() == 0:
                            continue

                        title = title_element.inner_text().strip()
                        link = title_element.get_attribute('href')
                        company = "Check Title" 
                        description = "Description not available on list page."
                        
                        if title and link:
                            if link.startswith('item?id='):
                                link = f"https://news.ycombinator.com/{link}"

                            jobs.append({
                                "title": title,
                                "company": company,
                                "url": link,
                                "description": description
                            })
                    except Exception as e:
                        logging.warning(f"Skipped a job row due to parsing error: {e}")

                logging.info(f"Total jobs extracted so far: {len(jobs)}")
                
                if len(jobs) >= max_jobs:
                    logging.info("Reached maximum job target. Stopping pagination.")
                    break

                # --- PAGINATION LOGIC ---
                # Look for the "More" link at the bottom of the page
                more_link = page.locator('a.morelink').first
                
                if more_link.count() > 0:
                    logging.info("Clicking 'More' to load the next page...")
                    more_link.click()
                    # Wait for the new page to settle before looping again
                    page.wait_for_load_state("networkidle") 
                else:
                    logging.info("No more pages available. Ending scraping.")
                    break # Exit the while loop if there's no "More" button

        except Exception as e:
            logging.error(f"Failed to scrape {url}: {e}")
        finally:
            browser.close()
            
    return jobs

# --- Testing Block ---
if __name__ == "__main__":
    print("Testing paginated Playwright scraper.py...")
    test_url = "https://news.ycombinator.com/jobs" 
    
    # We will try to pull 1000, but it will stop early if HN has less than that
    extracted_jobs = scrape_jobs(test_url, max_jobs=1000)
    print(f"\nSUCCESS: Extracted a total of {len(extracted_jobs)} jobs across all pages!")