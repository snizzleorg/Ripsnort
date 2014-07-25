#!/usr/bin/env python
# -*- coding: utf-8 -*-


import os
import sys
import shutil
import logging


import disc_drive


dirname = os.path.dirname(os.path.realpath( __file__ ))

sys.path.append( os.path.join(dirname,"ripper") )
import ripper

sys.path.append( os.path.join(dirname,"dependancies") )
import config_to_dict
import dvdfingerprint

sys.path.append( os.path.join(dirname,"notification" ) )
import notification

sys.path.append( os.path.join(dirname,"scraper" ) )
import scraper



def contentTypeForTracksAndName(tracks,name,config):
    if len(name) == 0:
        return None

    contentType = None
    
    hasSeasonInName = 'season' in name.lower()
    hasSeriesInName = 'series' in name.lower()
    hasDiscInName = 'disc' in name.lower()
    hasDiskInName = 'disk' in name.lower()
    
    if ( hasSeasonInName or hasSeriesInName ) and ( hasDiscInName or hasDiskInName ):
        #nameIndicatesTVShow
        contentType = 'tvshow'
    else:
        #check the track lengths
        minDurationMovie = int(config['ripper']['movie_min_length_seconds'])
        maxDurationMovie = int(config['ripper']['movie_max_length_seconds'])

        minDurationTV = int(config['ripper']['tvepisode_min_length_seconds'])
        maxDurationTV = int(config['ripper']['tvepisode_max_length_seconds'])
        
        tracksMovies = tracksUnderDuration(maxDurationMovie, tracksOverDuration(minDurationMovie,tracks))

        tracksTV = tracksUnderDuration(maxDurationTV, tracksOverDuration(minDurationTV,tracks))
        
        if len(tracksTV) > 0 and len(tracksMovies) == 0:
            contentType = 'tvshow'
        elif len(tracksMovies) > 0 and len(tracksTV) == 0:
            contentType = 'movie'
        else:
            #we have both movie and video candidates
            
            #check the durations of the tv tracks, if they are similar in length, then we can assume they are episodes
            
            durations = []
            durationTotalS = 0
            
            for track in tracksTV:
                durations.append( track.durationS )
                durationTotalS += track.durationS
            
            durationAverage = durationTotalS / len(durations)
            
            durationsAreCloseToAverage = True
            
            for track in tracksTV:
                if abs(track.durationTotalS / durationAverage) < 0.9 or abs(track.durationTotalS / durationAverage) > 1.1:
                    durationsAreCloseToAverage = False
                    break
                    
            if durationsAreCloseToAverage:
                contentType = 'tvshow'
            else:
                #durations don't all match, assume its a movie
                contentType = 'movie'
    
    logging.debug('Content type for name:' + name + ', tracks:' + str(tracks) + ' = ' + contentType)
    
    return contentType


def tracksOverDuration(durationMin,discTracks):
    tracksRet = []
    
    for track in discTracks:
        if track.durationS >= durationMin:
            tracksRet.append(track)
    
    return tracksRet


def tracksUnderDuration(durationMax,discTracks):
    tracksRet = []
    
    for track in discTracks:
        if track.durationS <= durationMax:
            tracksRet.append(track)
    
    return tracksRet


