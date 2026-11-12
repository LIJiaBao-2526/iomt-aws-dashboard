# Pulse IoMT project

Synthetic heart-rate monitoring with AWS, GitHub Pages, a local HTTP device simulator and retrieval-assisted explanations.

- Website: https://lijiabao-2526.github.io/iomt-aws-dashboard/
- Report: https://lijiabao-2526.github.io/iomt-aws-dashboard/report.html

## Local end-to-end demonstration

Requires Python 3.10+; no pip packages for local mode. From this folder:

```powershell
python backend/server.py
```

In a second terminal:

```powershell
python tools/simulator.py --scenario normal
```

Open http://127.0.0.1:8877. Enable five-second refresh. To stream an elevated scenario:

```powershell
python tools/simulator.py --scenario high --interval 1
```

The pipeline is HTTP simulator → validated SQLite storage → dashboard → rule → source-linked explanation. Browser-only scenarios never write to storage. `start_demo.ps1` launches the server too. Stop with Ctrl+C. SQLite persists synthetic records in the Git-ignored `.local` folder. Only the local computer can open this loopback address; use Pages for other computers.

## Optional DeepSeek integration

Set `DEEPSEEK_API_KEY` in the server's environment before starting it; never paste a key into the website or commit it. The server does not load `.env` files. `DEEPSEEK_MODEL` defaults to `deepseek-flash`; confirm availability in your provider account. In local database mode, the assistant retrieves up to three curated snippets, sends only the question and synthetic statistics to the official HTTPS completion API, and labels actual generated output. Missing key/provider failure returns labelled retrieval results. Public Pages uses retrieval only, with no paid requests.

No real DeepSeek call or physical sensor is claimed as tested. Mock tests verify adapter behavior only. The user selected a synthetic demonstration version without hardware/key.

## Tests

```powershell
python -m unittest discover -s tests -p "test_*.py" -v
node tests/test_logic.cjs
```

Covers finite-value validation, timezone handling, future timestamps, synthetic-only inputs, duplicate conflicts/idempotency, persisted storage, origin restrictions, HTTP round trips, rule boundaries/gaps, retrieval and mocked provider success/failure. See `TEST_RESULTS.txt` for recorded validation. These tests do not establish clinical accuracy.

## AWS

Public endpoint: `https://rl6z5doxlg.execute-api.us-east-1.amazonaws.com/dev/demo`.

`backend/demo.py` reads only the reserved synthetic DynamoDB series. `backend/deploy_demo.py` is the existing guarded Learner Lab deployment; run from its directory in authenticated CloudShell. Existing `/dev/readings` remains IAM protected. Deployment acceptance requires external JSON/CORS verification and anonymous access rejection on the original route. Cloud resources are lab-dependent; a failure is displayed explicitly and does not become fake AWS data. Current verification is recorded in `TEST_RESULTS.txt`.

## References

- https://api-docs.deepseek.com/api/create-chat-completion/
- https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site
- https://docs.aws.amazon.com/apigateway/latest/developerguide/how-to-cors.html
- https://www.nhs.uk/symptoms/heart-palpitations/

On 2026-11-12, authenticated Academy access confirmed that course 170264 had ended. The legacy AWS endpoint returned HTTP 500. A new active Lab is required for cloud restoration. The public page therefore starts in explicitly labelled browser-synthetic mode.

## Verified virtual ESP32 route

Wokwi: https://wokwi.com/projects/480447773460293633

Run the local server, then `python tools/mqtt_bridge.py`. Start the Wokwi project and enable database refresh on the local dashboard. Click the knob and use End for 150 bpm or Home for 50 bpm. The real virtual-board-to-MQTT-to-HTTP-to-SQLite flow was verified, including 75 to 150 bpm and the elevated rule. No physical measurements are claimed. The public Pages site does not read local SQLite.

Windows shortcuts on this computer: Start_Local_Server.cmd, Start_MQTT_Bridge.cmd, Run_Tests.cmd. They use the installed Codex Python runtime, falling back to the Python launcher on other computers. No pip dependencies are needed. See wokwi/README.md for detailed operation. Only one Wokwi simulator instance should run at a time.
