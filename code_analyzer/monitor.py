import os
import time
import logging
from dotenv import load_dotenv
from core.utils import parse_git_url
from core.git_provider import GitHubProvider, GitLabProvider
from core.analyzer import Analyzer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("monitor.log"),
        logging.StreamHandler()
    ]
)

def load_config():
    load_dotenv()
    config = {
        "openai_api_key": os.getenv("OPENAI_API_KEY"),
        "openai_base_url": os.getenv("OPENAI_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/"),
        "github_token": os.getenv("GITHUB_TOKEN"),
        "gitlab_token": os.getenv("GITLAB_TOKEN"),
        "repo_url": os.getenv("MONITOR_REPO_URL"),
        "check_interval": int(os.getenv("CHECK_INTERVAL", 600)), # Default 10 minutes
        "llm_model": os.getenv("LLM_MODEL", "gemini-2.5-pro")
    }
    return config

def save_report(report_content, pr_id):
    report_dir = "reports"
    if not os.path.exists(report_dir):
        os.makedirs(report_dir)
    
    filename = f"{report_dir}/report_{pr_id}.md"
    with open(filename, "w", encoding="utf-8") as f:
        f.write(report_content)
    logging.info(f"Report saved to {filename}")

def main():
    config = load_config()
    
    if not config["openai_api_key"]:
        logging.error("OPENAI_API_KEY not found in environment variables.")
        return
    
    if not config["repo_url"]:
        logging.error("MONITOR_REPO_URL not found in environment variables.")
        return

    logging.info(f"Starting monitor for {config['repo_url']} with interval {config['check_interval']}s")

    # Initialize Provider
    # We need to parse the repo URL to determine provider
    # Using the dummy URL trick again as in app.py
    dummy_url = config["repo_url"].rstrip("/") + "/pull/1" if "github" in config["repo_url"] else config["repo_url"].rstrip("/") + "/-/merge_requests/1"
    parsed = parse_git_url(dummy_url)
    
    if not parsed:
        logging.error("Invalid repository URL.")
        return

    if parsed["provider"] == "github":
        provider = GitHubProvider(token=config["github_token"])
    elif parsed["provider"] == "gitlab":
        provider = GitLabProvider(token=config["gitlab_token"])
    
    analyzer = Analyzer(
        api_key=config["openai_api_key"], 
        base_url=config["openai_base_url"],
        model=config["llm_model"]
    )

    while True:
        try:
            logging.info("Checking for open PRs...")
            open_prs = provider.get_open_prs(parsed)
            logging.info(f"Found {len(open_prs)} open PRs.")

            for pr in open_prs:
                pr_id = str(pr['id'])
                report_path = f"reports/report_{pr_id}.md"
                
                if os.path.exists(report_path):
                    logging.info(f"Report for PR #{pr_id} already exists. Skipping.")
                    continue
                
                logging.info(f"Analyzing PR #{pr_id}: {pr['title']}...")
                
                # Fetch Details & Diff
                pr_info = parsed.copy()
                pr_info["pr_id"] = pr_id
                
                details = provider.get_pr_details(pr_info)
                diff = provider.get_diff(pr_info)
                
                # Analyze
                context = analyzer.analyze_context(diff, details)
                dev = analyzer.analyze_for_dev(diff, details, context)
                qa = analyzer.analyze_for_qa(diff, details, context)
                
                # Generate & Save Report
                report = analyzer.generate_report(details, context, dev, qa)
                save_report(report, pr_id)
                
        except Exception as e:
            logging.error(f"Error in monitoring loop: {str(e)}")
        
        logging.info(f"Sleeping for {config['check_interval']} seconds...")
        time.sleep(config["check_interval"])

if __name__ == "__main__":
    main()
