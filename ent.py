#!/usr/bin/python3
#-*- coding: utf-8 -*-

import config
import notifier
import log

import requests, os, json, re, datetime
from bs4 import BeautifulSoup

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

    def get_assgt_information_array(self):
        if not self.connected: return False
        info = { "year_info": False, "dept_info": False }
            
        # we first check for year assignment
        c = self.session.get(config.ent_results_url)
        soup = BeautifulSoup(c.text, 'html.parser')
        table_map = soup.find(id='portlet-DossierAdmEtu-tab1').find_all('tr', attrs={ 'style' : 'border-bottom: 0.1em solid #B6CBD6'} ) # NOTE: this could change if they were to change the theme

        for elt in table_map:

            elt_name = str(elt.find( 'td', attrs={ 'class' : 'fl-text-navy'} ).string)
            elt_val =str( elt.find( 'td', attrs={ 'style' : 'padding-left: 3em'} ).text)
            
            if "Inscription(s)" in elt_name and "jury" in elt_val:
                info["year_info"] = True
                break
        
        # then we check for department assignment
        
        c = self.session.get(config.ent_dept_assgt_url)
        soup = BeautifulSoup(c.text, 'html.parser')
        t = soup.find(id='msg').find('a')['href']

        c = self.session.get(t)
        soup = BeautifulSoup(c.text, 'html.parser')
        table_map = soup.find(id='c8482').find_all('a', text=re.compile(r"(a|A)ffectations?"))

        if table_map:
            info["dept_info"] = True
        
        return info


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
        #    results["Espagnol 4,CC"] = '0 / 20';
        
        
        return results
    
    @staticmethod
    def get_unset_results():

        results = json.load( open(config.filestore+'results.json', 'r') )
        uset = dict()
        
        for k, r in results.items():
            if r == "":
                i = k.split(",")
                uset[i[0]] = ""

        for k, r in results.items():
            if r == "":
                i = k.split(",")
                uset[i[0]] += i[1] + ", "
            
        uset = {k: v[:-2] for k, v in uset.items()}
        
        return uset

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

    def save_state(self, tu):

        f1 = open(config.filestore+'results.json', 'w+')
        json.dump(tu[0], f1)
            
        f2 = open(config.filestore+'assgt.json', 'w+')
        json.dump(tu[1], f2)

        log.logger.debug("Saved info to filestore.")

    def crawl(self):

        if not self.connected: return False

        log.logger.info("Checking for new information...")
        curr_results = self.get_results_array() 
        curr_assgt = self.get_assgt_information_array()

        r = (curr_results, curr_assgt)

        if not os.path.isfile(config.filestore+'results.json'):
            self.save_state(r)
        elif not os.path.isfile(config.filestore+'assgt.json'):
            self.save_state(r)
        
        else:
            prev_results = json.load( open(config.filestore+'results.json', 'r') )
            
            changes_results = []
            for elt in prev_results:
                if prev_results[elt] == "" and curr_results[elt] != "":
                    changes_results.append(elt)
                else:
                    continue

            if changes_results == []:
                log.logger.info('No changes in results.')

            else:
                log.logger.info("New results are online, notifying...")
                notifier.Notification(changes_results, "results")

            prev_assgt = json.load( open(config.filestore+'assgt.json', 'r') )
            changes_assgt = []
            
            for elt in prev_assgt:
                if prev_assgt[elt] == False and curr_assgt[elt] == True:
                    changes_assgt.append(elt)
                else:
                    continue

            if changes_assgt == []:
                log.logger.info('No changes in assgt.')
                                                                        
            else:

                if "year_info" in changes_assgt:
                    log.logger.info("Year assgt is available, notifying...")
                    notifier.Notification([], "year_info")

                if "dept_info" in changes_assgt:
                    log.logger.info("Dept assgt is available, notifying...")
                    notifier.Notification([], "dept_info")


            if not config.debug:
                self.save_state(r)
            
            return (changes_results, changes_assgt)
