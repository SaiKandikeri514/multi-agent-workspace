import os
from jira import JIRA
from dotenv import load_dotenv

load_dotenv()

jira_url = "https://chandra-sai.atlassian.net"
jira_email = os.environ.get("JIRA_EMAIL")
jira_token = os.environ.get("JIRA_API_TOKEN")

jira_client = JIRA(server=jira_url, basic_auth=(jira_email, jira_token))
issue = jira_client.issue('MDP-11')
transitions = jira_client.transitions(issue)
print("AVAILABLE TRANSITIONS FOR MDP-11:")
for t in transitions:
    print(f"ID: {t['id']}, Name: '{t['name']}'")
