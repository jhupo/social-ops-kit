# Style Guide

## Naming

- Python package and module filenames: `snake_case.py`
- Python directories under `src/`: `snake_case`
- Skill directories: `kebab-case`
- Markdown docs: `kebab-case.md`
- Tests: `test_<subject>.py`

## Code style

- Python 3.11+
- 4-space indentation
- max line length: 100
- double quotes in Python source
- explicit type hints for stable-core public functions
- small focused modules over giant script files

## Repository rules

1. Stable public capability names must use `snake_case`.
2. Do not introduce one-off debug or probe filenames into stable source directories.
3. Platform-specific experiments must live outside the stable manifest surface.
4. New files should follow the naming scheme on first commit; avoid later rename churn.
