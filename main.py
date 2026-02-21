import time
import logging
import db
import scraper
import evaluator
import notifier

# Set up clean logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# We'll use Hacker News for our first full integration test
TARGET_URL = "https://news.ycombinator.com/jobs"

def main():
    logging.info("Starting the AI-Powered Job Opportunity Tracker...")
    
    # 1. Initialize Database
    db.init_db()
    
    # 2. Scrape Jobs (Limiting to 15 for this test run so we don't wait too long)
    logging.info(f"Scraping jobs from {TARGET_URL}...")
    jobs = scraper.scrape_jobs(TARGET_URL, max_jobs=15) 
    logging.info(f"Found {len(jobs)} jobs. Beginning processing...")

    for job in jobs:
        url = job['url']
        
        # 3. Check Database State
        if db.job_exists(url):
            logging.info(f"⏭️ Skipping known job: {job['title'][:30]}...")
            continue
            
        logging.info(f"🧠 Evaluating new job: {job['title'][:30]}...")
        
        # 4. AI Evaluation
        eval_result = evaluator.evaluate_job(job['title'], job['description'])
        score = eval_result.get('score', 0)
        is_agency = eval_result.get('is_agency', False)
        summary = eval_result.get('summary', 'No summary provided.')

        # 5. Delivery Logic (Only send if score >= 5 and it's not a recruiting agency)
        if score >= 5 and not is_agency:
            logging.info(f"🎯 MATCH FOUND! Score {score}. Sending Telegram alert...")
            notifier.send_telegram_alert(
                title=job['title'],
                company=job['company'],
                url=url,
                score=score,
                summary=summary
            )
        else:
            logging.info(f"❌ Ignored. Score: {score}/10, Agency: {is_agency}")

        # 6. Save State
        db.insert_job(
            job_url=url,
            title=job['title'],
            company=job['company'],
            raw_description=job['description'],
            llm_score=score,
            is_agency=is_agency,
            summary=summary
        )
        
        # 7. Rate Limiting: Polite 3-second delay so Groq doesn't block our free API key
        time.sleep(3)

    logging.info("Pipeline run complete.")

if __name__ == "__main__":
    main()