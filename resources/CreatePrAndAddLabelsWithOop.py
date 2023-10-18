import os
from github import Github
from github.GithubException import UnknownObjectException, GithubException
import urllib3
from requests.exceptions import ReadTimeout
import socket
import tempfile
import fileinput

class CreatePRAndAddLabel:

    API_TOKEN = os.getenv('GITHUB_TOKEN_PSW')
    app_name = os.getenv('NAME')
    # branch_name = os.getenv('GIT_BRANCH')
    image_tag = os.getenv('VERSION')    

    # API_TOKEN=""
    # app_name="priyankapractice"
    branch_name="JIRA-1236"
    # buildahImageTag="ocp-29"

    authorization = f'token {API_TOKEN}'

    print(f"API TOKEN {API_TOKEN}")

    num_retries = 10
    backoff_factor = 15
    retry_data = urllib3.util.retry.Retry(total=num_retries,read=num_retries,connect=num_retries,backoff_factor=backoff_factor,)

    github_client = Github(API_TOKEN)
    
    application_manifest_repo = "sarsatis/helm-charts"
    git_commit_prefix = "feat"
    file_path = f"manifests/{app_name}/values-sit.yaml"
    file_path1 = f"manifests/priyankapractice/values-sit.yaml"
    errored_messages = []
    repo = ""
    print(branch_name)
    

    def __init__(self):
        print("inside Init")
        self.update_image_tag_and_raise_pr()


    def update_image_tag_and_raise_pr(self):
        repo = self.fetch_repository()

        file_content, pr_created, file_content_decoded = self.check_if_pr_exists_and_fetch_file_content(repo,self.file_path)

        new_file_content = getattr(self, "update_image_tag")(file_content=file_content_decoded, variable_key = "imageTag")
        print(f"print new image value \n {new_file_content}")

        self.check_if_branch_exists(repo)

        self.commit_to_branch(repo, file_content, new_file_content,self.file_path)

        self.create_pr(repo, pr_created)

        # if self.app_name in 'priyankalearnings':
        #     repo = self.fetch_repository()
        #     file_content, pr_created, file_content_decoded = self.check_if_pr_exists_and_fetch_file_content(repo,self.file_path1)
        #     new_file_content = getattr(self, "update_image_tag")(file_content=file_content_decoded, variable_key = "priyankaLearningsImageTag")
        #     print(f"print new image value \n {new_file_content}")
        #     self.check_if_branch_exists(repo)
        #     print(f" commit id {repo.get_branch(self.branch_name).commit}")
        #     print(f" commit sha {repo.get_branch(self.branch_name).commit.sha}")
        #     self.commit_to_branch(repo, file_content, new_file_content,self.file_path1)


    def fetch_repository(self):
        try:
            repo = self.github_client.get_repo(self.application_manifest_repo)
            print("Client Initiation Complete")
        except UnknownObjectException:
            error = f"[SKIPPING] Repo doesn't exist or have no access-{self.application_manifest_repo}"
            self.errored_messages.append(error)
            print(error)
        return repo

    def create_pr(self, repo, pr_created):
        title = f"{self.git_commit_prefix}: {self.branch_name} - Update image tag for application {self.app_name}"
        
        if not pr_created:
            try:
                print(f"Inside PR")
                pr = repo.create_pull(head=self.branch_name,base=repo.default_branch,title=title,body=title)
                print(f"PR Raised")
                self.add_labels(repo, pr)
            except (GithubException, socket.timeout, urllib3.exceptions.ReadTimeoutError, ReadTimeout) as e:
                print(f"PR creation timeout - ({repo.name}) - sleeping 60s")
                print(f"Details: {e}")


    def add_labels(self, repo, pr):
        labels = [self.app_name,"dev"]
        issue = repo.get_issue(number=pr.number)
        issue.set_labels(*labels)
        print(f"Added Labels to PR")


    def commit_to_branch(self, repo, file_content, new_file_content,file_path):
        git_method = "update_file"
        git_method_args = {
            "content":new_file_content,
            "path": file_path,
            "branch":self.branch_name,
            "message":f"{self.git_commit_prefix}: {self.branch_name} - Upadting image tag for application {self.app_name}",
            "sha": file_content.sha
        }
        
        getattr(repo, git_method)(**git_method_args)
        print(f"Updated content to branch")


    def check_if_branch_exists(self, repo):
        branch_list = []
        for branch in list(repo.get_branches()):
            branch_list = branch_list[:len(branch_list)] + [branch.name]
            
        print(f"branch list {branch_list}")

        if self.branch_name not in branch_list:
            try:
                print(f"creating new branch")
                repo_branch = repo.get_branch(repo.default_branch)
                repo.create_git_ref(ref=f'refs/heads/{self.branch_name}', sha=repo_branch.commit.sha)
                print(f"branch created")
            except UnknownObjectException as e:
                if "Not Found" in e.data['message']:
                    err = f"[SKIPPING] {repo.name} - branch unable to be created - most likely due to permissions or empty repo"
                    print(err)
                    self.errored_messages.append(err)


    def check_if_pr_exists_and_fetch_file_content(self, repo, file_path):
        if repo.archived:
            print(f"[SKIPPING] Archived repo - {self.application_manifest_repo}")

        file_content = repo.get_contents(file_path, ref=repo.default_branch)

        pr_created = False

        for pr in repo.get_pulls():
            if self.branch_name == pr.head.ref:
                try:
                    file_content = repo.get_contents(file_path, ref=pr.head.ref)
                    pr_created = True
                except UnknownObjectException:
                    print(f"[INFO] File wasn't found")
                    file_content_decoded = ""

        print(f"file content before decoding \n {file_content}")
        file_content_decoded = file_content.decoded_content.decode("utf-8")
        print(f"print old image value \n {file_content_decoded}")
        return file_content,pr_created,file_content_decoded

            
    @staticmethod
    def update_image_tag(**kwargs):
        content = kwargs['file_content']
        if not content:
            return ""
        
        # read through file and perform replacement
        content_lines = []
        content_lines = content.split("\n")
        i = 0
        while i < len(content_lines):
            print(f"content_lines[i] = {content_lines[i]}")
            if ':' in content_lines[i] and kwargs["variable_key"] in content_lines[i]:
                print(f"Update line content {content_lines[i]}")
                content_lines[i] = f"  {kwargs['variable_key']}: {os.getenv('VERSION')}"
            i +=1
        content = "\n".join(content_lines)
        content = "\n".join(list(content.splitlines()))
        return content


if __name__ == "__main__":
    CreatePRAndAddLabel()