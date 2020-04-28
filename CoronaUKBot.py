import random
import asyncio
import aiohttp
import json
import requests
import pandas as pd
import discord
import math
import os

from bs4 import BeautifulSoup
from discord.ext.commands import Bot
from discord import Emoji


# Guard guild id : 225357490655723520
BOT_PREFIX = ("?", "!")

TOKEN = os.getenv('DISCORD_TOKEN_CORONA')
CORONA_THUMBNAIL_URL = 'https://cdn.discordapp.com/app-icons/700076177011900438/4a19422eb9880e8778723e0823d34416.png'

WOM_HEADER = {
    "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.75 Safari/537.36",
    "X-Requested-With": "XMLHttpRequest"
}

WOM_URL = 'https://www.worldometers.info/coronavirus/'

client = Bot(command_prefix=BOT_PREFIX)

def formatWith0DP(value):
	return "{:.0f}".format(value)

def totalDeathByCounty(df, country):
	return df[df['Country,Other'].str.match(country, na=False)].values[0][3]

@client.command(
		name='uk_stats',
		aliases=['uk', 'Uk', 'UK', 'uK'],
		description="Shows the current status of corona in the UK.",
		brief="Corona stats for the UK",
		pass_context=True
)
async def uk_stats(ctx):
	await ctx.send(embed=embedFromCountry('uk', 'uk'))

@client.command(
		name='stats',
		aliases=['c'],
		description="View stats for the named country: !c [country]",
		brief="Corona stats for the named country",
		pass_context=True
)
async def stats(ctx, *args):

	formatted_country=''
	input_country=''

	for word in args:
		word = word.lower()
		formatted_country+=word
		input_country+=word+' '

	input_country.strip()

	if 'korea' in formatted_country:
		formatted_country='s.korea'

	await ctx.send(embed=embedFromCountry(formatted_country, input_country))


def isNaN(string):
    return string != string

def last_updated_value(request):
	soup = BeautifulSoup(request.content, 'html.parser')
	return soup.findAll('div',attrs={"style" : "font-size:13px; color:#999; margin-top:5px; text-align:center"})[0].text

def embedFromCountry(formatted_country, input_country):
	r = requests.get(WOM_URL, headers=WOM_HEADER)
	df = pd.read_html(r.text)
	df = df[0]  # why?
	df_loc = df[df['Country,Other'].str.lower().replace(' ','', regex=True).str.match(formatted_country, na=False)]
	
	if df_loc.size == 0 : 
		embed = discord.Embed(
			colour= discord.Colour.red()
		)

		embed.set_author(name= 'CoronaUK', icon_url= CORONA_THUMBNAIL_URL)
		embed.set_thumbnail(url= CORONA_THUMBNAIL_URL)
		embed.add_field(name= 'Nigga can you spell?', value='_' + input_country +'_' + ' was not found', inline=True)
		return embed
	else :

		embed = discord.Embed(
				colour= discord.Colour.blue()
			)

		total_cases= df_loc['TotalCases'].values[0]
		
		if isNaN(df_loc['NewCases'].values[0]):
			new_cases= '...' 
		else:
			new_cases= df_loc['NewCases'].values[0]
		
		total_deaths= df_loc['TotalDeaths'].values[0]
		
		if isNaN(df_loc['NewDeaths'].values[0]):
			new_deaths= '...'
		else:
			new_deaths= df_loc['NewDeaths'].values[0]

		embed.set_author(name= 'CoronaUK | Stats for ' + df_loc['Country,Other'].values[0], icon_url= CORONA_THUMBNAIL_URL)
		embed.set_thumbnail(url= CORONA_THUMBNAIL_URL)
		embed.add_field(name= 'Total Cases', value=formatWith0DP(total_cases), inline=True)
		embed.add_field(name= 'New Cases', value=str(new_cases), inline=True)
		embed.add_field(name= '_ _', value='_ _', inline=True)
		embed.add_field(name= 'Total Deaths', value=formatWith0DP(total_deaths), inline=True)
		embed.add_field(name= 'New Deaths', value=str(new_deaths), inline=True)
		embed.add_field(name= 'Mortality Rate', value="{:.2f}%".format((total_deaths/total_cases)*100), inline=True)
		embed.set_footer(text= last_updated_value(r) + ' (Worldometers)')

		return embed

