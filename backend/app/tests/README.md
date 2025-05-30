# Test Backend Document

These instructions should be used for guidance in configuring, creating, and running tests.

## Prerequisites

- PyTest: 8.3.5
- Coverage.py: 7.8.2

## Installation

The prerequisites are installed together with the backend ones with the command:

```bash
pip install -r requirements.txt
```

## Running the Tests

Being in the backend root folder, follow the steps below:

1. Running the tests:

```bash
pytest
```

This command will run the tests and generate a report on standard output.

2. Running the tests with line coverage:

```bash
coverage run -m pytest
```

This will generate information about line coverage and store it in the ".coverage" file.

3. Generating the HTML report of line coverage:

```bash
coverage html
```

This command creates a report in html format, which will be stored in the "htmlcov" folder, which can be accessed through the link displayed in the standard output.
