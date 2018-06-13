#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import os
import json

# pyent, a python program that extracts data from uPortal
#                                                                         
# Copyright (C) 2017-2018, darkgallium
#                                                                         
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#                                                                         
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#                                                                         
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.

# This file has been made to be launched automatically with a cron task
# It will automatically check if there is any new result on ENT and will accordingly notify all users

p = os.path.dirname(os.path.realpath(__file__))
with open(p+'/config.json', 'r') as f:
    c = json.load(f)
    locals().update(c) # importing config parameters as local variables, https://stackoverflow.com/a/18647701
