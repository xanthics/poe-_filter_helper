'''
* Copyright (c) 2016 Jeremy Parks. All rights reserved.
*
* Permission is hereby granted, free of charge, to any person obtaining a
* copy of this software and associated documentation files (the "Software"),
* to deal in the Software without restriction, including without limitation
* the rights to use, copy, modify, merge, publish, distribute, sublicense,
* and/or sell copies of the Software, and to permit persons to whom the
* Software is furnished to do so, subject to the following conditions:
*
* The above copyright notice and this permission notice shall be included in
* all copies or substantial portions of the Software.
*
* THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
* IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
* FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
* AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
* LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
* FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
* DEALINGS IN THE SOFTWARE.

Author: Jeremy Parks
Purpose: Get GGG stashtab data and store in local db
Note: Requires Python 3.5.x
      Database opens a new connection and writes after each page is retrieved as
      TinyDB documentation doesn't indicated when the data is written to disk
'''

import requests
from tinydb import TinyDB, Query
import re


#  Print all leagues in database
def leagues():
	with TinyDB('stashcache.json') as db:
		q = Query()
		#  Print Leagues
		league = []
		while True:
			if league:
				val = db.get(~ q.league.matches('|'.join(league)) & q.league.exists())
			else:
				val = db.get(q.league.exists())
			if not val:
				break
			league.append(val['league'])
		print(league)


# Add current data to the db
def adddata(nextchange, remove, add):
	with TinyDB('stashcache.json') as db:
		q = Query()

		# Update Next ID
		if db.search(q.key.exists()):
			db.update({'next': nextchange}, q.key == 'nextid')
		else:
			db.insert({'key': 'nextid', 'next': nextchange})

		# Remove items that have a stash tab that matches this update
		for i in remove:
			db.remove(q.tabid == i)

		# Insert our new data
		for i in add:
			db.insert(i)


def get_stashes(start=None):
	if not start:
		with TinyDB('stashcache.json') as db:
			q = Query()
			if db.search(q.key.exists()):
				start = db.get(q.key.exists())['next']

	if start:
		url = 'https://www.pathofexile.com/api/public-stash-tabs?id={}'.format(start)
	else:
		url = 'https://www.pathofexile.com/api/public-stash-tabs'

	print("Starting {}".format(url))
	req = requests.get(url)

	data = req.json(encoding='utf-8')

	nextchange = ""
	remove = []
	add = []
	keys = {}
	for i in data:
		if 'stashes' == i:
			for ii in data[i]:
				if 'items' in ii and ii['items']:
					for iii in ii['items']:
						if iii['frameType'] in [3, 6]:
							note = ""
							if 'note' in iii and ('~b/o' in iii['note'] or '~price' in iii['note']):
								note = iii['note']
							elif 'stash' in ii and ('~b/o' in ii['stash'] or '~price' in ii['stash']):
								note = ii['stash']
								keys[ii['stash']] = True
							if note:
								if ii['id'] not in remove:
									remove.append(ii['id'])
								price = re.match(r'(~b/o|~price) (-?\d*(\.\d+)?) (vaal|jew|chrom|alt|jewel|chance|chisel|cartographer|fuse|fusing|alch|scour|blessed|chaos|regret|regal|gcp|gemcutter|divine|exalted|exa|ex|mirror)', note.lower())
								if price:
									if float(price.group(2)) > 0:
										unit = price.group(4)
										if unit in ['exalted', 'exa', 'ex']:
											unit = 'exa'
										elif unit in ['fuse', 'fusing']:
											unit = 'fuse'
										add.append({'type': iii['frameType'], 'league': iii['league'], 'base': iii['typeLine'], 'cost': price.group(2), 'unit': unit, 'tabid': ii['id'], 'ids': iii['id']})
								else:
									with open('erroritems.txt', 'a') as f:
										f.write("{} *** {}\n".format(note, {'type': iii['frameType'], 'league': iii['league'], 'base': iii['typeLine'], 'tabid': ii['id'], 'ids': iii['id']}))
		else:
			nextchange = data[i]

	adddata(nextchange, remove, add)
	return nextchange


if __name__ == "__main__":

	nc = get_stashes()

	oldnc = nc
	while True:
		nc = get_stashes(nc)
		if oldnc == nc:
			break
		oldnc = nc

	leagues()
