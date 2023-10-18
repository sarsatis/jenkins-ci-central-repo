echo "Opening a Pull Request"

curl -X 'POST' \
  'https://github.com/sarsatis/gitops-argocd/pulls' \
  -H 'accept: application/json' \
  -H "authorization: $GITHUB_TOKEN" \
  -H 'Content-Type: application/json' \
  -d '{
  "assignee": "sarsatis",
  "assignees": [
    "sarsatis"
  ],
  "base": "main",
  "body": "Updated deployment specification with a new image version.",
  "head": "feature-test",
  "title": "Updated Solar System Image"
}'

echo "Success"