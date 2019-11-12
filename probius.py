#A HotS Discord bot
#Call in Discord with [hero/modifier]
#Modifier is hotkey or talent tier
#Data is pulled from HotS wiki
#Project started on 14/9-2019

import discord
import asyncio
import io
import aiohttp
import re
import random

from aliases import *			#Spellcheck and alternate names for heroes
from trimBrackets import *		#Trims < from text
from printFunctions import *	#The functions that output the things to print
from heroPage import *			#The function that imports the hero pages
from emojis import *			#Emojis
from miscFunctions import*		#Edge cases and help message
from getDiscordToken import *	#The token is in an untracked file because this is a public Github repo
from builds import *			#Hero builds
from rotation import *			#Weekly rotation
from quotes import *			#Lock-in quotes
from stats import stats

async def mainProbius(client,message,texts):
	loggingMessage=message.channel.guild.name+' '*(15-len(message.channel.guild.name))+message.channel.name+' '+' '*(17-len(message.channel.name))+str(message.author)+' '*(18-len(str(message.author)))+' '+message.content
	print(loggingMessage)
	await client.get_channel(643231901452337192).send('`'+loggingMessage+'`')
	for text in texts:
		hero=text[0]
		buildsAliases=['guide','build','b','g','builds','guides']
		quotesAliases=['quote','q','quotes']
		rotationAlises=['rotation','rot','r']
		aliasesAliases=['aliases','names','acronyms','a','n']
		wikipageAliases=['all','page','wiki']
		randomAliases=['random','ra','rand']
		statsAliases=['stats','scores','leaderboard']
		if hero == 'avatar':
			await client.getAvatar(message.channel,text[1])
			continue
		if hero in statsAliases:
			async with message.channel.typing():
				await stats(message.channel)
				continue
		if hero in randomAliases:
			hero=random.choice(getHeroes())
		if hero in ['help','info']:
			await message.channel.send(helpMessage())
			continue
		if hero in buildsAliases:
			if len(text)==2:
				await guide(aliases(text[1]),message.channel)
			else:
				await message.channel.send("Elitesparkle's builds: <https://elitesparkle.wixsite.com/hots-builds>")
			continue
		if hero in rotationAlises:
			await rotation(message.channel)
			continue
		if hero=='good bot':
			await emoji(['Probius','love'],message.channel)
			continue
		if hero=='bad bot':
			await emoji(['Probius','sad'],message.channel)
			continue
		if ':' in hero:
			await emoji(text,message.channel)
			continue
		if ']' in hero:
			continue
		if hero in ['chogall',"cho'gall",'cg','cho gall','cho-gall']:
			await message.channel.send("Cho and Gall are 2 different heroes. Choose one of them")
			print('Dual hero')
			continue
		if hero in quotesAliases:
			if len(text)==2:
				await message.channel.send(getQuote(aliases(text[1])))
			else:
				await message.channel.send('All hero select quotes: <https://github.com/Asddsa76/Probius/blob/master/quotes.txt>')
			continue
		if hero in aliasesAliases:
			await message.channel.send('All hero alternate names: <https://github.com/Asddsa76/Probius/blob/master/aliases.py>')
			continue
		if hero == 'all':
			await printAll(message,text[1])
			continue
		if hero in ['emoji','emojis','emote','emotes']:
			await message.channel.send('Emojis: [:hero/emotion], where emotion is of the following: happy, lol, sad, silly, meh, angry, cool, oops, love, or wow.')
			continue
		hero=aliases(hero)
		if len(text)==2:#If user switches to hero first, then build/quote
			if text[1] in buildsAliases:
				await guide(hero,message.channel)
				continue
			if text[1] in quotesAliases and text[1]!='q':
				await message.channel.send(getQuote(hero))
				continue

		[abilities,talents]=heroAbilitiesAndTalents(hero)
		abilities=extraD(abilities,hero)
		if abilities==404:
			try:#If no results, then "hero" isn't a hero
				await printAll(message,text[0])
			except:
				pass
			continue
		
		output=''
		try:
			tier=text[1]#If there is no identifier, then it throws exception
			if tier in randomAliases:
				await message.channel.send(printTier(talents,random.randint(0,6)))
				return
		except:
			quote=getQuote(hero)
			output=printAbilities(abilities)
			if len(output)!=2:
				output=quote+output
			else:
				output[0]=quote+output[0]
		if output=='':
			if tier.isdigit():#Talent tier
				tier=int(tier)
				output=printTier(talents,int(tier/3)+int(hero=='Chromie' and tier!=1))#Talents for Chromie come 2 lvls sooner, except lvl 1
			elif tier in ['mount','z']:
				output=abilities[-1]#Last ability. It's heroic if the hero has normal mount, but that's an user error
			elif tier=='extra':
				if hero in ['Zeratul','Gazlowe','Nova','Whitemane']:#Some heroes have the entry for 1 button between D and Q, these have them last
					output=abilities[-1]
				elif hero=='Gall':#Gall has extra and a special mount
					output=abilities[-2]
				elif hero=='Stitches':#Hook is after Q
					output=abilities[2]
				else:
					output=abilities[1]
			elif tier=='r':#Ultimate
				if hero=='Tracer':#She starts with her heroic already unlocked, and only has 1 heroic
					output=abilities[4]
				else:
					output=printTier(talents,3-2*int(hero=='Varian'))#Varian's heroics are at lvl 4
			elif len(tier)==1 and tier in 'dqwe':#Ability (dqwe)
				output=printAbility(abilities,tier)
			elif tier=='trait':
				output=printAbility(abilities,'d')
			elif tier in wikipageAliases:#Linking user to wiki instead of printing everything
				await message.channel.send('<https://heroesofthestorm.gamepedia.com/Data:'+hero+'#Skills>')
				continue
			else:
				tier=abilityAliases(hero,tier)
				output=printSearch(abilities, talents, tier, hero)
		
		if len(output)==2:#If len is 2, then it's an array with output split in half
			if message.channel.name=='rage':
				await message.channel.send(output[0].upper())
				await message.channel.send(output[1].upper())
			else:
				await message.channel.send(output[0])
				await message.channel.send(output[1])
		else:
			if message.channel.name=='rage':
				output=output.upper()
			try:
				await message.channel.send(output)
			except:
				if output=='':
					try:#If no results, it's probably an emoji with : forgotten. Prefer to call with : to avoid loading abilities and talents page
						await emoji([hero,tier],message.channel)
						continue
					except:
						pass
					if message.channel.name=='rage':
						await message.channel.send('ERROR: '+hero.upper()+' DOES NOT HAVE "'+tier.upper()+'".')
					else:
						await message.channel.send('Error: '+hero+' does not have "'+tier+'".')
					print('No results')
				else:
					if message.channel.name=='rage':
						await message.channel.send("ERROR: EXCEEDED DISCORD'S 2000 CHARACTER LIMIT. BE MORE SPECIFIC")
					else:
						await message.channel.send("Error: exceeded Discord's 2000 character limit. Be more specific")
					print('2000 limit')

