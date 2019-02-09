#!/usr/bin/python3
#-*- coding: utf-8 -*-

import config
import log

import requests, os, json, re, datetime
from bs4 import BeautifulSoup

# pyent, a python program that extracts data from uPortal
#                                                                         
# Copyright (C) 2017-2019, darkgallium
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

class ENT:

    def __init__(self, login, password):
        
        if config.debug:
            log.logger.debug("DEBUG mode is enabled.")

        # Setting login and password as object variables
        self.login = login
        self.password = password

        # Initiating connection
        self.connected = self.connect()

    def connect(self): 
        
        self.session = requests.Session()
        c = self.session.get(config.ent_entrypoint_url)
        soup = BeautifulSoup(c.text, 'html.parser')

        auth_data = {}
        for link in soup.find_all('input'):
            auth_data[link.get('name')] = link.get('value')
        
        auth_data['username'] = self.login
        auth_data['password'] = self.password
        
        form_url = soup.find(id='fm1')['action']
        base_url = config.ent_entrypoint_url.split("/")[0]+"//"+config.ent_entrypoint_url.split("/")[2] 
        c = self.session.post(base_url+form_url, auth_data)
        soup = BeautifulSoup(c.text, 'html.parser')

        if soup.find_all(id='portalNavigationList'):
            log.logger.info("Now connected to "+config.ent_results_url.split("/")[2])
            return True
        else:
            return False
    
    def is_connected(self):
        
        return self.connected

    def get_results_array(self):
        
        if not self.connected: return False
        c = self.session.get(config.ent_results_url)
        
        soup = BeautifulSoup(c.text, 'html.parser')
        table_map = soup.find(id='portlet-DossierAdmEtu-tab2').find_all('tr', attrs={ 'style' : 'border-bottom: 0.1em solid #B6CBD6'} ) # NOTE: this could change if they were to change the theme

        results = {}
        empty_result_regex = re.compile(r" / \d+")

        for elt in table_map:
            elt_name = str(elt.find( 'td', attrs={ 'align' : 'left'} ).string)
            elt_result = str(elt.find( 'td', attrs={ 'align' : 'right'} ).string)
            try: 
                elt_name_sanit = elt_name.split('-', 2)[2].split(':') 
                uc_name = str(elt_name_sanit[0]).strip()
                result_type = str(elt_name_sanit[1]).strip()

            except IndexError as e:
                continue 

            else:
                if empty_result_regex.match(elt_result) is not None: results[uc_name+","+result_type] = ''
                else: results[uc_name+","+result_type] = elt_result
    
        #if config.debug:
            # do debugging stuff
        #    results["Mécanique 4,P1"] = '0 / 20';
        
        
        return results
    
    @staticmethod
    def crawling_available():
        d = datetime.datetime.now()
        
        days = config.crawling_schedule_days.split("-")
        hours = config.crawling_schedule_hours.split("-")

        if config.crawling_enabled:
            if (d.isoweekday() in range(int(days[0]), (int(days[1])+1))):
                if (d.hour in range(int(hours[0]), (int(hours[1])+1))):
                    return True

        return False

    def save_state(self, t):

        f = open(config.filestore+'results.json', 'w+')
        log.logger.debug("Saved results to filestore.")
        json.dump(t, f)

    def crawl(self):

        if not self.connected: return []
        log.logger.info("Checking for new results...")
        curr_results = self.get_results_array()
   
        
        if curr_results == {}:
            log.logger.info("Results page doesn't contain any data.")
            return []

        elif not os.path.isfile(config.filestore+'results.json'):
            self.save_state(curr_results)
            return []

        else:
            prev_results = json.load( open(config.filestore+'results.json', 'r') )

            changes = []
            for elt in prev_results:
                if prev_results[elt] == "" and curr_results[elt] != "":
                    changes.append(elt)
                else:
                    continue

            if changes == []:
                log.logger.info('No changes were made.')

            else:
                log.logger.info("New results are online...")

            if not config.debug:
                self.save_state(curr_results) # When we are in debug mode, we are not saving results by default.        
            
            return changes
