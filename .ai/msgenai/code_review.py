import os
from openai import OpenAI
from github import Github

# Get the GitHub and OpenAI API Keys from environment
github_token = os.getenv('GITHUB_TOKEN')
openai_api_key = os.getenv("OPENAI_API_KEY")

#Initialize the GitHub and OpenAI clients
github = Github(github_token)
client = OpenAI(api_key=openai_api_key)

#Get the repository and PR from the GitHub API
repo = github.get_repo(os.getenv('GITHUB_REPOSITORY'))

pull_request_url = os.getenv('GITHUB_REF')
print("pull_request_url=", pull_request_url);
pull_request_number = pull_request_url.split('/')[-2]
print("pull_request_number=", pull_request_number)
if pull_request_url:
    try:
        pull_request_number = int(pull_request_number)
        print("pull_request_number=", pull_request_number)
        if pull_request_number:
            pr = repo.get_pull(pull_request_number)
            print("pr=", pr)
    except ValueError:
        # Handle invalid URL format or extract manually
        print("inside first else")
        pass
else:
    # Handle case where pull request URL is not available
    print("inside second else")
    pass

# Get the differences in the PR
diff = pr.get_files()

# Reviw each file in the PR
for file in diff:
    if file.filename.endswith('.js'):
        #Get the content of the file
        content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode()

        # use the openai api to review the code
        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{"role": "user", "content": content}],
            stream=True,
            max_tokens=1500,
            n=1,
            stop=None,
            temperature=0.7
        )

         #if there are any issues post a comment on the PR
        for review in stream:
            if review.choices[0].delta.content is not None:
                pr.create_issue_comment(review.choices[0].delta.content)

#TODO: Implement code review using OpenAI API
