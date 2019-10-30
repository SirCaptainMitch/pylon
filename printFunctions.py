from aliases import *
from miscFunctions import *

def printAbilities(abilities):#No identifier, print all abilities
	if len(abilities)<8:
		output=''
		for i in abilities:
			output+=i+'\n'
		return output
	else:
		output1=''
		output2=''
		for i in abilities[0:4]:
			output1+=i+'\n'
		for i in abilities[4:]:
			output2+=i+'\n'
		return[output1,output2]

def printTier(talents,tier):#Print a talent tier
	output=''
	for i in talents[tier]:
		output+=i+'\n'
	return output

def printAbility(abilities,hotkey):#Prints abilities with matching hotkey
	output=''
	for ability in abilities:
		if hotkey.upper() in ability[3:5]:
			output+=ability+'\n'
	return output

def printSearch(abilities, talents, name, hero):#Prints abilities and talents with the name of the identifier
	if '--' in name:
		[name,exclude]=name.split('--')
	else:
		exclude='this string is not in any abilities or talents'
	output=''
	for ability in abilities:
		if name in ability.lower() and exclude not in ability.lower():
			output+=ability+'\n'
	levelTiers=[0,1,2,3,4,5,6]
	if hero=='Varian':
		del levelTiers[1]
	else:
		del levelTiers[3]
	for i in levelTiers:
		talentTier=talents[i]
		for talent in talentTier:
			if name in talent.lower() and exclude not in talent.lower():
				output+='***'+str(i*3+1+int(i==6)-2*int(hero=='Chromie' and i!=0))+':*** '+talent+'\n'
	return output

async def printLarge(channel,inputstring):#Get long string. Print lines out in 2000 character chunks
	strings=[i+'\n' for i in inputstring.split('\n')]
	output=strings.pop(0)
	while strings:
		if len(output)+len(strings[0])<2000:
			output+=strings.pop(0)
		else:
			await channel.send(output)
			output=strings.pop(0)
	await channel.send(output)

async def printAll(message,keyword):#When someone calls [all/keyword]
	async with message.channel.typing():
		if len(keyword)<4:
			await channel.send('Please use a keyword with at least 4 letters minimum')
			return
		from heroPage import heroAbilitiesAndTalents
		toPrint=''
		for hero in getHeroes():
			[abilities,talents]=heroAbilitiesAndTalents(hero)
			abilities=extraD(abilities,hero)
			output=printSearch(abilities,talents,keyword,hero)
			if output=='':
				continue
			toPrint+='`'+hero.replace('_',' ')+':` '+output
		if toPrint=='':
			return
		botChannels={'Wind Striders':571531013558239238,'The Hydeout':638160998305497089}
		if toPrint.count('\n')>5 and message.channel.guild.name in botChannels:#If the results is more lines than this, it gets dumped in specified bot channel
			channel=message.channel.guild.get_channel(botChannels[message.channel.guild.name])
			introText=message.author.mention+", Here's all heroes' "+'"'+keyword+'":\n'
			toPrint=introText+toPrint
		else:
			channel=message.channel
	await printLarge(channel,toPrint)