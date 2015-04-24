import string as s, random as r
import urllib
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
    try:
        url = u'http://reddit.com/r/aww.json?sorted=new&after=0'
        data = json.loads(urllib.request.urlopen(url).read().decode("utf8"))['data']['children']

        for d in data:
            pick = d['data']
            if pick['url'].find('i.imgur') == -1:
                img_url = pick['url'].strip('?1')
                img_thumb = pick['thumbnail'].strip('?1')
                imgur_images.append((img_url, img_thumb))
    except:
        pass # if Error 429, do nothing

@register.assignment_tag
def get_image():
    if imgur_images:
        return r.choice(imgur_images)
    else:
        return None