@client.command(
		aliases=['v'],
		description="Wager for highest Corona death count by the end of 2020\nCong: Brazil, India, Italy\nOli: Brazil, China, Turkey\nMouse: China, Italy, Spain",
		brief="Victory"
)
async def victory():
	r = requests.get(WOM_URL, headers=WOM_HEADER)
	df = pd.read_html(r.text)
	df = df[0]  # why?
	
	brazil = totalDeathByCounty(df, 'Brazil')
	india = totalDeathByCounty(df, 'India')
	italy = totalDeathByCounty(df, 'Italy')
	china = totalDeathByCounty(df, 'China')
	spain = totalDeathByCounty(df, 'Spain')
	turkey = totalDeathByCounty(df, 'Turkey')

	mouse_total = china + italy + spain
	cong_total = india + italy + brazil
	oli_total = brazil + china + turkey

	my_list = [(cong_total, 'Cong'), (mouse_total, 'Mouse'), (oli_total, 'Oli')]
	my_list.sort(reverse= True)

	embed = discord.Embed(
			colour= discord.Colour.blue()
		)

	embed.set_author(name= 'CoronaUK', icon_url= CORONA_THUMBNAIL_URL)
	embed.set_thumbnail(url= CORONA_THUMBNAIL_URL)
	embed.add_field(name= '1st _ _ _ _ _ _ _ _ _ _ _ _', value= my_list[0][1] + '\n' + formatWith0DP(my_list[0][0]), inline=True)
	embed.add_field(name= '2nd _ _ _ _ _ _ _ _ _ _', value= my_list[1][1] + '\n' + formatWith0DP(my_list[1][0]), inline=True)
	embed.add_field(name= 'Shitter', value= my_list[2][1] + '\n' + formatWith0DP(my_list[2][0]), inline=True)
	embed.set_footer(text= last_updated_value(r) + ' (Worldometers)')

	await client.say(embed=embed)

@client.command(
		name='Emojis',
		aliases=['em', 'emojis'],
		description="Shows all custom emojis on the server using emojis function",
		brief="All custom emojis",
		pass_context=True
)
async def showAll(ctx):
	output = ""
	guild = ctx.message.guild

	for emoji in client.emojis:
		if emoji.guild == guild:
			output += str(emoji)

	print(str(output))
	await ctx.send(output)

@client.command(
		name='pluck',
		aliases=['p'],
		description="Peaches pluck",
		brief="Peaches pluck",
		pass_context=True
)
async def showAll(ctx):
	output = ""
	guild = ctx.message.guild

	pluckList =	random.choices(range(1, 12), weights=(0.59873, 0.10264, 0.08553, 0.0532, 0.05132, 0.06843, 0.01711, 0.01711, 0.0391, 0.0260, 0.0130))
	pluck = pluckList[0]

	emoji_id = 0

	if pluck == 1: #Normal
		emoji_id = 230186896406347776
	elif pluck == 2: #Eyebrow Eyes
		emoji_id = 230187217618862080
	elif pluck == 3: #Line eyes
		emoji_id = 230187066544095232
	elif pluck == 4: #Circle
		emoji_id = 230187161045958656
	elif pluck == 5: #Carrot Eyes
		emoji_id = 230187004938289153
	elif pluck == 6: #Wink
		emoji_id = 230187297839120384
	elif pluck == 7: #Dot eyes
		emoji_id = 230187388469641216
	elif pluck == 8: #Stich Face
		emoji_id = 230187504828022784
	elif pluck == 9:
		emoji_id = 230186708992393216
	elif pluck == 10:
		emoji_id = 230179410219630593
	elif pluck == 11:
		emoji_id = 230186643061997568

	emoji = client.get_emoji(emoji_id)
	await ctx.send(emoji)



client.run(TOKEN)
