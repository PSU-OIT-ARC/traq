import string as s, random as r
import urllib2 as request
import json
import time as t

from django import template

register = template.Library()

@register.assignment_tag
def imgurize():
	"""
	Ref: http://codegolf.stackexchange.com/questions/10488/find-random-images-from-http-i-imgur-com

	WARNING: repeated use may cause HTTP Error 429: Too Many Requests.
	Please respect the server and use with caution.
	"""
	# r = 'njj'
	# h = 'erqqvg.pbz/'
	# u = 'uggc://'+h+"e/"+r
	# url = u.decode('rot13')+".json?sorted=new&after=%s" % a 
	url = u'http://reddit.com/r/aww.json?sorted=new&after=0'
	data = json.loads(request.urlopen(url).read())['data']['children']

	l = len(data)
	pick = r.choice(data)
	p = pick['data']
	
	#image_url = p['url'].strip('?1')
	#count = 0
	#while image_url.find('i.imgur') == -1 and count < 5:
	# NOTE: will keep looking for image with url 'i.imgur'
	#	pick = r.choice(data)
	#	count += 1
	#p = pick['data']

	image_url = p['url'].strip('?1')
	thumbnail = p['thumbnail'].strip('?1')

	return image_url, thumbnail

whys = ("... why?",
	"Sad panda :(",
	"We missed you. ... I missed you.",
	"Woohoo!")

@register.simple_tag
def why():
	return r.choice(whys)
	