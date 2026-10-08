# Pulse — AWS IoMT dashboard

Academic prototype displaying synthetic heart-rate data. Website: GitHub Pages (`main` / `docs`).

## Scope
- AWS API Gateway → Lambda → DynamoDB → dashboard.
- Public `/dev/demo` is read-only and fixed to a reserved synthetic series.
- Existing `/dev/readings` remains IAM authenticated.
- Normal/high scenarios run in the browser and never write to AWS.
- DeepSeek and physical sensors are not connected yet.
- No personal identifiers, API keys or AWS credentials are included.

## Local preview
Run `python -m http.server 8780 --directory docs` and open http://127.0.0.1:8780.

## AWS
`backend/demo.py` exposes only timestamp and heart rate from the reserved synthetic device. `backend/deploy_demo.py` is intended for the existing Learner Lab CloudShell and verifies account, public read, CORS and protected original route. Review identifiers when deploying to another account.

This is a proof of concept, not a clinical system. Public demo readings are synthetic historical samples, not live sensor measurements. Account availability or budget may interrupt the AWS endpoint; local scenarios remain available and explicitly labelled.

References:
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html
