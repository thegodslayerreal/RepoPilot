import json

from repopilot.cli import main


def test_analyze_command_writes_json_report(tmp_path, monkeypatch, capsys):
    output = tmp_path / "report.json"
    issue_data = [
        {
            "number": 7,
            "title": "App crashes at startup",
            "body": "Startup exception",
            "labels": [],
            "html_url": "https://github.com/octo/project/issues/7",
            "state": "open",
        }
    ]
    monkeypatch.setattr(
        "sys.argv",
        ["repopilot", "analyze", "octo/project", "--output", str(output)],
    )
    monkeypatch.setattr("repopilot.cli.fetch_open_issues", lambda *args, **kwargs: issue_data)

    main()

    report = json.loads(output.read_text(encoding="utf-8"))
    assert report["repository"] == "octo/project"
    assert report["summary"]["issues_analyzed"] == 1
    assert "Report saved to" in capsys.readouterr().out
