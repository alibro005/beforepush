# BeforePush

[![PyPI version](https://img.shields.io/pypi/v/before-push.svg)](https://pypi.org/project/before-push/)
[![Python 3.13+](https://img.shields.io/badge/Python-3.13%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](https://github.com/alibro005/beforepush/blob/main/LICENSE)
[![Tests](https://github.com/alibro005/beforepush/actions/workflows/test.yml/badge.svg)](https://github.com/alibro005/beforepush/actions/workflows/test.yml)

<p align="center">
  <img src="https://raw.githubusercontent.com/alibro005/beforepush/main/docs/assets/beforepush.svg" alt="BeforePush logo" width="160">
</p>

A lightweight CLI that checks whether your Git branch is ready before pushing or opening a pull request.

## Features

* Check if the current directory is a Git repository
* Show the current branch
* Detect uncommitted or untracked changes
* Check upstream branch configuration
* Check if the current branch is behind a target branch
* Support custom target branches
* Warn about newly staged files larger than 5 MB (configurable)
* Clean terminal output with Rich

## Installation

Install BeforePush from PyPI:

```bash
pip install before-push
```

## Usage

Run BeforePush inside a Git repository:

```bash
beforepush
```

To specify a different target branch:

```bash
beforepush --target develop
```

Set a different maximum size for newly staged files with `--max-file-size`.
Values accept bytes or binary `KB`/`MB` units; the default is `5MB`:

```bash
beforepush --max-file-size 10MB
beforepush --max-file-size 500KB
beforepush --max-file-size 5242880
```

This warns only for newly added files in the Git index. Existing tracked files,
including modified ones, are not flagged solely for being large. Warnings do not
block the command or produce a non-zero exit code.

For detailed installation, usage, and Git pre-push hook instructions, see the [documentation](https://alibro005.github.io/beforepush/).

## Demo

![beforepush](https://raw.githubusercontent.com/alibro005/beforepush/main/docs/assets/demo.gif)

## Contributing

Contributions are welcome! See [CONTRIBUTING.md](CONTRIBUTING.md) for development setup, testing, and contribution guidelines.

## Contributors

Thanks to everyone who contributes to BeforePush!  ❤️

<a href="https://github.com/alibro005/beforepush/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=alibro005/beforepush" />
</a>

## Scope

BeforePush focuses on local Git branch readiness.

It does not create or merge pull requests, authenticate with GitHub, perform code reviews, manage remote repositories, or modify Git history.

## License

This project is licensed under the MIT License.
