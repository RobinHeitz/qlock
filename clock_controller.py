from datetime import datetime
import logging
import traceback
import pytz
import time
from pixel_definition import (
    HOUR_DEF, MIN_POINTS_DEF, WD_10_1, WD_2, WD_20_1, WD_5_1, WD_GOOD_MORNING, WD_GOOD_NIGHT, WD_MIN_4, WD_IT_IS,WD_1_O_CLOCK,WD_CLOCK,
    WD_5_MIN_AFTER,WD_10_MIN_AFTER,WD_15_MIN_AFTER,WD_20_MIN_AFTER,WD_5_MIN_BEFORE_HALF,WD_HALF,
    WD_5_MIN_AFTER_HALF, WD_20_BEFORE,WD_15_BEFORE,WD_10_BEFORE,WD_5_BEFORE, WD_before, WD_quarter,
    WD_HAPPY, WD_HAPPY_BD,WD_BIRTHDAY,WD_CHARLY,WD_ALL_PIXELS
    )
from pixel_controller import PixelController

from helper_funcs import next_hour, translate_to_12h_clock_format, clock_words,hour_wording_rep,determineClockState


logging.basicConfig(filename="logging.log",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

logger = logging.getLogger('urbanGUI')


CLOCK_STATE_SHOW_CLOCK_TIME = "CLOCK_STATE_SHOW_CLOCK_TIME"
CLOCK_STATE_SHOW_GOOD_MORNING = "CLOCK_STATE_SHOW_GOOD_MORNING"
CLOCK_STATE_SHOW_GOOD_NIGHT = "CLOCK_STATE_SHOW_GOOD_NIGHT"

STD_COL = (255,255,255)

DEF_MIN_DOTS = "DEF_MIN_DOTS"
DEF_IT_IS = "DEF_IT_IS" 
DEF_TIME_WORDS = "DEF_TIME_WORDS" #after, half, 15 min before etc.
DEF_HOUR_WORD_REP = "DEF_HOUR_WORD_REP"

DEF_BIRTHDAY = "DEF_BIRTHDAY"

DEF_GOOD_NIGHT = "DEF_GOOD_NIGHT"
DEF_GOOD_MORNING = "DEF_GOOD_MORNING"

DEF_ClOCK_RELATED_KEYS = [DEF_MIN_DOTS, DEF_IT_IS, DEF_TIME_WORDS, DEF_HOUR_WORD_REP, DEF_BIRTHDAY]

class ChangePixels:

    def __init__(self, pixels,key,oldPixels=None, color=STD_COL):
        self.pixels = pixels
        self.key = key 
        self.oldPixels = oldPixels
        self.color = color

    def __str__(self):
        return 'pixels: {}'.format(self.pixels)



class ClockController:


    def __init__(self):
        logger.info("ClockController init method")
        self.birthDate = (6,14) # (month, day)
        # self.birthDate = (6,9) # (month, day)

        self.controller = PixelController()
        self.currentClockState = CLOCK_STATE_SHOW_CLOCK_TIME

        self.pixelStatus = {}
        self.changeQueue = []

        self.clock()

    
    def clock(self):
    
        try:
            while True:
                
                utc = pytz.timezone('UTC')
                now = utc.localize(datetime.utcnow())

                local_tz = pytz.timezone('Europe/Berlin')
                local_time = now.astimezone(local_tz)

                y = local_time.year
                m = local_time.month
                d = local_time.day
                hour = translate_to_12h_clock_format(local_time.hour)
                min = local_time.minute

                
                newClockState = determineClockState(local_time)
                if newClockState != self.currentClockState:
                    self.currentClockState = newClockState
                    logging.info(f"New current clockstate: {self.currentClockState}")
                    self.deactivate_active_pixels()

                
                if self.currentClockState == CLOCK_STATE_SHOW_CLOCK_TIME:
                    
                    #min dots
                    min_pixels = MIN_POINTS_DEF.get(min % 5)
                    old_min_pixels = self.pixelStatus.get(DEF_MIN_DOTS)
                    
                    if min_pixels != old_min_pixels:
                        self.changeQueue.append(ChangePixels(min_pixels, DEF_MIN_DOTS, old_min_pixels))

                    #it is
                    if self.pixelStatus.get(DEF_IT_IS) is None:
                        self.changeQueue.append(ChangePixels(WD_IT_IS,DEF_IT_IS))

                    #timing words, like 15 min before, half etc.
                    currentWord = clock_words(min)
                    oldWord =self.pixelStatus.get(DEF_TIME_WORDS)
                    if oldWord != currentWord:
                        #need change clock word
                        self.changeQueue.append(
                            ChangePixels(currentWord, DEF_TIME_WORDS,oldWord)
                        )
                    
                    #hour like 1, 2, 3 etc.
                    # DEF_HOUR_WORD_REP
                    currentHourWord = hour_wording_rep(min, hour)
                    oldHourWord = self.pixelStatus.get(DEF_HOUR_WORD_REP)
                    if currentHourWord != oldHourWord:
                        self.changeQueue.append(
                            ChangePixels(currentHourWord, DEF_HOUR_WORD_REP, oldHourWord)
                        )
                    
                    #check for birthday
                    old_bd = self.pixelStatus.get(DEF_BIRTHDAY)
                    cur_bd = []
                    if m == self.birthDate[0] and d == self.birthDate[1]:
                        #its her birthday
                        cur_bd  = WD_HAPPY_BD + WD_CHARLY

                    if old_bd != cur_bd:
                        self.changeQueue.append(ChangePixels(cur_bd, DEF_BIRTHDAY, old_bd, (28,217,230)))




                    

                elif self.currentClockState == CLOCK_STATE_SHOW_GOOD_MORNING:
                    
                    old_gm_pixels = self.pixelStatus.get(DEF_GOOD_MORNING)
                    cur_gm_pixels = WD_GOOD_MORNING +  WD_CHARLY
                    
                    if old_gm_pixels != cur_gm_pixels:

                        self.changeQueue.append(
                            ChangePixels(cur_gm_pixels, DEF_GOOD_MORNING)
                        )
                
                
                
                
                elif self.currentClockState == CLOCK_STATE_SHOW_GOOD_NIGHT:
                    
                    old_gn_pixels = self.pixelStatus.get(DEF_GOOD_NIGHT)
                    cur_gn_pixels = WD_GOOD_NIGHT + WD_CHARLY

                    if old_gn_pixels != cur_gn_pixels:
                        self.changeQueue.append(
                            ChangePixels(cur_gn_pixels, DEF_GOOD_NIGHT)
                        )
                
                if len(self.changeQueue) > 0: 
                    print("+++ len of queue:", len(self.changeQueue), datetime.now().strftime("%H:%M:%S"))
                self.workThroughQueue()
                


                time.sleep(1)

        except KeyboardInterrupt:
            self.deactivate_active_pixels()
        except Exception as e:
            logging.error(f"Exception occured, print(e) = {e}, tracepack = {traceback.print_exc()}")
                
    
    def deactivate_active_pixels(self):
        """Called once after time change, clears Pixels"""
        # self.controller.deactivatePixels(WD_ALL_PIXELS)

        pixels = []
        for key in self.pixelStatus.keys():
            pixels = pixels + self.pixelStatus.get(key,[])
            self.pixelStatus.pop(key)
        self.controller.deactivatePixels(pixels)


    def workThroughQueue(self):

        while len(self.changeQueue) > 0:
            p = self.changeQueue.pop()
            
            #deactive old pixels
            if p.oldPixels:
                self.controller.deactivatePixels(p.oldPixels)

            self.controller.activatePixelsRGB(p.pixels, *p.color)
            self.pixelStatus[p.key] = p.pixels

        
if __name__ == "__main__":
    controller = ClockController()

