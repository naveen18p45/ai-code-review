import os
from github import Github
from openai import api

# Get the GitHub and OpenAI API Keys from environment
github_token = os.getenv('GITHUB_TOKEN')
openai_api_key = os.getenv("OPENAI_API_KEY")

#Initialize the GitHub and OpenAI clients
github = GitHub(github_token)
openai.api_key = openai_api_key

#Get the repository and PR from the GitHub API
repo = github.get_repo(os.getenv('GITHUB_REPOSITORY'))
pr = repo.get_pull(int(os.getenv('GITHUB_REF').split('/')[-1]))

# Get the differences in the PR
diff = pr.get_files()

# Reviw each file in the PR
for file in diff:
    if file.filename.endswith('.js'):
        #Get the content of the file
        content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode()

        # use the openai api to review the code
        review = openai.Completion.create(
            engine="davinci-codex",
            prompt=content,
            max_tokens=60
        )

        #if there are any issues post a comment on the PR
        if review.choices[0].text.strip():
            pr.create_issue_comment({review.choices[0].text})

#TODO: Implement code review using OpenAI API
