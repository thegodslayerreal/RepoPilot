# Contributing

Thanks for considering a contribution.

- Search existing issues and pull requests first.
- For substantial changes, open an issue to discuss the design.
- Include tests for new behavior and bug fixes.
- Update documentation when commands or output change.
- Keep the core local-first. Do not add telemetry or network calls without explicit maintainer review.
- Never commit tokens, secrets, or private repository data.

Development setup:

```bash
pip install -e ".[dev]"
pytest
ruff check .
```

Good first contributions include edge-case tests, improved label rules, JSON schema validation, and documentation.
