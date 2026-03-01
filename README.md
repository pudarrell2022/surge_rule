# Surge Rule Set

A lightweight rule-set repository for [Surge](https://nssurge.com/) domain routing.

## Overview

This project maintains custom domain-based rule lists under `ruleset/`.
Each `.list` file contains `DOMAIN-SUFFIX` entries that can be imported into a Surge configuration.

Currently included:

- `homebrew.list`: domains required for Homebrew-related access
- `bybit.list`: domains related to Bybit services

## Directory Structure

```text
.
├── ruleset/
│   ├── homebrew.list
│   └── bybit.list
└── README.md
```

## Rule Format

Each line follows Surge rule-set syntax:

```text
DOMAIN-SUFFIX,example.com
```

No comments or blank lines are required, but both are acceptable if needed.

## Usage

Reference these lists in your Surge profile, for example:

```ini
[Rule]
RULE-SET,https://raw.githubusercontent.com/<your-username>/surge_rule/main/ruleset/homebrew.list,PROXY
RULE-SET,https://raw.githubusercontent.com/<your-username>/surge_rule/main/ruleset/bybit.list,PROXY
FINAL,DIRECT
```

Replace `<your-username>` with your GitHub account and adjust policy names (`PROXY`, `DIRECT`, etc.) to your setup.

## Maintenance

1. Edit or add `.list` files in `ruleset/`.
2. Keep one domain rule per line.
3. Commit and push changes.
4. Update this README when adding new rule files.

## License

Add a license file if you plan to distribute this repository publicly.
