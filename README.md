# flake8-env-patterns

flake8 plugin which validates access to environment variables against allowed patterns

## installation

`pip install flake8-env-patterns`

## flake8 codes

| Code   | Description                                             |
|--------|---------------------------------------------------------|
| FEP001 | environment variable does not match any allowed pattern |

## configuration

This plugin expects a comma-separated list of regex patterns to validate environment variable access
against.
Patterns can be specified via `--env-variable-patterns` or as part of the flake8 configuration:

```ini
[flake8]
env-variable-patterns = AWS_.*,MYAPP_.*
```

## as a pre-commit hook

See [pre-commit](https://github.com/pre-commit/pre-commit) for instructions.
Sample `.pre-commit-config.yaml`:

```yaml
- repo: https://github.com/pycqa/flake8
  rev: 7.0.0
  hooks:
    - id: flake8
      additional_dependencies: [flake8-env-patterns==0.1.0]
```
