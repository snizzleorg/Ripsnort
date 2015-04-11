#!/usr/bin/env python
# -*- coding: utf-8 -*-


import logging
from xml.etree import ElementTree
from xml.dom import minidom

class MediaContent(object):
    def __init__(self):
        self.content_type = ''
        self.production_year = -1
        self.title = ''
        self.durationS = []
        self.scraper_source = ''
        self.scraper_data = None
        self.unique_id = None
        self.photos_urls = []
        self.poster_urls = []
        self.plot_outline = ''
        self.genres = []
        self.public_url = ''
        self.popularity = 0

    def longestDuration(self):
        if len(self.durationS) > 0:
            return max(self.durationS)
        else:
            return 0

    def shortestDuration(self):
        if len(self.durationS) > 0:
            return min(self.durationS)
        else:
            return 0
        
    def hasDurationBetweenMaxMin(self,maxDurationS,minDurationS):
        isMatch = False
        
        durations = self.durationS
        
        if durations is None:
            durations = []
        
        for durationSeconds in durations:
            if durationSeconds >= minDurationS and durationSeconds <= maxDurationS:
                isMatch = True
                break

        return isMatch
    
    def nfo(self):
        rootElem = ElementTree.Element('movie')
        
        idElem = ElementTree.SubElement(rootElem,'id')
        idElem.attrib['moviedb'] = str(self.scraper_source)
        idElem.text = str(self.unique_id)
        
        titleElem = ElementTree.SubElement(rootElem,'title')
        titleElem.text = str(self.title)
        
        yearElem = ElementTree.SubElement(rootElem,'year')
        yearElem.text = str(self.production_year)
        
        outlineElem = ElementTree.SubElement(rootElem,'outline')
        outlineElem.text = str(self.plot_outline)
        
        for genre in self.genres:
            genreElem = ElementTree.SubElement(rootElem,'genre')
            genreElem.text = str(genre)
            
        xmlText = ElementTree.tostring(rootElem)
        
        xmlPretty = minidom.parseString(xmlText).toprettyxml()
        
        return xmlPretty
        

    def __repr__(self):
        retStr = "<MediaContent "
        retStr += "content: " + self.content_type + ", "
        retStr += "year: " + str(self.production_year) + ", "
        retStr += "title: " + str(self.title)
        retStr += ">"
        return retStr

    def __eq__(self,cmp):
        titleMatch = self.title == cmp.title
        yearMatch = self.production_year == cmp.production_year
        return titleMatch and yearMatch
        
    def __ne__(self,cmp):
        return not self.__eq__(cmp)

    def __hash__(self):
        return hash((str(self.scraper_data),self.unique_id))


class MovieMedia(MediaContent):
    def __init__(self):
        super(MovieMedia,self).__init__()
        self.content_type = 'movie'

    def __repr__(self):
        retStr = "<MovieMedia "
        retStr += "year: " + str(self.production_year) + ", "
        retStr += "title: " + self.title.encode('ascii','replace')
        retStr += ">"
        
        return retStr


class TVShowMedia(MediaContent):    
    def __init__(self):
        super(TVShowMedia,self).__init__()
        self.content_type = 'tvshow'
        self.number_of_episodes = 0
        self.number_of_seasons = 0

    def __repr__(self):
        retStr = "<TVShowMedia "
        retStr += "number of episodes: (" + str(self.number_of_episodes) + "), "
        retStr += "number of seasons: (" + str(self.number_of_seasons) + "), "
        retStr += "title: " + self.title.encode('ascii','replace')
        retStr += ">"
        
        return retStr


class TVEpisodeMedia(MediaContent):    
    def __init__(self):
        super(TVEpisodeMedia,self).__init__()
        self.content_type = 'tvepisode'
        self.episode_number = None
        self.episode_title = None
        self.season_number = None

    def __repr__(self):
        retStr = "<TVEpisodeMedia "
        retStr += "episode: (" + str(self.episode_number) + "),"
        retStr += "epi.title: (" + str(self.episode_title) + "),"
        retStr += "season: (" + str(self.season_number) + "),"
        retStr += "year: " + str(self.production_year) + ", "
        retStr += "title: " + self.title.encode('ascii','replace')
        retStr += ">"
        
        return retStr


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)

    movie = MovieMedia()
    tvshow = TVEpisodeMedia()
    tvep = TVEpisodeMedia()