async def welcome(member):
	guild=member.guild
	if guild.name=='Wind Striders':
		print(member.name+' joined')
		channel=guild.get_channel(557366982471581718)#general
		rulesChannel=guild.get_channel(634012658625937408)#server-rules
		await channel.send('Welcome '+member.mention+'! Please read '+rulesChannel.mention+' and ping **Olympian(mod)** with the **bolded** info at top **(`Region`, `Rank`, and `Preferred Colour`)** to get sorted <:peepoLove:606862963478888449>')
		await member.add_roles(guild.get_role(560435022427848705))#UNSORTED role

def findTexts(message):
	text=message.content.lower()
	leftBrackets=[1+m.start() for m in re.finditer('\[',text)]#Must escape brackets when using regex
	rightBrackets=[m.start() for m in re.finditer('\]',text)]
	texts=[text[leftBrackets[i]:rightBrackets[i]].split('/') for i in range(len(leftBrackets))]
	return texts

async def fetch(session, url):
	async with session.get(url) as response:
		return await response.text()

async def getPostInfo(post):
	title=post.split('", "')[0]
	post=post.split('"author": "')[1]
	author=post.split('"')[0]
	post=post.split('"permalink": "')[1]
	shortUrl=post.split('"')[0]
	url='https://old.reddit.com'+shortUrl
	return [title,author,url]

