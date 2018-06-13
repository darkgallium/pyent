#!/usr/bin/python3
#-*- coding: utf-8 -*-
import config
import log
import sqlite3

import requests
import os
import json
import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from urllib.parse import urlparse
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

class Notification:

    def __init__(self, changes, typ):
        
        self.changes = changes
        
        if "sm" in config.notification_methods and typ=="results":
            self.send_results_mail()
        
        if "sm" in config.notification_methods and typ=="year_info":
            self.send_year_info_mail()
        
        if "sm" in config.notification_methods and typ=="dept_info":
            self.send_dept_info_mail()

    def get_sm_list(self):

        if config.debug:
            db = config.filestore+"sm_users_testing.db" # TODO: we should not assume by default that this database is present and useable

        else:
            db = config.filestore+"sm_users.db" # TODO: we should not assume by default that this database is present and useable

        c = sqlite3.connect(db)
        d = c.cursor()

        e = d.execute("SELECT email, hash FROM sm_users WHERE state=0")
        f = e.fetchall()
        c.close()
        return f

    def send_results_mail(self):

       a = self.get_sm_list()
       
       for r in a:
            body = ""

            if len(self.changes) == 1: 
                subject = "Nouvelle note disponible sur l'ENT"
                body = "Une nouvelle note de "+self.changes[0].split(',')[0]+" ("+self.changes[0].split(',')[1]+") est disponible sur l'ENT.\r\nConsultez-là ici : "+config.ent_results_url+"\r\n\r\n"
            else:
                subject = "Nouvelles notes disponibles sur l'ENT"
                body = ""
                for c in self.changes:
                    body+="Une nouvelle note de "+c.split(',')[0]+" ("+c.split(',')[1]+") est disponible sur l'ENT.\r\n"
                
                body+="Consultez-les ici : "+config.ent_results_url+"\r\n\r\n"
            
            log.logger.info("Sending an email to "+r[0])
            body+="Pour ne plus recevoir d'alertes par mail : "+config.sm_unsub_url+"?s="+r[1]+"\r\nMessage automatique, ne pas répondre."

            msg = MIMEMultipart()
            msg['From'] = config.sm_mail_from 
            msg['To'] = r[0]
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            server = smtplib.SMTP(config.sm_SMTP_host, config.sm_SMTP_port)
            server.starttls()
            server.login(config.sm_mail_from, config.sm_SMTP_password)
            text = msg.as_string()
            server.sendmail(config.sm_mail_from, r , text)
            server.quit()

    def send_year_info_mail(self):

       a = self.get_sm_list()
       for r in a:
           subject = "Résultats du jury d'année disponibles"
           body = "La délibération du jury d'année vous concernant est dés à présent disponible sur l'ENT.\r\nConsultez-là ici (onglet dossier administratif) : "+config.ent_results_url+"\r\n\r\n"
                
           log.logger.info("Sending an email to "+r[0])
           body+="Pour ne plus recevoir d'alertes par mail : "+config.sm_unsub_url+"?s="+r[1]+"\r\nMessage automatique, ne pas répondre."

           msg = MIMEMultipart()
           msg['From'] = config.sm_mail_from 
           msg['To'] = r[0]
           msg['Subject'] = subject
                
           msg.attach(MIMEText(body, 'plain'))
                
           server = smtplib.SMTP(config.sm_SMTP_host, config.sm_SMTP_port)
           server.starttls()
           server.login(config.sm_mail_from, config.sm_SMTP_password)
           text = msg.as_string()
           server.sendmail(config.sm_mail_from, r , text)
           server.quit()

    def send_dept_info_mail(self):

       a = self.get_sm_list()
       
       for r in a:
           
           subject = "Affectations dans les départements de spécialité"
           body = "Le tableau des affectations en départements de spécialités est désormais disponible sur l'intranet.\r\nConsultez-le ici : "+config.ent_dept_assgt_url+"\r\n\r\n"
                
           log.logger.info("Sending an email to "+r[0])
           body+="Pour ne plus recevoir d'alertes par mail : "+config.sm_unsub_url+"?s="+r[1]+"\r\nMessage automatique, ne pas répondre."

           msg = MIMEMultipart()
           msg['From'] = config.sm_mail_from 
           msg['To'] = r[0]
           msg['Subject'] = subject
                
           msg.attach(MIMEText(body, 'plain'))
                
           server = smtplib.SMTP(config.sm_SMTP_host, config.sm_SMTP_port)
           server.starttls()
           server.login(config.sm_mail_from, config.sm_SMTP_password)
           text = msg.as_string()
           server.sendmail(config.sm_mail_from, r , text)
           server.quit()
