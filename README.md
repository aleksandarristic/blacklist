# blacklist

A collection of various blacklists of hosts for use in pihole or similar software.

### Index of lists
* [scam_hosts_srb.txt](/lists/scam_hosts_srb.txt) - Various scam, fraud, phishing, typosquatting websites targeting serbian internet users (collected by members of https://bezbedanbalkan.net/ forum) - currently contains 515 unique exact domains
* [crowdstrike_list.txt](/lists/crowdstrike_list.txt) - List containing Crowdstrike lookalike domains in the aftermath of Crowdstrike Falcon BSOD bug
* [all.txt](/lists/all.txt) - Compiled list of all other lists

### Authors of original list used for `scam_hosts_srb.txt`
* [@milos_rs_](https://twitter.com/milos_rs_ "@milos_rs_ on X")
* [maxxa](https://bezbedanbalkan.net/user-5.html "maxxa on Bezbedanbalkant.net")


--


### Usage examples for `build_list.py`

Tool usage:

```
usage: build_list.py [-h] [-s SECTION] [-f FILENAME] [-t TARGET] [--run] [--debug]

options:
  -h, --help            show this help message and exit
  -s SECTION, --section SECTION
                        Section name (eg: "Scam" or "typosquatting").
  -f FILENAME, --filename FILENAME
                        File with "raw" data. See raw.md for supported formats and substitutions.
  -t TARGET, --target TARGET
                        Target filename. If exists, it will be updated with the new content.
  --run                 Run the script. Otherwise just quit.
  --debug               Debug mode. Writes a lot.
```

The `build_list.py` will parse any textual file with domains in a line-by-line format and into the blacklist compatible output file. The input file needs to meet the following criteria:

* Each line is a new domain.
* Each domain is the first word in the line.

The tool will apply substitutions from `subs.json` to each line it reads from the input file (eg: it will replace `[.]` with `.` - you can add any subs you like). It will not overwrite old content - it's only ever going to add new hosts in the apropriate section. The resulting list of hosts will have unique hosts in sorted order. The tool will also write section headers and a few comment lines underneath. The idea is to run the tool for each new raw source file to populate different sections of the resulting output file. The blacklist from this repo has been built using this tool, so you can see [scam_hosts_srb.txt](/lists/scam_hosts_srb.txt) for example output.

#### Usage examples:

The following example will read `scam.txt` for new hosts, open the `out.txt`, find the existing section named `Scam` and add new hosts.
```
./build_list.py -f scam.txt -s Scam -t out.txt --run
```

# Unit Tests for build_list.py

## Overview

Comprehensive unit tests for the `build_list.py` blacklist management script. The test suite includes 36 tests covering all major functions and edge cases.

## Test Coverage

### Test Classes

1. **TestParseLine** (6 tests)
   - Simple domain parsing
   - Space-separated value handling
   - Substitution application (single and multiple)
   - Whitespace stripping
   - Empty string handling

2. **TestLoadSubs** (6 tests)
   - Valid JSON loading
   - Caching mechanism verification
   - File not found error handling
   - Invalid JSON error handling
   - I/O error handling

3. **TestLoadNewData** (5 tests)
   - Valid file loading
   - Empty line filtering
   - File not found error handling
   - I/O error handling
   - Space-separated value parsing

4. **TestParseTarget** (6 tests)
   - Single section parsing
   - Multiple section parsing
   - Comment handling
   - Content outside sections warning
   - Malformed section handling
   - Empty file handling

5. **TestWriteData** (4 tests)
   - Single section writing
   - Multiple section writing
   - Automatic newline addition
   - UTF-8 encoding verification

6. **TestConfigureLogging** (2 tests)
   - INFO level configuration
   - DEBUG level configuration

7. **TestIntegration** (3 tests)
   - Full workflow (load → parse → merge → write)
   - New section creation
   - Empty substitutions handling

8. **TestEdgeCases** (7 tests)
   - Multiple consecutive spaces
   - Only whitespace lines
   - Consecutive sections without spacing
   - Empty sections
   - Special characters in domains

## Running the Tests

### Run all tests:
```bash
cd ~/<repo location>/blacklist/scripts
python -m unittest test_build_list -v
```

### Run specific test class:
```bash
python -m unittest test_build_list.TestParseLine -v
```

### Run specific test:
```bash
python -m unittest test_build_list.TestParseLine.test_parse_line_simple -v
```

### Run with coverage (if coverage.py is installed):
```bash
pip install coverage
coverage run -m unittest test_build_list
coverage report -m
coverage html  # Generates HTML report in htmlcov/
```

## Test Results

```
----------------------------------------------------------------------
Ran 36 tests in 0.018s

OK
```

## Key Features Tested

✅ **File Operations**
- Reading files with proper encoding (UTF-8)
- Writing files with proper encoding
- Error handling for missing/corrupted files

✅ **Data Parsing**
- Domain extraction from various formats
- String substitutions with caching
- Section-based file structure parsing
- Comment preservation

✅ **Error Handling**
- FileNotFoundError
- IOError
- json.JSONDecodeError
- IndexError/ValueError

✅ **Edge Cases**
- Empty files and sections
- Malformed input
- Content outside sections
- Special characters
- Multiple whitespace scenarios

✅ **Performance**
- Substitution caching to avoid repeated file I/O
- Efficient list comprehensions

## Test Dependencies

- Python 3.6+ (uses f-strings)
- `unittest` (standard library)
- `unittest.mock` (standard library)
- `tempfile` (standard library)

## Continuous Integration

These tests can be integrated into CI/CD pipelines:

```yaml
# Example GitHub Actions workflow
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: '3.9'
      - run: python -m unittest discover -s scripts -p 'test_*.py' -v
```

## Future Improvements

- [ ] Add performance benchmarks
- [ ] Add mutation testing
- [ ] Test main() function with full argument parsing
- [ ] Add property-based tests with hypothesis
- [ ] Test concurrent file access scenarios
