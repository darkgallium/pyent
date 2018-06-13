#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import config

import logging
from logging.handlers import RotatingFileHandler

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

logger = logging.getLogger()

if config.debug:
    logger.setLevel(logging.DEBUG)

else:
    logger.setLevel(logging.INFO)
   
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
   
file_log = RotatingFileHandler(config.filestore+"pyent.log", 'a', 10000, 1) # TODO: we should be able to change these two last parameters in config

file_log.setFormatter(formatter)
logger.addHandler(file_log)
