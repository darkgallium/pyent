#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from ent import ENT
import config
import log

import discord
from discord.ext import commands
import asyncio
import os, re, json, random, datetime

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

bot = commands.Bot(command_prefix='~')

@bot.event
async def on_ready():
    log.logger.info("Logged in on Discord as "+bot.user.name+" ("+bot.user.id+")")

    #await bot.change_presence(game=discord.Game(name="Algèbre Linéaire"), status=discord.Status.dnd)
    await bot.loop.create_task(check_info())


@bot.command()
async def unset():
    e = discord.Embed()
    ur = ENT.get_unset_results()
    for i,j in ur.items():
        e.add_field(name=i, value=j, inline=False)

    await bot.say("", embed=e)

@bot.command()
async def final_countdown():
    exams_days = json.load( open(config.filestore+"exam_schedule.json", 'r') )
    most_close_date = datetime.datetime(1999, 1, 1)

    for d in exams_days['dates']:
        parsed_date = datetime.datetime.strptime(d, "%Y%m%d%H%M%S")
        
        if parsed_date > most_close_date:
            most_close_date = parsed_date


    countdown = most_close_date - datetime.datetime.now()
    hours, remainder = divmod(countdown.seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    await bot.say("Il vous reste "+str(countdown.days)+" jours, "+str(hours)+" heures, "+str(minutes)+" minutes et "+str(seconds)+" secondes avant le début de la prochaine session de partiels.\r\nRetournez donc à vos révisisons !")


async def check_info():
    
    await bot.wait_until_ready()
    
    while not bot.is_closed:
        d = datetime.datetime.now()
        
        if ENT.crawling_available():
            e = ENT(config.ent_login, config.ent_password)
            changes = e.crawl()
            
            for c in config.ds_bot_notif_channel:
                channel = bot.get_channel(c)           
                
                if len(changes[0])>1:
                    await bot.send_message(channel,'Bonjour!\r\n')
                    for c in changes[0]:
                            d = c.split(",")
                            await bot.send_message(channel,'Une nouvelle note de '+d[0]+' ('+d[1]+') est disponible sur l\'ENT.\r\n')
                    await bot.send_message(channel,'Vous pouvez les consulter au lien suivant : '+config.ent_results_url)
                    
                elif len(changes[0])==1:
                    d = changes[0][0].split(",")
                    await bot.send_message(channel,'Bonjour!\r\nUne nouvelle note de '+d[0]+' ('+d[1]+') est disponible sur l\'ENT.\r\nVous pouvez la consulter au lien suivant : '+config.ent_results_url)
                
                if "year_info" in changes[1]: 
                    await bot.send_message(channel,'Bonjour!\r\nLes délibérations du jury d\'année sont dés à présent disponible sur l\'ENT.\r\nConsultez-les ici (onglet dossier administratif) : '+config.ent_results_url)
                if "dept_info" in changes[1]:
                    await bot.send_message(channel,'Bonjour!\r\nLe tableau des affectations en départements de spécialité est désormais disponible sur l\'intranet.\r\nConsultez-le ici : '+config.ent_dept_assgt_url)

        await asyncio.sleep(config.crawling_interval)


bot.run(config.ds_bot_tkn)
