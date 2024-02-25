#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import json
import logging
import os
import sys

SUBS = 'subs.json'
LOG_FILE = "build_list.log"

log = logging.getLogger(__file__)


def configure_logging(debug=False):
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    file_handler = logging.FileHandler(filename=LOG_FILE)
    handlers = [file_handler, logging.StreamHandler(sys.stdout)]

    logging.basicConfig(level=logging.DEBUG if debug else logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s", datefmt="%d-%b-%y %H:%M:%S", handlers=handlers, )


def parse_args():
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


def load_subs(filename):
    with open(filename, 'r') as f:
        return json.loads(f.read())


def load_new_data(filename):
    try:
        with open(filename, 'r') as f:
            data = []
            lines = f.readlines()
            for l in lines:
                data.append(parse_line(l))
            return data
    except Exception as e:
        log.error(f'Could not load "{filename}": {e}')
        return []


def parse_line(line):
    # assume ' '-separated domain is the first word in the line
    if ' ' in line:
        line = line.split(' ')[0].lstrip()

    # do substitutions
    for orig, sub in load_subs(SUBS).items():
        line = line.replace(orig, sub)

    return line


def parse_target(target_file):
    """
    Parses target file for existing sections and their corresponding entries
    """
    result = {}
    current_section_name = None
    with open(target_file, 'r') as f:
        lines = f.readlines()

    for l in lines:
        l = l.strip()
        if l.startswith('###') and l.endswith('domains start'):
            try:
                current_section_name = l.split(' ')[1]
                result[current_section_name] = {'items': [], 'comments': []}
                continue
            except Exception as e:
                log.error(f'Could not identify section start: {e}')
                continue

        if l.startswith('###') and l.endswith('domains end'):
            current_section_name = None
            continue

        if l.startswith('#') and current_section_name:
            result[current_section_name]['comments'].append(l)
            continue

        if l and current_section_name:
            result[current_section_name]['items'].append(l)

    log.debug(result)
    return result


def write_data(data, target):
    with open(target, 'w') as f:
        for section, section_data in data.items():
            log.debug(f'Writing section "{section}".')
            f.write(f'\n### {section} domains start\n')

            for comment_line in section_data['comments']:
                if not comment_line.endswith('\n'): comment_line += '\n'
                f.write(comment_line)
            f.write('\n')

            for line in section_data['items']:
                if not line.endswith('\n'): line += '\n'
                f.write(line)

            f.write('\n')
            f.write(f'### {section} domains end\n')
            log.debug('Done')
        log.debug('All done')


def main():
    args = parse_args()
    if not args.run or not (args.section and args.filename and args.target):
        log.info('Nothing to do, bye!')
        quit(0)

    if args.target and not os.path.exists(args.target):
        log.info(f'Target file "{args.target}" does not exist and will be created.')
        with open(args.target, 'w') as f:
            print('', file=f)

    data = parse_target(args.target)

    if args.section in data.keys():
        log.info(f'Section "{args.section}" found in "{args.target}" and will be updated.')
        initial_record_count = len(data[args.section]['items'])
        log.debug(f'Initial count of section "{args.section}" is: {initial_record_count}.')

    else:
        log.info(f'Section "{args.section}" was not found in "{args.target}". New section will be created.')
        data[args.section] = {'items': [], 'comments': []}
        initial_record_count = 0

    new_data = load_new_data(args.filename)
    log.debug(f'Loaded {len(new_data)} new records.')

    data[args.section]['items'].extend(new_data)
    data[args.section]['items'] = sorted(
        list(set(data[args.section]['items'])))  # ugly hack to have a sorted list of unique lines
    updated_count = len(data[args.section]['items'])

    log.debug(f'Updated record count is: {updated_count}')
    log.debug(f'Updated data: {data}')
    log.info(
        f'Added {updated_count - initial_record_count} new unique records to the section "{args.section}" in file "{args.target}".')
    log.info(f'Writing data to "{args.target}"...')
    write_data(data, args.target)

    log.info('All done!')


if __name__ == '__main__':
    main()