if __name__ == "__main__":
    
    if len(sys.argv) <= 1:
        print 'Call with drive i.e. autorip.py /dev/disk2'
        sys.exit(1)

    discdevice=''

    argsList = sys.argv[1:]
    
    while ( len(argsList) > 0 ):
        discdevice = argsList[0]

        #Remove last argument
        argsList = argsList[1:]
        
    drive = disc_drive.DiscDrive(discdevice)
    
    if drive.isOpen():
       drive.closeTray()
    
    if not drive.isDiscInserted():
        print 'No disc inserted!'
        sys.exit(1)

    else:
        #load config
        config = config_to_dict.config_to_dict().do(os.path.join(dirname,'settings.ini'))

        #load ripper, scraper and notification
        notify = notification.notification(config['notification'])
        
        ripper = ripper.Ripper(config['ripper'],discdevice)

        logging.info( 'Format name: ' + ripper.formattedName())

        contentType = contentTypeForTracksAndName(ripper.discTracks(),ripper.formattedName(),config)
        
        logging.info( 'Content type: ' + contentType )

        mediascraper = scraper.MediaScraper(config['scraper'])
        
        mediaobjs = mediascraper.findContent(contentType,ripper.formattedName())
        
        if len(mediaobjs) is not 1:
            alt_name = dvdfingerprint.disc_title(drive.mountedPath())
            mediaobjs = mediascraper.findMovie(alt_name)
    
        ripTracks = []
    
        if contentType == 'movie':
            if config['ripper']['movie_rip_extras'].lower() == 'yes':
                minDuration = 0
                maxDuration = 9999
                ripExtraContent = True
            else:
                minDuration = int(config['ripper']['movie_min_length_seconds'])
                maxDuration = int(config['ripper']['movie_max_length_seconds'])
                ripExtraContent = False
            
            ripPathComplete = config['ripper']['movie_complete_save_path']
            ripPathIncomplete = config['ripper']['movie_incomplete_save_path']

        elif contentType == 'tvshow':
            if config['ripper']['tv_rip_extras'].lower() == 'yes':
                minDuration = 0
                maxDuration = 9999
                ripExtraContent = True
            else:
                minDuration = int(config['ripper']['tvepisode_min_length_seconds'])
                maxDuration = int(config['ripper']['tvepisode_max_length_seconds'])
                ripExtraContent = False

            ripPathComplete = config['ripper']['tv_incomplete_save_path']
            ripPathIncomplete = config['ripper']['tv_incomplete_save_path']
            
        else:
            print 'Unexpected content type ' + str(contentType)
            sys.exit(1)

        ripTracks = tracksUnderDuration(maxDuration, tracksOverDuration(minDuration,ripper.discTracks()))
        
        if ripExtraContent == False and len(mediaobjs) == 1:
            #we don't want the extra content and we have an exact match, Use the duration from the media object to filter out erronous matches
            mediaDurationS = mediaobjs[0].durationS
            logging.info( 'Filtering results to match duration ' + str(mediaDurationS) )
            ripTracks = tracksUnderDuration(mediaDurationS * 1.14, tracksOverDuration(mediaDurationS * 0.86,ripTracks))            


        logging.info( 'Video candidates:' + str(ripTracks) )

        if config['ripper']['backup_disc'] == 'no' and config['ripper']['rip_disc'] == 'no':
            logging.error( 'No ripping enabled. Not much to do without either rip_disc or backup_disc set to True' )
            sys.exit(1)

        if config['ripper']['backup_disc'].lower() == 'yes':
            logging.info( 'Making disk backup' )

            notify.startedBackingUpDisc(ripper.formattedName())

            ripper.ripDiscBackup( os.path.join(ripPathIncomplete,ripper.formattedName()) )

            notify.finishedBackingUpDisc(ripper.formattedName())

        if config['ripper']['rip_disc'].lower() == 'yes':
            logging.info( 'Ripping disc tracks' )
            
            notify.startedRippingTracks( ripTracks, ripper.formattedName() )
            
            ripper.ripDiscTracks( ripTracks, os.path.join(ripPathIncomplete,ripper.formattedName()) )

            didMove = False
        
            #rename output file only if there is 1-1 match
            if len(mediaobjs) == 1 and len(ripTracks) == 1:
                srcFile = os.path.join(ripPathIncomplete,ripper.formattedName(),ripTracks[0].outputFileName)
                newFileName = mediaobjs[0].title + ' ' + mediaojbs[0].production_year + ripTracks[0].outputFileName.split('.')[-1]
                dstFile = os.path.join(ripPathComplete,newFileName)

                os.rename(srcFile,dstFile)
                shutil.rmtree( os.path.join(ripPathIncomplete,ripper.formattedName()) )
            
                didMove = True
                
            #TODO change notify message to include move location
            
            notify.finishedRippingTracks( ripTracks, ripper.formattedName() )

        #lastly eject the tray
        drive.openTray()
        
    
    
