import mechanize
import sys
import re
import subprocess

baseurl = "http://watchseries.cr/"
priorityhosts = ["vidzi","vodlocker","thevideo","vidbull","daclips"] # Specify which hosts you want to display

br = mechanize.Browser()
ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0 (compatible;)'
br.addheaders = [('User-Agent', ua), ('Accept', '*/*')]
br.set_handle_robots(False)


class FindShow(object):

	def __init__(self):
		self.name = None
		self.season = None
		self.episode = None
		self.url = None

	# Goes through the input arguments and finds the show, season, and episode
	# If it can't find that info, it asks for it
	def parseinput(self):
		total = len(sys.argv)
		if total >= 2:
			nums = re.findall("[-+]?\d+[\.]?\d*?[-+]?\d*", sys.argv[total-1])
			try:
				self.season = int(nums[0])
				self.episode = int(nums[1])
			except:
				pass
			if len(nums) > 0:
				lastword = total-1
			else:
				lastword = total
			if len(sys.argv[1:lastword]) > 0:
				self.name = ""
			for word in sys.argv[1:lastword]:
				self.name += word + " "
			self.name = self.name[:-1]
		if self.name == None:
			self.name = raw_input("Name of Show: ")
		if self.season == None:
			self.season = input("Season: ")
		if self.episode == None:
			self.episode = input("Episode: ")

	# generates the url with all of the episode links
	def constructurl(self):
		self.url = baseurl + "/series/" + self.name.replace(" ","-") + "/season/" + str(self.season) + "/episode/" + str(self.episode)



class FindVideo(object):

	def __init__(self, linkpage):
		self.linkpage = linkpage
		self.extlinks = []
		self.vidlink = None

	# Finds all of the external links 
	def findextlinks(self):
		try:
			br.open(self.linkpage)
		except:
			sys.exit("Show not found")
		for link in br.links(text_regex='Watch This Link'):
			if link.url.find(baseurl) > -1:
				self.extlinks.append(link.url)

	# Goes through the external links on the watchseries site and returns the first link that
	# is from a priority host (otherwise just the first link)
	def parseextlinks(self):
		for extlink in self.extlinks:
			result = self.getvidlink(extlink)[0]
			if result != None:
				for j, host in enumerate(priorityhosts):
					if result.url.find(host) > -1:
						if result.url.find("vidzi") > -1:
							self.vidlink = result.url
						print(result.url)
		if result == None and len(self.extlinks) != 0:
			br.open(self.extlinks[0])
			self.vidlink = [link for link in br.links(text_regex='Click Here To Play')][0].url

	# Just gets the first video link, ignoring the priority hosts
	def getfirstlink(self):
		if len(self.extlinks) != 0:
			br.open(self.extlinks[0])
			self.vidlink = [link for link in br.links(text_regex='Click Here To Play')][0].url
			return

	# returns the video link, given the external link on the watchseries site
	def getvidlink(self, extlink):
		br.open(extlink)
		return [link for link in br.links(text_regex='Click Here To Play')]


show = FindShow()
show.parseinput()
show.constructurl()
print(show.name + ", Season " + str(show.season) + " Episode " + str(show.episode))

episode = FindVideo(show.url)
episode.findextlinks()
episode.parseextlinks()

command = 'open ' + episode.vidlink
subprocess.Popen(command, shell = True) 