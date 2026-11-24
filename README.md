# RepoPilot

A local-first toolkit for repetitive GitHub repository maintenance.

Initial features:
- Suggest issue labels using transparent keyword rules.
- Find potentially duplicate issues using Jaccard token similarity.
- Draft release notes from merged pull request JSON.
- Run a read-only issue suggestion workflow in GitHub Actions.

## Install

Requires Python 3.10+.

```bash
python -m venv .venv
# Windows: .venv\Scripts\activate
# macOS/Linux: source .venv/bin/activate
pip install -e ".[dev]"
```

## Try it

```bash
repopilot suggest-labels --title "App crashes on startup" --body "It raises an exception"
repopilot duplicates --input examples/issues.json --threshold 0.25
repopilot release-notes --input examples/pulls.json
pytest
```

Core analysis runs locally. No issue or pull request content is transmitted to an external service. Label suggestions are advisory: RepoPilot does not modify issues.

## Project status

Early development, version 0.1.0. Interfaces may change before 1.0.

## Roadmap

- [x] Rule-based issue label suggestions
- [x] Local duplicate detection baseline
- [x] Release note drafting
- [x] Tests and CI
- [ ] Read-only GitHub API integration
- [ ] Repository-specific rule configuration
- [ ] HTML maintainer report
- [ ] Optional semantic duplicate detection

See CONTRIBUTING.md. Licensed under MIT.
