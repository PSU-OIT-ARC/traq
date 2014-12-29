import string as s, random as r
import urllib2 as request
import json
import time as t

from django import template

register = template.Library()

imgur_images = []

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

	#image_url = p['url'].strip('?1')
	#thumbnail = p['thumbnail'].strip('?1')

	
	for d in data:
		pick = d['data']
		if pick['url'].find('i.imgur') == -1:			
			img_url = pick['url'].strip('?1')
			img_thumb = pick['thumbnail'].strip('?1')
			imgur_images.append((img_url, img_thumb))

	#return image_url, thumbnail

@register.assignment_tag
def get_image():
	return r.choice(imgur_images)

whys = ("... why?",
	"Sad panda :(",
	"Aw, we missed you.",
	"Woo-hoo!")

@register.simple_tag
def why():
	return r.choice(whys)
	