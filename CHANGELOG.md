# Changelog

All notable changes to `scitex-logging` are documented here.

The format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/);
versions follow [Semantic Versioning](https://semver.org/).

## [Unreleased]

## [0.1.7]

- fix(workflows): resync integrated release pipeline from scitex-dev v0.11.20
- fix(workflows): standardize to scitex-dev canonical CI set

## [0.1.6]

- fix(tests): clear test-quality violations (PA-306, PA-307)
- docs(branding): two-row shields badge block, author email update
- chore(gitignore): exclude .venv, .coverage, .csh, .dat, build artifacts
- fix(handlers): LazyStderrStreamHandler — resolve sys.stderr per emit

## [0.1.5]

- test(llm): coverage lift (10% → 97-100%, +87 tests)
- refactor(llm): __main__.py split (reverted)
- chore(deps): bump scitex-dev>=0.11.14

## [0.1.4]

- chore(deps): bump scitex-dev pin floor to 0.11.7
- docs(readme): add ## Architecture and ## Demo sections (PS141/PS142)
- fix(release-safety): opt-in publish-pypi.yml (workflow_dispatch only)

## [0.1.3]

- Initial CHANGELOG entry — see git log for prior history.