class MyClient(discord.Client):
	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.seenTitles=[]
		# create the background task and run it in the background
		self.bgTask0 = self.loop.create_task(self.bgTaskSubredditForwarding())
		self.bgTask1 = self.loop.create_task(self.bgTaskUNSORTED())

	async def fillPreviousPostTitles(self):
		await self.wait_until_ready()
		async with aiohttp.ClientSession() as session:
			page = await fetch(session, 'https://old.reddit.com/r/heroesofthestorm/new.api')
			posts=page.split('"clicked": false, "title": "')[1:]
			output=[]
			for post in posts:
				[title,author,url] = await getPostInfo(post)#Newest post that has been checked
				output.append(title)
			return output

	async def on_ready(self):
		self.seenTitles=await self.fillPreviousPostTitles()		#Fills seenTitles with all current titles
		print('Logged on as', self.user)

	async def on_message(self, message):
		#Don't respond to ourselves
		if message.author == self.user:
			return
		ignoredUsers=['Rick Astley','PogChamp',"Swann's Helper"]
		if message.author.name in ignoredUsers:
			return
		if '[' in message.content and ']' in message.content:
			texts=findTexts(message)
			await mainProbius(self,message,texts)
		
	async def on_message_edit(self,before, after):
		if '[' in after.content and ']' in after.content:
			try:
				beforeTexts=findTexts(before)
			except:
				beforeTexts=[]
			newTexts=[i for i in findTexts(after) if i not in beforeTexts]
			if newTexts:#Nonempty lists have boolean value true
				await mainProbius(self,after,newTexts)

	async def on_raw_reaction_add(self,payload):
		if client.get_user(payload.user_id).name=='Asddsa76':
			await (await (client.get_channel(payload.channel_id)).fetch_message(payload.message_id)).add_reaction(payload.emoji)

	async def on_member_join(self,member):
		await welcome(member)

	async def getAvatar(self,channel,userMention):
		userString=userMention[2:-1].replace('!','')
		user=self.get_user(int(userString))
		await channel.send(user.avatar_url)

	async def bgTaskSubredditForwarding(self):
		await self.wait_until_ready()
		#channel = self.get_channel(557366982471581718)#WS general
		channel = self.get_channel(604394753722941451)#PT general-2
		while not self.is_closed():
			async with aiohttp.ClientSession() as session:
				page = await fetch(session, 'https://old.reddit.com/r/heroesofthestorm/new.api')#Screw JSON parsing, I'll do it myself
				posts=page.split('"clicked": false, "title": "')[1:]
				print(self.seenTitles)
				for post in posts:
					[title,author,url] = await getPostInfo(post)
					print(title)
					if author in ['Asddsa76', 'Blackstar_9', 'Spazzo965', 'SomeoneNew666', 'joshguillen', 'SotheBee', 'AnemoneMeer', 'jdelrioc', 'Pscythic', 'Elitesparkle', 'slapperoni', 'secret3332', 'Carrygan_', 'Archlichofthestorm', 'Gnueless', 'ThatDoomedStudent', 'InfiniteEarth', 'SamiSha_', 'twinklesunnysun', 'zanehyde', 'Pelaberus', 'KillMeWithMemes', 'ridleyfire','bran76765']:
						if title not in self.seenTitles:#This post hasn't been processed before
							self.seenTitles.append(title)

							title=title.replace('&amp;','&')
							await channel.send('**'+title+'** by '+author+': '+url)
							await self.get_channel(643231901452337192).send('`'+title+' by '+author+'`')
							print(title+' by '+author)
			await asyncio.sleep(60)#Check for new posts every minute

	async def bgTaskUNSORTED(self):
		await self.wait_until_ready()
		channel = self.get_channel(557366982471581718)#WSgeneral
		role=channel.guild.get_role(560435022427848705)#UNSORTED
		rulesChannel=channel.guild.get_channel(634012658625937408)#server-rules
		while not self.is_closed():
			await asyncio.sleep(60*60*24)#Sleep 24 hours
			await channel.send('Note to all '+role.mention+': Please read '+rulesChannel.mention+' and ping **Olympian(mod)** with the **bolded** info at top **(`Region`, `Rank`, and `Preferred Colour`)** to get sorted before Blackstorm purges you <:peepoLove:606862963478888449>')

client = MyClient()
client.run(getDiscordToken())