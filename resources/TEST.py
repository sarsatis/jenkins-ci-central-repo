from flask import Flask, request, redirect
from github import Github
import os

app = Flask(__name__)

@app.route('/')
def index():
    return "Welcome to my Flask App!"

@app.route('/create_pr_and_add_label', methods=['POST'])
def create_pr_and_add_label():
    try:
        data = request.json
        
        API_TOKEN = os.getenv('GITHUB_TOKEN_PSW')
        app_name = data.get('name')
        image_tag = data.get('version')
        branch_name = f"JIRA-1236-{app_name}"
        application_manifest_repo = "sarsatis/helm-charts"
        git_commit_prefix = "feat"
        file_path = f"manifests/{app_name}/sit/immutable/values.yaml"
        
        github_client = Github(API_TOKEN)
        repo = github_client.get_repo(application_manifest_repo)
        
        # Your logic for updating file content, creating PR, and adding labels goes here...

        pr_url = "https://github.com/your_username/your_repository/pulls/1"  # Replace with the actual PR URL
        
        return redirect(pr_url)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)