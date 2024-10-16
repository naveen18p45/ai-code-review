import asyncio
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
        if pull_request_number:
            pr = repo.get_pull(pull_request_number)
    except ValueError:
        # Handle invalid URL format or extract manually
        pass
else:
    # Handle case where pull request URL is not available
    pass

# Get the differences in the PR
diff = pr.get_files()

def get_streamed_completion(content):
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": content}],
        stream=True,
    )

    for chunk in response:
        print("Chunk received:", chunk)  # Debug line
        delta_content = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else None
        if delta_content:
            print("comment=", delta_content)
            pr.create_issue_comment(delta_content)
        else:
            print("No content in chunk")
def main(diff):
    for file in diff:
        if file.filename.endswith('.js'):
            # Get the content of the file
            content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode()
            print("content=", content)
            get_streamed_completion(content)

# Run the main function
main(diff)

# Reviw each file in the PR
# for file in diff:
#     if file.filename.endswith('.js'):
#         #Get the content of the file
#         content = repo.get_contents(file.filename, ref=pr.head.sha).decoded_content.decode()
#         print("content=", content)
#         # use the openai api to review the code
#         async def get_streamed_completion(content):
#             async with client.chat.completions.create(
#                 model="gpt-4o-mini",
#                 messages=[{"role": "user", "content": content}],
#                 stream=True,
#             ) as response:
#                 async for chunk in response:
#                     #if there are any issues post a comment on the PR
#                     if chunk.choices[0].delta.content is not None:
#                         print("comment=", chunk.choices[0].delta.content)
#                         pr.create_issue_comment(chunk.choices[0].delta.content)

#         # Run the asynchronous function
#         asyncio.run(get_streamed_completion(content))
                

#TODO: Implement code review using OpenAI API
