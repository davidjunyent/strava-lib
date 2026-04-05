# strava-lib

A shared Python library for Strava integration projects. It provides tools for formatting activities, Git operations, and managing configuration.

## Features

- Format Strava activities as markdown
- Create Git commits with custom dates
- Manage environment variables

## Installation

Add to `requirements.txt` or install with pip:

```bash
-e ../strava-lib
# or
pip install -e ../strava-lib
```

## Main Functions

- `load_environment()`
- `format_activity_markdown(activity)`
- `save_activity_file(markdown_content, file_path, repo_path)`
- `create_commit_with_date(repo_path, file_path, activity, git_name, git_email)`

## Environment Variables

Required:
- `ACTIVITIES_REPO_PATH`
- `GIT_EMAIL`
- `GIT_NAME`

Optional:
- `IMPORT_START_DATE` (default: 2012-01-01)
- `IMPORT_BATCH_SIZE` (default: 200)

## Development

```bash
pip install -r requirements-dev.txt
pytest -v
```

## Example

See the **strava-test** project for usage examples.

## License

MIT
