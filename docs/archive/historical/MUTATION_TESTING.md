# Targeted mutation experiment

The optional Cosmic Ray job mutates path-containment and CLI-limit validation, not the full Python CLI.
The runner is pinned to 8.7.0. Ordinary Python and Bashunit checks continue in the main CI workflow.
GitHub Actions creates a fresh SQLite mutation session, a JSONL dump, and a Markdown result report.

Run in a disposable Python 3.13 environment:

    python -m pip install -r requirements-mutation.txt
    python -m unittest discover -s tests -p test_validation.py -v
    cosmic-ray init mutation.toml mutation.sqlite
    cosmic-ray exec mutation.toml mutation.sqlite
    cosmic-ray dump mutation.sqlite > mutation-results.jsonl
    python tools/mutation_report.py mutation-results.jsonl --markdown mutation-summary.md

Survivors do not automatically fail this exploratory job. A timeout or incompetent
result is inconclusive, never credited as a killed mutant. Inspect every survivor
against the unmutated source and add assertions for meaningful missed behavior.

The mutator must not become a runtime dependency of agent-dotfiles.
