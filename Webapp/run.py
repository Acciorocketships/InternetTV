from flask import Flask, render_template
import mechanize
app = Flask(__name__)

baseurl = "http://www1.watch-series.io/"
priorityhosts = ["vidzi","daclips","gorillavid","thevideo","streamin"] # Specify which hosts you want to display
br = mechanize.Browser()
ua = 'Mozilla/5.0 (X11; Linux x86_64; rv:18.0) Gecko/20100101 Firefox/18.0 (compatible;)'
br.addheaders = [('User-Agent', ua), ('Accept', '*/*')]
br.set_handle_robots(False)



@app.route('/')
def errorpage():
	return render_template('error.html')



@app.route('/<show>/<int:season>/<int:episode>')
def home(show=None,season=1,episode=1):
	url = constructurl(show,season,episode)
	ep = FindVideo(url)
	ep.findextlinks()
	ep.parseextlinks()
	links = ep.prioritylinks
	bestlink = ep.vidlink
	try:
		print(links)
		print("Best Link: ", bestlink)
	links.remove(bestlink)
	links.insert(0,bestlink)
	return render_template('tv.html',show=" ".join(show.capitalize().split("-")),season=str(season),episode=str(episode),links=ep.prioritylinks)



def constructurl(show,season,episode):
		url = baseurl + "/series/" + show.replace(" ","-") + "-season-" + str(season) + "-episode-" + str(episode)
		return url



class FindVideo(object):

	def __init__(self, linkpage):
		self.linkpage = linkpage
		self.extlinks = [] # Links that appear on watchseries.cr
		self.prioritylinks = [] # Actual video links that are printed to the console
		self.vidlink = None # The best videolink

	# Finds all of the external links 
	def findextlinks(self):
		br.open(self.linkpage)
		for link in br.links(text_regex='Watch This Link'):
			if link.url.find(baseurl) > -1:
				self.extlinks.append(link.url)

	# Goes through the external links on the watchseries site and returns the first link that
	# is from a priority host (otherwise just the first link)
	def parseextlinks(self):
		result = None
		for extlink in self.extlinks:
			result = self.getvidlink(extlink)
			if result != None:
				for j, host in enumerate(priorityhosts):
					if result.find(host) > -1:
						if result.find(priorityhosts[0]) > -1:
							self.vidlink = result
						print(result)
						self.prioritylinks.append(result)
		if self.vidlink == None and len(self.prioritylinks) != 0:
			self.vidlink = self.prioritylinks[0]
		elif result == None and len(self.extlinks) != 0:
			br.open(self.extlinks[0])
			self.vidlink = [link for link in br.links(text_regex='Click Here To Play')][0].url

	# Just gets the first video link, ignoring the priority hosts
	def getfirstlink(self):
		if len(self.extlinks) != 0:
			br.open(self.extlinks[0])
			self.vidlink = [link for link in br.links(text_regex='Click Here To Play')][0].url

	# returns the video link, given the external link on the watchseries site
	def getvidlink(self, extlink):
		br.open(extlink)
		return [link for link in br.links(text_regex='Click Here To Play')][0].url




if __name__ == '__main__':
	app.run(host='0.0.0.0', port=8080, debug=False)