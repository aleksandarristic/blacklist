#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import tempfile
import unittest
from unittest.mock import patch, mock_open, MagicMock
from io import StringIO

# Import the module to test
import build_list


class TestParseLine(unittest.TestCase):
    """Test cases for parse_line function."""

    def setUp(self):
        """Reset the substitutions cache before each test."""
        build_list._subs_cache = {}

    def test_parse_line_simple(self):
        """Test parsing a simple domain without substitutions."""
        with patch('build_list.load_subs', return_value={}):
            result = build_list.parse_line("example.com\n")
            self.assertEqual(result, "example.com")

    def test_parse_line_with_space(self):
        """Test parsing a line with space-separated values."""
        with patch('build_list.load_subs', return_value={}):
            result = build_list.parse_line("example.com 127.0.0.1\n")
            self.assertEqual(result, "example.com")

    def test_parse_line_with_substitution(self):
        """Test parsing with substitutions applied."""
        with patch('build_list.load_subs', return_value={'[.]': '.'}):
            result = build_list.parse_line("example[.]com\n")
            self.assertEqual(result, "example.com")

    def test_parse_line_with_multiple_substitutions(self):
        """Test parsing with multiple substitutions."""
        with patch('build_list.load_subs', return_value={'[.]': '.', 'hxxp': 'http'}):
            result = build_list.parse_line("hxxp://example[.]com")
            self.assertEqual(result, "http://example.com")

    def test_parse_line_strips_whitespace(self):
        """Test that leading/trailing whitespace is stripped."""
        with patch('build_list.load_subs', return_value={}):
            result = build_list.parse_line("example.com  \n")
            self.assertEqual(result, "example.com")

    def test_parse_line_leading_whitespace(self):
        """Leading whitespace must not drop the domain (regression)."""
        with patch('build_list.load_subs', return_value={}):
            result = build_list.parse_line("   example.com\n")
            self.assertEqual(result, "example.com")

    def test_parse_line_tab_separated(self):
        """Tab-separated lines: the domain is the first field."""
        with patch('build_list.load_subs', return_value={}):
            result = build_list.parse_line("example.com\t127.0.0.1\n")
            self.assertEqual(result, "example.com")

    def test_parse_line_empty_string(self):
        """Test parsing an empty string."""
        with patch('build_list.load_subs', return_value={}):
            result = build_list.parse_line("")
            self.assertEqual(result, "")


class TestLoadSubs(unittest.TestCase):
    """Test cases for load_subs function."""

    def setUp(self):
        """Reset the substitutions cache before each test."""
        build_list._subs_cache = {}

    def test_load_subs_valid_json(self):
        """Test loading valid JSON substitutions."""
        test_data = {"[.]": ".", "hxxp": "http"}
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))):
            result = build_list.load_subs('test.json')
            self.assertEqual(result, test_data)

    def test_load_subs_caching(self):
        """Test that substitutions are cached after first load."""
        test_data = {"[.]": "."}
        with patch('builtins.open', mock_open(read_data=json.dumps(test_data))) as mock_file:
            # First call
            result1 = build_list.load_subs('test.json')
            # Second call
            result2 = build_list.load_subs('test.json')
            
            self.assertEqual(result1, result2)
            # File should only be opened once due to caching
            self.assertEqual(mock_file.call_count, 1)

    def test_load_subs_file_not_found(self):
        """Test handling of missing substitutions file."""
        build_list._subs_cache = {}
        with patch('builtins.open', side_effect=FileNotFoundError()):
            with patch('build_list.log') as mock_log:
                result = build_list.load_subs('missing.json')
                self.assertEqual(result, {})
                mock_log.error.assert_called_once()

    def test_load_subs_invalid_json(self):
        """Test handling of invalid JSON."""
        build_list._subs_cache = {}
        with patch('builtins.open', mock_open(read_data='invalid json{')):
            with patch('build_list.log') as mock_log:
                result = build_list.load_subs('bad.json')
                self.assertEqual(result, {})
                mock_log.error.assert_called_once()

    def test_load_subs_io_error(self):
        """Test handling of I/O errors."""
        build_list._subs_cache = {}
        with patch('builtins.open', side_effect=IOError('Disk error')):
            with patch('build_list.log') as mock_log:
                result = build_list.load_subs('error.json')
                self.assertEqual(result, {})
                mock_log.error.assert_called_once()


