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

# This file has been made to be launched automatically with a cron task
# It will automatically check if there is any new result on ENT and will accordingly notify all users

bot = commands.Bot(command_prefix='~')

@bot.event
async def on_ready():
    log.logger.info("Logged in on Discord as "+bot.user.name+" ("+bot.user.id+")")

    await bot.change_presence(game=discord.Game(name="Algèbre Linéaire"), status=discord.Status.dnd)
    await bot.loop.create_task(check_results())

async def check_results():
    await bot.wait_until_ready()
    
    while not bot.is_closed:
        d = datetime.datetime.now()
        
        if ENT.crawling_available():

            e = ENT(config.ent_login, config.ent_password)
            changes = e.crawl()
            
            for channel_id in config.ds_bot_notif_channels:
                
                channel = bot.get_channel(channel_id)

                if len(changes)>1:
                    await bot.send_message(channel,'@everyone Bonjour!\r\n')
                    for c in changes:
                            d = c.split(",")
                            await bot.send_message(channel,'Une nouvelle note de '+d[0]+' ('+d[1]+') est disponible sur l\'ENT.\r\n')
                    await bot.send_message(channel,'Vous pouvez les consulter au lien suivant : '+config.ent_results_url)
                    
                elif len(changes)==1:
                    d = changes[0].split(",")
                    await bot.send_message(channel,'@everyone Bonjour!\r\nUne nouvelle note de '+d[0]+' ('+d[1]+') est disponible sur l\'ENT.\r\nVous pouvez la consulter au lien suivant : '+config.ent_results_url)

        await asyncio.sleep(config.crawling_interval)


bot.run(config.ds_bot_tkn)
