import sys
import urllib
import urllib2
import httplib
import re
from BeautifulSoup import BeautifulSoup
from BeautifulSoup import BeautifulStoneSoup


class PopcornTV:
    __USERAGENT = "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:18.0) Gecko/20100101 Firefox/18.0"

    def __init__(self):
        opener = urllib2.build_opener()
        # Use Firefox User-Agent
        opener.addheaders = [('User-Agent', self.__USERAGENT)]
        urllib2.install_opener(opener)

    def getCategories(self):
        pageUrl = "http://home.popcorntv.it/"
        data = urllib2.urlopen(pageUrl).read()
        tree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
        
        links = tree.find("div", "nav1").findAll('a')
        categories = []
        # In queste categorie non ci sono video
        avoid_categories = ["Home", "GenteTV"]
        for link in links:
            category = {}
            category["title"] = link.contents[0].strip()
            if category["title"] in avoid_categories:
                continue
            category["url"] = link["href"]                
            categories.append(category)
       
        return categories

    def getSubCategories(self, pageUrl):
        data = urllib2.urlopen(pageUrl).read()
        htmlTree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)

        subcategories = []
        links = htmlTree.find("div", "nav2").findAll("a")
        for link in links:
            subcategory = {}
            subcategory["url"] = link["href"]
            subcategory["title"] = link.contents[0].strip()
            subcategories.append(subcategory)
       
        return subcategories
        
    def getVideoBySubCategories(self, pageUrl):
        data = urllib2.urlopen(pageUrl).read()
        htmlTree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
    
        tags = htmlTree.find("div", "tags")
        if tags is None:
            videos = self.getVideoByPage(htmlTree)
        else:
            videos = []
            pages = tags.findAll("a")
            for page in pages:
                data = urllib2.urlopen(page["href"]).read()
                htmlTree = BeautifulSoup(data, convertEntities=BeautifulSoup.HTML_ENTITIES)
                videos = videos + self.getVideoByPage(htmlTree)
        return videos
    
    def getVideoByPage(self, htmlTree):
        videos = []
        
        item = htmlTree.find("div", "evidenza-image")
        if item is not None:
            video = {}
            image_tag = item.find("img")
            video["url"] = item.find("a")["href"]
            video["thumb"] = image_tag["src"]
            video["title"] = image_tag["alt"]
            videos.append(video)
        
        items = htmlTree.find("div", "delta-section-content trailers140")
        if items is not None:
            items = items.findAll("div",  "trailers140")

            for item in items:
                video = {}
                image = item.find("div", "trailers-image")
                image_tag = image.find("img")
                video["url"] = image.find("a")["href"]
                video["thumb"] = image_tag["src"]
                video["title"] = image_tag["alt"]
                # don't insert duplicate items
                if video not in videos:
                    videos.append(video)
        
        return videos

    def getSmilUrl(self, pageUrl):
        htmlData = urllib2.urlopen(pageUrl).read()
        
        try:
            match=re.compile('url: escape\("(.+?)"\)').findall(htmlData)
            url = match[0]
        except IndexError:
            match=re.compile('src="/player/ova.asp\?q=(.+?)"').findall(htmlData)
            url = match[0]
            url = url.replace("xxxzzz", "&")

        return url
        
    def getVideoURL(self, smilUrl):
        data = urllib2.urlopen(smilUrl).read()
        htmlTree=BeautifulStoneSoup(data, convertEntities=BeautifulStoneSoup.HTML_ENTITIES)
        
        base = htmlTree.find('meta')['base']
        filepath = htmlTree.find('video')['src']
        url = base + " playpath=" + filepath

        return url