class TestLoadNewData(unittest.TestCase):
    """Test cases for load_new_data function."""

    def setUp(self):
        """Reset the substitutions cache before each test."""
        build_list._subs_cache = {}

    def test_load_new_data_valid_file(self):
        """Test loading data from a valid file."""
        test_content = "example.com\ntest.org\n"
        with patch('builtins.open', mock_open(read_data=test_content)):
            with patch('build_list.load_subs', return_value={}):
                result = build_list.load_new_data('test.txt')
                self.assertEqual(result, ['example.com', 'test.org'])

    def test_load_new_data_with_empty_lines(self):
        """Test that empty lines are filtered out."""
        test_content = "example.com\n\ntest.org\n\n"
        with patch('builtins.open', mock_open(read_data=test_content)):
            with patch('build_list.load_subs', return_value={}):
                result = build_list.load_new_data('test.txt')
                self.assertEqual(result, ['example.com', 'test.org'])

    def test_load_new_data_file_not_found(self):
        """Test handling of missing file."""
        with patch('builtins.open', side_effect=FileNotFoundError()):
            with patch('build_list.log') as mock_log:
                result = build_list.load_new_data('missing.txt')
                self.assertEqual(result, [])
                mock_log.error.assert_called_once()

    def test_load_new_data_io_error(self):
        """Test handling of I/O errors."""
        with patch('builtins.open', side_effect=IOError('Read error')):
            with patch('build_list.log') as mock_log:
                result = build_list.load_new_data('error.txt')
                self.assertEqual(result, [])
                mock_log.error.assert_called_once()

    def test_load_new_data_with_spaces(self):
        """Test loading data with space-separated values."""
        test_content = "example.com 127.0.0.1\ntest.org 192.168.1.1\n"
        with patch('builtins.open', mock_open(read_data=test_content)):
            with patch('build_list.load_subs', return_value={}):
                result = build_list.load_new_data('test.txt')
                self.assertEqual(result, ['example.com', 'test.org'])


class TestParseTarget(unittest.TestCase):
    """Test cases for parse_target function."""

    def test_parse_target_single_section(self):
        """Test parsing a file with a single section."""
        test_content = """
### Scam domains start
# This is a comment
malicious.com
evil.org
### Scam domains end
"""
        with patch('builtins.open', mock_open(read_data=test_content)):
            result = build_list.parse_target('target.txt')
            self.assertIn('Scam', result)
            self.assertEqual(result['Scam']['items'], ['malicious.com', 'evil.org'])
            self.assertEqual(result['Scam']['comments'], ['# This is a comment'])

    def test_parse_target_multiple_sections(self):
        """Test parsing a file with multiple sections."""
        test_content = """
### Scam domains start
scam1.com
### Scam domains end

### Phishing domains start
phish1.com
### Phishing domains end
"""
        with patch('builtins.open', mock_open(read_data=test_content)):
            result = build_list.parse_target('target.txt')
            self.assertIn('Scam', result)
            self.assertIn('Phishing', result)
            self.assertEqual(result['Scam']['items'], ['scam1.com'])
            self.assertEqual(result['Phishing']['items'], ['phish1.com'])

    def test_parse_target_with_comments(self):
        """Test parsing sections with multiple comments."""
        test_content = """
### Test domains start
# Comment 1
# Comment 2
domain.com
### Test domains end
"""
        with patch('builtins.open', mock_open(read_data=test_content)):
            result = build_list.parse_target('target.txt')
            self.assertEqual(len(result['Test']['comments']), 2)

    def test_parse_target_content_outside_section(self):
        """Test warning for content outside sections."""
        test_content = """
orphan.com
### Test domains start
domain.com
### Test domains end
"""
        with patch('builtins.open', mock_open(read_data=test_content)):
            with patch('build_list.log') as mock_log:
                result = build_list.parse_target('target.txt')
                mock_log.warning.assert_called_once()

    def test_parse_target_malformed_section_start(self):
        """Test handling of malformed section start (no section name)."""
        test_content = """
### domains start
domain.com
### Test domains end
"""
        with patch('builtins.open', mock_open(read_data=test_content)):
            with patch('build_list.log') as mock_log:
                result = build_list.parse_target('target.txt')
                # There is no name between '###' and 'domains start', so the
                # section is rejected with an error and no bogus section created.
                mock_log.error.assert_called()
                self.assertEqual(result, {})

    def test_parse_target_multiword_section_name(self):
        """Test that section names containing spaces are captured in full."""
        test_content = """
### My Section domains start
domain.com
### My Section domains end
"""
        with patch('builtins.open', mock_open(read_data=test_content)):
            result = build_list.parse_target('target.txt')
            self.assertIn('My Section', result)
            self.assertEqual(result['My Section']['items'], ['domain.com'])

    def test_parse_target_empty_file(self):
        """Test parsing an empty file."""
        with patch('builtins.open', mock_open(read_data="")):
            result = build_list.parse_target('empty.txt')
            self.assertEqual(result, {})


