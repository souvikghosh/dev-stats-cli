# dev-stats-cli

A CLI tool for developer statistics from GitHub and local git repositories.

## Features

- **GitHub Profile Stats**: View public profile, repository statistics, and language breakdown
- **Local Repo Analysis**: Analyze commit history, contributors, and file types
- **Profile Comparison**: Compare two GitHub profiles side-by-side
- Beautiful terminal output with Rich

## Installation

1. Clone the repository:
```bash
git clone https://github.com/souvikghosh/dev-stats-cli.git
cd dev-stats-cli
```

2. Create and activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install:
```bash
pip install -e ".[dev]"
```

## Usage

### GitHub Statistics

View statistics for a GitHub user:
```bash
devstats github torvalds
```

With authentication (higher rate limits):
```bash
export GITHUB_TOKEN=your_token
devstats github torvalds

# Or pass directly
devstats github torvalds --token your_token
```

Include forked repositories:
```bash
devstats github username --forks
```

### Local Repository Analysis

Analyze current directory:
```bash
devstats local
```

Analyze specific path:
```bash
devstats local /path/to/repo
```

Show more recent commits:
```bash
devstats local --commits 20
```

### Compare Profiles

Compare two GitHub users:
```bash
devstats compare torvalds gvanrossum
```

## Example Output

```
╭─────────────────────────────────────────────────────────────────╮
│                          @torvalds                              │
│  Linus Torvalds                                                 │
│                                                                 │
│  Public Repos: 7  Followers: 200k+  Following: 0               │
╰─────────────────────────────────────────────────────────────────╯

┏━━━━━━━━━━━━━━━━━━━━━┳━━━━━━━━━━━━━━┓
┃ Repository Stats     ┃              ┃
┡━━━━━━━━━━━━━━━━━━━━━╇━━━━━━━━━━━━━━┩
│ Total Repositories  │ 7            │
│ Total Stars         │ 180,000+     │
│ Total Forks         │ 60,000+      │
│ Top Language        │ C            │
└─────────────────────┴──────────────┘

┏━━━━━━━━━━━━┳━━━━━━━┳━━━━━━━━━━━━━━━━━━━━━━┓
┃ Language   ┃ Repos ┃ Bar                  ┃
┡━━━━━━━━━━━━╇━━━━━━━╇━━━━━━━━━━━━━━━━━━━━━━┩
│ C          │ 3     │ ████████████████████ │
│ Shell      │ 2     │ █████████████        │
└────────────┴───────┴──────────────────────┘
```

## Commands

| Command | Description |
|---------|-------------|
| `devstats github <username>` | Show GitHub profile statistics |
| `devstats local [path]` | Analyze local git repository |
| `devstats compare <user1> <user2>` | Compare two GitHub profiles |
| `devstats version` | Show version |
| `devstats --help` | Show help |

## Options

### `github` command
- `--token, -t`: GitHub personal access token
- `--forks, -f`: Include forked repositories

### `local` command
- `--commits, -c`: Number of recent commits to show (default: 10)

### `compare` command
- `--token, -t`: GitHub personal access token

## Running Tests

```bash
# Activate virtual environment
source venv/bin/activate

# Run tests
pytest

# Run with verbose output
pytest -v
```

## Project Structure

```
dev-stats-cli/
├── src/
│   └── dev_stats_cli/
│       ├── __init__.py
│       ├── cli.py          # Typer CLI commands
│       ├── github_api.py   # GitHub API client
│       └── local_git.py    # Local git analysis
├── tests/
│   ├── test_github_api.py
│   └── test_local_git.py
├── pyproject.toml
├── README.md
└── LICENSE
```

## Technologies

- **Typer** - CLI framework
- **Rich** - Terminal formatting
- **GitPython** - Local git operations
- **Requests** - HTTP client

## Rate Limits

GitHub API has rate limits:
- Without authentication: 60 requests/hour
- With token: 5,000 requests/hour

Set `GITHUB_TOKEN` environment variable for higher limits.

## License

MIT
