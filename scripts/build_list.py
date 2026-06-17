#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import sys

from typing import Dict, List

SUBS = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'subs.json')
LOG_FILE = 'build_list.log'
ITEMS_KEY = 'items'
COMMENTS_KEY = 'comments'

log = logging.getLogger(__file__)

# Cache for substitutions to avoid repeated file I/O (keyed by filename)
_subs_cache: Dict[str, Dict[str, str]] = {}


def configure_logging(debug: bool = False) -> None:
    """
    Configure logging.
    :param debug: If set to True, use debug logging
    :type debug: bool
    :return:
    :rtype:
    """
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    file_handler = logging.FileHandler(filename=LOG_FILE)
    handlers = [file_handler, logging.StreamHandler(sys.stdout)]

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
                        format='%(asctime)s - %(levelname)s - %(message)s', datefmt='%d-%b-%y %H:%M:%S',
                        handlers=handlers)


def parse_args() -> argparse.Namespace:
    """
    Wrapper for parsing arguments using argparse
    :return: Arguments parsed from the sys.argv
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser()

    parser.add_argument('-s', '--section', action='store', dest='section',
                        help='Section name (eg: "Scam" or "typosquatting").')
    parser.add_argument('-f', '--filename', action='store', dest='filename',
                        help='File with "raw" data. See raw.md for supported formats and substitutions.')
    parser.add_argument('-t', '--target', action='store', dest='target',
                        help='Target filename. If exists, it will be updated with the new content.')

    parser.add_argument('--run', action='store_true', dest='run', default=False,
                        help='Run the script. Otherwise just quit.')
    parser.add_argument('--debug', action='store_true', dest='debug', default=False, help='Debug mode. Writes a lot.')

    args = parser.parse_args()

    configure_logging(args.debug)
    log.debug(args)
    return args


def load_subs(filename: str) -> Dict[str, str]:
    """
    Load substitution map from file (cached).
    :param filename: File with substitutions.
    :type filename: str
    :return: Map of substitutions
    :rtype: Dict[str, str]
    """
    if filename not in _subs_cache:
        try:
            with open(filename, 'r', encoding='utf-8') as f:
                _subs_cache[filename] = json.load(f)
        except FileNotFoundError:
            log.error(f'Substitutions file not found: "{filename}"')
            _subs_cache[filename] = {}
        except json.JSONDecodeError as e:
            log.error(f'Invalid JSON in substitutions file "{filename}": {e}')
            _subs_cache[filename] = {}
        except IOError as e:
            log.error(f'Could not read substitutions file "{filename}": {e}')
            _subs_cache[filename] = {}
    return _subs_cache[filename]


def load_new_data(filename: str) -> List[str]:
    """
    Loads new data from the specified filename.
    :param filename: File to load data from
    :type filename: str
    :return: List of parsed lines.
    :rtype: List[str]
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return [parse_line(line) for line in f if line.strip()]
    except FileNotFoundError:
        log.error(f'File not found: "{filename}"')
        return []
    except IOError as e:
        log.error(f'Could not read "{filename}": {e}')
        return []


def parse_line(line: str) -> str:
    """
    Parses a line to apply the following transformations:
    - Take the part of the line just up until the first space character (assumes space-separated lines format)
    - Apply substitutions as defined in the substitutions file.
    :param line: A line to parse
    :type line: str
    :return: Returns a parsed line
    :rtype: str
    """
    # assume the domain is the first whitespace-separated word in the line
    # split() handles spaces, tabs, and leading/trailing whitespace
    parts = line.split()
    line = parts[0] if parts else ''

    # do substitutions (loaded once and cached)
    subs = load_subs(SUBS)
    for orig, sub in subs.items():
        line = line.replace(orig, sub)

    return line


