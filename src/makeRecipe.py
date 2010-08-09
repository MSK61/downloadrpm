#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
creates a URL list for RPM packages to be downloaded from the given file

Usage: makeRecipe.py -r REPOFILE -o URLFILE QUEUEFILE
"""

############################################################
#
# Copyright 2010 Mohammed El-Afifi
# This file is part of downloadRPM.
#
# downloadRPM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# downloadRPM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public
# License along with downloadRPM.  If not, see
# <http://www.gnu.org/licenses/>.
#
# program:      RPM package downloader
#
# file:         makeRecipe.py
#
# function:     RPM URL list generator
#
# description:  creates a URL list for RPM pacakges as extracted from
#               the given file
#
# author:       Mohammed Safwat (MS)
#
# environment:  KWrite 4.4.4, python 2.5.2, Fedora release 10 (Cambridge)
#               Kate 3.3.3, python 2.5.2, Fedora release 10 (Cambridge)
#
# notes:        This is a private program.
#
############################################################

from __future__ import with_statement
import logging
from logging import debug, info
import os
import re
import sys
import optparse
# command-line option variables
# variable to receive the output file name
_OUT_OPT_VAR = "out_file_name"
# variable to receive the repository-to-URL conversion file
_REPO_OPT_VAR = "repo_file_name"

def process_command_line(argv):
    """
    Return a 2-tuple: (settings object, args list).
    `argv` is a list of arguments, or `None` for ``sys.argv[1:]``.
    """
    if argv is None:
        argv = sys.argv[1:]

    # initialize the parser object:
    parser = optparse.OptionParser("%prog -r REPOFILE -o URLFILE QUEUEFILE",
        formatter=optparse.TitledHelpFormatter(width=78),
        add_help_option=None)

    # define options here:
    parser.add_option(      # URL output file
        '-o', '--output', dest=_OUT_OPT_VAR,
        help='Save the URL list into this file.')
    parser.add_option(      # repository-to-URL file
        '-r', '--repo-file', dest=_REPO_OPT_VAR,
        help='Use this file to resolve a repository into a base URL.')
    parser.add_option(      # customized description; put --help last
        '-h', '--help', action='help',
        help='Show this help message and exit.')

    settings, args = parser.parse_args(argv)

    # check number of arguments:
    mandatoryArgs = 1
    extraArgs = len(args) - mandatoryArgs

    if extraArgs != 0:
        parser.error('program takes exactly one RPM queue file; ' +
                     (('"%s" ignored' % args[mandatoryArgs:]) if
                     extraArgs > 0 else "none specified") + '.')

    # further process settings
    # missing repository conversion file
    if not getattr(settings, _REPO_OPT_VAR):
        parser.error("Repository conversion file name not specified!")

    return settings, args

def main(argv=None):
    settings, args = process_command_line(argv)
    logging.basicConfig(level=logging.INFO)
    run(args[0], getattr(settings, _REPO_OPT_VAR),
        getattr(settings, _OUT_OPT_VAR))
    return 0        # success


def run(rpm_list_file, repo_file, out_file):
    """Identify the installed packages from the input file.

    `rpm_list_file` is the file containing information about RPM
                    packages.
    `repo_file` is the file containing the mapping between repositories
                and base URL's.
    `out_file` is the output file to dump the results into.
    The function reads in the provided file containing RPM package
    information and generates a file containing the URL list of the RPM
    packages with the aid of the repository-to-URL map file. The results
    are dumped to an output file.

    """
    # Process the repsitory mapping file.
    # Parsing the repository-to-URL mapping file first in memory is
    # better since the map will be typically much smaller in size than
    # the number of packages. The other alternative would be to read the
    # RPM package file, sotring all information of packages in memory
    # but RPM pacakge information would be large in that case.
    info("Reading repository mapping file %s...", repo_file)
    url_sep = '/'
    repo_map = {}
    with open(repo_file) as repo_map_file:
        for line in repo_map_file:

            line = line.splitlines()[0]

            if line:  # Overlook empty lines.

                # Remove end-of-line characters.
                repo_info = line.split()
                repo_urls = repo_info[1:]
                debug("Found for repository %s URL's %s", repo_info[0],
                    repo_urls)
                # Don't drop old repository links(if any) and strip /
                # from URL's.
                repo_map.setdefault(repo_info[0], set()).update(
                    [url.rstrip(url_sep) for url in repo_urls])

            else:
                debug("Empty line encountered!")

    info("Finished reading repository mapping file %s, generating URL list "
        "from RPM list file %s...", repo_file, rpm_list_file)
    # Transform the rpm list file into a URL list.
    link_sep = '\t'
    # URL part separators
    name_ver_sep = '-'
    ver_arch_sep = '.'
    # filter to identify rpm package version correctly
    ver_filter = re.compile("(?:\d+:)?(.+)")
    file_ext = ".rpm"
    wrt_permit = 'w'
    res_file = open(out_file, wrt_permit) if out_file else sys.stdout
    with open(rpm_list_file) as rpm_list:
        for rpm_info in rpm_list:

            rpm_info = rpm_info.splitlines()[0]

            if rpm_info:  # Overlook empty lines.

                # Remove end-of-line characters.
                name, arch, ver, repo = rpm_info.split()
                res_file.write(link_sep.join([url + url_sep + name + name_ver_sep +
                    ver_filter.match(ver).group(1) + ver_arch_sep + arch +
                    file_ext for url in repo_map[repo]]) + os.linesep)

            else:
                debug("Empty line encountered!")

    if out_file:
        res_file.close()

    info("Done!")


if __name__ == '__main__':
    status = main()
    sys.exit(status)
