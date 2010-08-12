#!/usr/bin/env bash
############################################################
#
# Copyright 2010 Mohammed El-Afifi
# This file is part of downloadRPM.
#
# downloadRPM is free software: you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# downloadRPM is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Lesser General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with downloadRPM.  If not, see <http://www.gnu.org/licenses/>.
#
# program:      RPM package downloader
#
# file:         downloadRPM.sh
#
# function:     RPM package downloader
#
# description:  downloads the RPM packages requested in the input file
#
# author:       Mohammed Safwat (MS)
#
# environment:  Kate 3.3.3, python 2.5.2, Fedora release 10 (Cambridge)
#               Emacs 22.3.1, python 2.5.2, Fedora release 10 (Cambridge)
#               VIM 7.2, python 2.5.2, Fedora release 10 (Cambridge)
#
# notes:        This is a private program.
#
############################################################
repoFile=$1
rpmListFile=$2
shift 2
urlListFile=list.txt
"$(dirname "$0")"/makeRecipe.py -r "$repoFile" -o $urlListFile \
    "$rpmListFile" && aria2c -i$urlListFile "$@" && rm $urlListFile
