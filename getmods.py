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
Purpose: Get a list of all mods in Content.ggpk
Note: Requires Python 3.5.x
'''

from PyPoE.poe.file.dat import RelationalReader
from PyPoE.poe.file.translations import TranslationFileCache
from PyPoE.poe.file.ggpk import GGPKFile
from PyPoE.poe.sim import mods


def genmodlist():
	path = GGPKFile()
	path.read('C:/Program Files (x86)/Grinding Gear Games/Path of Exile/Content.ggpk')
	path.directory_build()

	# speed things up
	opt = {
		'use_dat_value': False,
		'auto_build_index': True,
	}

	r = RelationalReader(
		path_or_ggpk=path,
		read_options=opt,
	)

	tc = TranslationFileCache(path_or_ggpk=path)

	buff = []
	for i in r['Mods.dat']:
		translation_result = mods.get_translation(i, tc)
		buff.append('{}: {}'.format(i['CorrectGroup'], translation_result.lines))
	with open('mods.txt', 'w') as f:
		f.write("\n".join(sorted(buff)))


if __name__ == "__main__":
	genmodlist()
