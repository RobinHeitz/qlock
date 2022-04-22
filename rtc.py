import os
import sys
import pyRPiRTC
import logging

def _setup_logger():
    logging.basicConfig(filename='/home/pi/dev/qlock/rtc.log', encoding='utf-8', level=logging.DEBUG)

def update_pi_time_from_rtc():
    # get time from RTC and set it as system date/time
    _setup_logger()
    logging.info("########################")
    logging.info("update_pi_time_from_rtc()")

    rtc = pyRPiRTC.DS1302(clk_pin=11, data_pin=13, ce_pin=15)
    try:
        dt = rtc.read_datetime()
        logging.info("Formatted datetime-string from rtc:")
        dt_formatted = dt.strftime('%Y%m%d %H:%M:%S')
        logging.info(dt_formatted)
        print(dt_formatted)
        
        os.system('sudo date -s "{}"'.format(dt_formatted))
    
    except ValueError:
        print("Error with RTC chip, check wiring")

    except Exception as e:
        print("Exception:")
        print(e)
    
    finally:
        rtc.close()


def update_rtc_time_from_pi():
    _setup_logger()
    logging.info('##############')
    logging.info('update_rtc_time_from_pi()')

    rtc = pyRPiRTC.DS1302(clk_pin=11, data_pin=13, ce_pin=15)
    try:
        dt_write = datetime.datetime.utcnow()
        rtc.write_datetime(dt_write)
        dt_read = rtc.read_datetime()
    
        if -2 < (dt_write - dt_read).total_seconds() < +2:
            logging.info("updating RTC was successfull")
            logging.info(dt_write.strftime('%Y%m%d %H:%M:%S'))            
            
        else:
            logging.debug("Unable to set RTC time")
    except ValueError:
        logging.debug('error with RTC chip, check wiring')
    finally:
        rtc.close()


if __name__ == "__main__":
    # when booting, update pi's clock
    update_pi_time_from_rtc()