class TestWriteData(unittest.TestCase):
    """Test cases for write_data function."""

    def test_write_data_single_section(self):
        """Test writing a single section to file."""
        test_data = {
            'Scam': {
                'items': ['evil.com', 'bad.org'],
                'comments': ['# Known scammers']
            }
        }
        
        m = mock_open()
        with patch('builtins.open', m):
            build_list.write_data(test_data, 'output.txt')
            
        # Get all write calls
        handle = m()
        write_calls = [call[0][0] for call in handle.write.call_args_list]
        
        # Verify structure
        self.assertIn('\n### Scam domains start\n', write_calls)
        self.assertIn('### Scam domains end\n', write_calls)

    def test_write_data_multiple_sections(self):
        """Test writing multiple sections."""
        test_data = {
            'Scam': {'items': ['scam.com'], 'comments': []},
            'Phishing': {'items': ['phish.com'], 'comments': []}
        }
        
        m = mock_open()
        with patch('builtins.open', m):
            build_list.write_data(test_data, 'output.txt')
            
        handle = m()
        write_calls = [call[0][0] for call in handle.write.call_args_list]
        
        # Check both sections are written
        section_starts = [call for call in write_calls if 'domains start' in call]
        self.assertEqual(len(section_starts), 2)

    def test_write_data_adds_newlines(self):
        """Test that newlines are added to lines without them."""
        test_data = {
            'Test': {'items': ['domain.com'], 'comments': ['# comment']}
        }
        
        m = mock_open()
        with patch('builtins.open', m):
            build_list.write_data(test_data, 'output.txt')
            
        handle = m()
        write_calls = [call[0][0] for call in handle.write.call_args_list]
        
        # Check that items have newlines
        self.assertIn('domain.com\n', write_calls)
        self.assertIn('# comment\n', write_calls)

    def test_write_data_encoding_utf8(self):
        """Test that file is opened with UTF-8 encoding."""
        test_data = {'Test': {'items': [], 'comments': []}}
        
        with patch('builtins.open', mock_open()) as m:
            build_list.write_data(test_data, 'output.txt')
            m.assert_called_once_with('output.txt', 'w', encoding='utf-8')


class TestConfigureLogging(unittest.TestCase):
    """Test cases for configure_logging function."""

    @patch('logging.basicConfig')
    @patch('logging.FileHandler')
    @patch('logging.StreamHandler')
    def test_configure_logging_info_level(self, mock_stream, mock_file, mock_basic):
        """Test logging configuration with INFO level."""
        build_list.configure_logging(debug=False)
        mock_basic.assert_called_once()

    @patch('logging.basicConfig')
    @patch('logging.FileHandler')
    @patch('logging.StreamHandler')
    def test_configure_logging_debug_level(self, mock_stream, mock_file, mock_basic):
        """Test logging configuration with DEBUG level."""
        build_list.configure_logging(debug=True)
        mock_basic.assert_called_once()