def parse_target(target_file: str) -> Dict[str, Dict[str, List[str]]]:
    """
    Parses the target file for existing sections and their corresponding entries.
    The returned data will have a section name as the first level key and a dictionary
    with 'items' and 'comments' keys as value. Both 'items' and 'comments' values are
    lists of str.
    :param target_file: Filename of the file to read from
    :type target_file: str
    :return: A map with section names as the key and section data as value
    :rtype: Dict[str, Dict[str, List[str]]]
    """
    result = {}
    current_section_name = None
    try:
        with open(target_file, 'r', encoding='utf-8') as f:
            lines = f.readlines()
    except FileNotFoundError:
        log.error(f'Target file not found: "{target_file}"')
        return {}
    except IOError as e:
        log.error(f'Could not read target file "{target_file}": {e}')
        return {}

    for line in lines:
        line = line.strip()
        if line.startswith('###') and line.endswith('domains start'):
            # section name is everything between the '###' marker and 'domains start'
            section_name = line[len('###'):-len('domains start')].strip()
            if not section_name:
                log.error(f'Could not identify section name in: "{line}"')
                continue
            current_section_name = section_name
            result[current_section_name] = {ITEMS_KEY: [], COMMENTS_KEY: []}
            continue

        if line.startswith('###') and line.endswith('domains end'):
            current_section_name = None
            continue

        if line.startswith('#') and current_section_name:
            result[current_section_name][COMMENTS_KEY].append(line)
            continue

        if line and current_section_name:
            result[current_section_name][ITEMS_KEY].append(line)
            continue
        
        # Warn about content outside of sections
        if line and not current_section_name:
            log.warning(f'Content found outside of any section: "{line[:50]}"')

    log.debug(result)
    return result


def write_data(data: Dict[str, Dict[str, List[str]]], target: str) -> None:
    """
    Write the data structure to the blacklist file.
    :param data: Data to write.
    :type data: Dict[str, Dict[str, List[str]]]
    :param target:
    :type target: str
    :return:
    :rtype: None
    """
    with open(target, 'w', encoding='utf-8') as f:
        for section, section_data in data.items():
            log.debug(f'Writing section "{section}".')
            f.write(f'\n### {section} domains start\n')

            for comment_line in section_data[COMMENTS_KEY]:
                if not comment_line.endswith('\n'):
                    comment_line += '\n'
                f.write(comment_line)
            f.write('\n')

            for line in section_data[ITEMS_KEY]:
                if not line.endswith('\n'):
                    line += '\n'
                f.write(line)

            f.write('\n')
            f.write(f'### {section} domains end\n')
            log.debug('Done')
        log.debug('All done')


def main() -> None:
    args = parse_args()
    if not args.run or not (args.section and args.filename and args.target):
        log.info('Nothing to do, bye!')
        sys.exit(0)

    if args.target and not os.path.exists(args.target):
        log.info(f'Target file "{args.target}" does not exist and will be created.')
        try:
            open(args.target, 'w', encoding='utf-8').close()
        except IOError as e:
            log.error(f'Could not create target file "{args.target}": {e}')
            sys.exit(1)

    data = parse_target(args.target)

    if args.section in data:
        log.info(f'Section "{args.section}" found in "{args.target}" and will be updated.')
        initial_record_count = len(data[args.section][ITEMS_KEY])
        log.debug(f'Initial count of section "{args.section}" is: {initial_record_count}.')

    else:
        log.info(f'Section "{args.section}" was not found in "{args.target}". New section will be created.')
        data[args.section] = {ITEMS_KEY: [], COMMENTS_KEY: []}
        initial_record_count = 0

    # set of entries from update file
    new_entries = set(load_new_data(args.filename))

    # set of entries already present in the list
    all_entries = set(data[args.section][ITEMS_KEY])
    log.debug(f'Loaded {len(new_entries)} new records.')

    # union
    all_entries.update(new_entries)

    # create a sorted list of entries
    all_entries = sorted(all_entries)
    data[args.section][ITEMS_KEY] = all_entries
    updated_count = len(all_entries)

    log.debug(f'Updated record count is: {updated_count}')
    log.debug(f'Updated data: {data}')
    log.info(f'Added {updated_count - initial_record_count} new unique records to the section "{args.section}" in file "{args.target}".')
    log.info(f'Writing data to "{args.target}"...')
    write_data(data, args.target)

    log.info('All done!')


if __name__ == '__main__':
    main()
