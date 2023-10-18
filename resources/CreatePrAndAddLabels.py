import requests
import json
import os

API_TOKEN = os.getenv('GITHUB_TOKEN_PSW')
authorization = f'token {API_TOKEN}'

name = os.getenv('NAME')
build_id = os.getenv('BUILD_ID')
branch_name = f"{name}-{build_id}"
print(branch_name)

print(authorization)

headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': authorization,
    'X-GitHub-Api-Version': '2022-11-28',
}

data = {
    "base": "main",
    "body": "Updated deployment specification with a new image version.",
    "head": branch_name,
    "title": "Updated Priyanka learnings Image"
}

response = requests.post('https://api.github.com/repos/sarsatis/helm-charts/pulls', headers=headers, data=json.dumps(data))

pretty_json = json.loads(response.content)
print (json.dumps(pretty_json, indent=2))
print(pretty_json.get("number"))
pr_number = pretty_json.get("number")
# pr_number = 16


label_headers = {
    'Accept': 'application/vnd.github+json',
    'Authorization': authorization,
    'Content-Type': 'application/json',
}

label_data = {
    "labels": [f"appname: {name}","env: sit","releaseName: test","canary"]
}

print('https://api.github.com/repos/sarsatis/helm-charts/issues/{pr_number}/labels')
response = requests.post(f'https://api.github.com/repos/sarsatis/helm-charts/issues/{pr_number}/labels', headers=label_headers, data=json.dumps(label_data))
print(response)