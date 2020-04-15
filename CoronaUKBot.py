import random
import asyncio
import aiohttp
import json
import requests
import pandas as pd
import discord

from discord.ext.commands import Bot

BOT_PREFIX = ("?", "!")
TOKEN = 'NzAwMDc2MTc3MDExOTAwNDM4.Xpdq2w.F0fcZcURcXvQ6cAR7obaEcmoN1g'

header = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

wom_url = 'https://www.worldometers.info/coronavirus/'

client = Bot(command_prefix=BOT_PREFIX)

# @client.command(name='8ball',
# 	description="test description.",
# 	brief="test brief.",
# 	aliases=['eightball', 'eightball2', 'eightball3'],
# 	pass_context=True)
# async def eight_ball(context):
# 	possible_responses = [
# 	'That is a resounding no1',
# 	'That is a resounding no2',
# 	'That is a resounding no3',
# 	'That is a resounding no4',
# 	'That is a resounding no5',
# 	'That is a resounding no6'
# 	]
# 	await client.say(random.choice(possible_responses) + ", " + context.message.author.mention)

# @client.command()
# async def square(number):
# 	squared_value = int(number) * int(number)
# 	await client.say(str(number) + " squared is " + str(squared_value))

@client.command(
		aliases=['uk', 'update', 'data']
)
async def deathcount():
	r = requests.get(wom_url, headers=header)
	df = pd.read_html(r.text)
	df = df[0]  # why?
	df_loc = df[df['Country,Other'].str.match('UK', na=False)]

	embed = discord.Embed(
			colour= discord.Colour.blue()
		)

	total_cases= df_loc['TotalCases'].values[0]
	new_cases= df_loc['NewCases'].values[0]
	total_deaths= df_loc['TotalDeaths'].values[0]
	new_deaths= df_loc['NewDeaths'].values[0]

	embed.set_author(name= 'Corona UK', icon_url= 'https://cdn.discordapp.com/app-icons/700076177011900438/4a19422eb9880e8778723e0823d34416.png')
	embed.set_thumbnail(url= 'https://cdn.discordapp.com/app-icons/700076177011900438/4a19422eb9880e8778723e0823d34416.png')
	embed.add_field(name= 'Total Cases', value=formatWith0DP(total_cases), inline=True)
	embed.add_field(name= 'New Cases', value=str(new_cases), inline=True)
	embed.add_field(name= '_ _', value='_ _', inline=True)
	embed.add_field(name= 'Total Deaths', value=formatWith0DP(total_deaths), inline=True)
	embed.add_field(name= 'New Deaths', value=str(new_deaths), inline=True)
	embed.add_field(name= 'Mortality Rate', value="{:.2f}%".format(total_deaths/total_cases), inline=True)
	embed.set_footer(text= 'Data from Worldometers')

	await client.say(embed=embed)

def formatWith0DP(value):
	return "{:.0f}".format(value)


client.run(TOKEN)
