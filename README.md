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