class TestIntegration(unittest.TestCase):
    """Integration tests using temporary files."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.test_dir = tempfile.mkdtemp()
        build_list._subs_cache = {}

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_full_workflow(self):
        """Test complete workflow from loading to writing."""
        # Create substitutions file
        subs_file = os.path.join(self.test_dir, 'subs.json')
        with open(subs_file, 'w', encoding='utf-8') as f:
            json.dump({'[.]': '.'}, f)

        # Create input file
        input_file = os.path.join(self.test_dir, 'input.txt')
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write('example[.]com\ntest[.]org\n')

        # Create target file
        target_file = os.path.join(self.test_dir, 'target.txt')
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write('''
### Scam domains start
# Existing entries
existing.com
### Scam domains end
''')

        # Patch SUBS constant
        with patch('build_list.SUBS', subs_file):
            # Load new data
            new_data = build_list.load_new_data(input_file)
            self.assertEqual(new_data, ['example.com', 'test.org'])

            # Parse target
            target_data = build_list.parse_target(target_file)
            self.assertIn('Scam', target_data)
            self.assertIn('existing.com', target_data['Scam']['items'])

            # Merge data
            all_entries = set(target_data['Scam']['items'])
            all_entries.update(new_data)
            target_data['Scam']['items'] = sorted(all_entries)

            # Write back
            build_list.write_data(target_data, target_file)

            # Verify result
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('example.com', content)
                self.assertIn('test.org', content)
                self.assertIn('existing.com', content)

    def test_create_new_section(self):
        """Test creating a new section in existing file."""
        target_file = os.path.join(self.test_dir, 'target.txt')
        with open(target_file, 'w', encoding='utf-8') as f:
            f.write('''
### Scam domains start
scam.com
### Scam domains end
''')

        # Parse and add new section
        data = build_list.parse_target(target_file)
        data['NewSection'] = {'items': ['new.com'], 'comments': ['# New section']}

        # Write back
        build_list.write_data(data, target_file)

        # Verify
        result = build_list.parse_target(target_file)
        self.assertIn('NewSection', result)
        self.assertIn('new.com', result['NewSection']['items'])

    def test_empty_substitutions(self):
        """Test workflow with empty substitutions."""
        subs_file = os.path.join(self.test_dir, 'subs.json')
        with open(subs_file, 'w', encoding='utf-8') as f:
            json.dump({}, f)

        input_file = os.path.join(self.test_dir, 'input.txt')
        with open(input_file, 'w', encoding='utf-8') as f:
            f.write('example.com\n')

        with patch('build_list.SUBS', subs_file):
            result = build_list.load_new_data(input_file)
            self.assertEqual(result, ['example.com'])


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions."""

    def setUp(self):
        """Reset the substitutions cache before each test."""
        build_list._subs_cache = {}

    def test_parse_line_with_multiple_spaces(self):
        """Test line with multiple consecutive spaces."""
        with patch('build_list.load_subs', return_value={}):
            result = build_list.parse_line("example.com  extra  data")
            self.assertEqual(result, "example.com")

    def test_parse_line_only_whitespace(self):
        """Test line with only whitespace."""
        with patch('build_list.load_subs', return_value={}):
            result = build_list.parse_line("   \n")
            self.assertEqual(result, "")

    def test_parse_target_consecutive_sections(self):
        """Test parsing sections without empty lines between them."""
        test_content = """### A domains start
a.com
### A domains end
### B domains start
b.com
### B domains end"""
        with patch('builtins.open', mock_open(read_data=test_content)):
            result = build_list.parse_target('target.txt')
            self.assertEqual(len(result), 2)
            self.assertIn('A', result)
            self.assertIn('B', result)

    def test_write_data_empty_sections(self):
        """Test writing sections with no items or comments."""
        test_data = {
            'Empty': {'items': [], 'comments': []}
        }
        
        m = mock_open()
        with patch('builtins.open', m):
            build_list.write_data(test_data, 'output.txt')
            
        handle = m()
        write_calls = [call[0][0] for call in handle.write.call_args_list]
        
        # Should still write section markers
        self.assertIn('\n### Empty domains start\n', write_calls)
        self.assertIn('### Empty domains end\n', write_calls)

    def test_parse_line_special_characters(self):
        """Test parsing lines with special characters."""
        with patch('build_list.load_subs', return_value={}):
            result = build_list.parse_line("example-site.com_test")
            self.assertEqual(result, "example-site.com_test")


if __name__ == '__main__':
    unittest.main()
