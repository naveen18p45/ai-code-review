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

def load_prompts(file_path):
    with open(file_path, 'r') as file:
        return [line.strip() for line in file.readlines() if line.strip()]

def get_streamed_completion(content):
    prompts = load_prompts('.ai/msgenai/ai/rule1.txt')  # Load prompts from the file
    custom_rule_prompt = "\n".join(prompts)

    # Combine the default review instruction with the custom rules
    prompt = (
        f"Please review the following code for both common coding standards and then the specific Rules below:\n\n"
        f"If a rule is not applicable do not mention it in the comment:\n\n"
        f"And provide all common coding standards that are not implemented with respect to the provided content:\n\n"
        f"Custom Rules:\n{custom_rule_prompt}\n\n"
        f"Code:\n{content}"
    )
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    comment = ""  # Initialize the comment variable
    for chunk in response:
        print("Chunk received:", chunk)  # Debug line
        delta_content = chunk.choices[0].delta.content if chunk.choices and chunk.choices[0].delta else None
        if delta_content:
            print("comment=", delta_content)
            comment += delta_content
        else:
            print("No content in chunk")
    if comment:
        pr.create_issue_comment(comment)
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
