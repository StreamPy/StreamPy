'''
Created on Sep 14, 2015

@author: Julian
'''
import sys
import time
#import ntplib
import logging
import numpy
import threading
import datetime


NTP_INTERVAL = 60.0
MIN_POINTS_TIME_FIT = 10
MAX_POINTS_TIME_FIT = 60
MAX_OFFSET_ALLOWED = 3600.0

class AccurateTimestamp(object):

    def __init__(self, time_servers):
        '''
        Constructor
        '''
        self.time_servers = time_servers
        self.timing_gradient = 0.0
        self.timing_intercept = 0.0
        self.last_offset = 0.0
        self.timing_base_time = time.time()
        self.running = False
        self.timing_lock = threading.Lock()
        
        try:
            self.ntpDaemon = threading.Thread(target=self.ntpThread)
            self.ntpDaemon.setDaemon(True)
            self.ntpDaemon.start()
        except Exception, errtxt:
            raise sys.exit(errtxt)

    def ntpThread(self):
        ntp_client = ntplib.NTPClient()
        # we start off needing to accumulate points for the line fit quickly
        startup_seconds = 1
        ntp_interval = startup_seconds
        
        line_fit_m = 0.0
        line_fit_c = 0.0
        
        x_points = []
        y_points = []
        
        base_time = time.time()
        start_time = base_time
        
        self.running = True
        while self.running:
            if ntp_interval < NTP_INTERVAL:
                startup_seconds += 2
                ntp_interval = startup_seconds
            else:
                ntp_interval = ntp_interval
                
            response = None
            
            for time_server in self.time_servers:
                try:
                    start_time = time.time()
                    response = ntp_client.request(time_server, version=3)
                    break
                except:
                    logging.warn('NTP: No response from %s',time_server)
              
            # if there is a response, and the offset is not ridiculous, add it to the fit
            # (a ridiculous offset can be caused if the NTP server is broken, for example)        
            if response: 
                if abs(response.offset) < MAX_OFFSET_ALLOWED :
                    self.last_offset = response.offset 
                    # add a point to the line for fitting
                    diff_epoch = (start_time-base_time) 
                    x_points.append(diff_epoch)
                    y_points.append(response.offset)
                    
                    if len(x_points) > MIN_POINTS_TIME_FIT:
                        while len(x_points) > MAX_POINTS_TIME_FIT:
                            x_points = x_points[1:]
                            y_points = y_points[1:]
                        
                        # get the current estimate
                        offset_estimate = diff_epoch*line_fit_m + line_fit_c
                        logging.info('Time server %s Offset %10.6f Estimate %10.6f Error %8.6fs',\
                                     time_server,response.offset,offset_estimate,response.offset-offset_estimate)
                        
                        # do the line fit to solve for y = mx+c
                        x_mean = numpy.mean(x_points)
                        y_mean = numpy.mean(y_points)
                        sum_xy = 0.0
                        sum_x2 = 0.0
                        for x,y in zip(x_points, y_points):
                            sum_xy += (x-x_mean)*(y-y_mean)
                            sum_x2 += (x-x_mean)*(x-x_mean)
                        line_fit_m = sum_xy / sum_x2
                        line_fit_c = y_mean - (line_fit_m*x_mean)
                        
                        #logging.info('Time interval %s Line fit m, c %s %s %s points',\
                        #             ntp_interval,line_fit_m, line_fit_c,len(x_points))   

                        self.setTimingFitVariables(base_time, line_fit_m, line_fit_c)
                else:
                    logging.warning('Time server %s reports excessive offset of %s - ignored', time_server, response.offset)
                    
            elapsed = time.time() - start_time
            if ntp_interval > elapsed:
                time.sleep(ntp_interval-elapsed) 
        logging.warn('NTP thread terminated')   

    def setTimingFitVariables(self, base_time, gradient, intercept):
        # this is called by the main client which is monitoring the system clock compared with NTP
        with self.timing_lock:
            self.timing_base_time = base_time
            self.timing_gradient = gradient
            self.timing_intercept = intercept
            
    def GetNtpCorrectedTimestamp(self):
        # from the current system time we use the NTP thread's line fit to estimate the true time
        time_now = time.time()
        offset_estimate = (time_now-self.timing_base_time) * self.timing_gradient + self.timing_intercept       
        return time_now + offset_estimate
    
    def GetNtpOffsetEstimate(self):
        time_now = time.time()
        offset_estimate = (time_now-self.timing_base_time) * self.timing_gradient + self.timing_intercept       
        return offset_estimate



def main():
    import matplotlib.pyplot as plt
    from matplotlib.lines import Line2D
    from matplotlib.text import Text
    
    plt.ion()
    
    TIME_SERVERS = ["ntp-02.caltech.edu","0.us.pool.ntp.org","1.us.pool.ntp.org","2.us.pool.ntp.org","3.us.pool.ntp.org"]


    log = logging.getLogger('')
    log.setLevel(logging.INFO)
        
    format = logging.Formatter("%(asctime)s - %(levelname)s - %(message)s")
       
    ch = logging.StreamHandler(sys.stdout)
    ch.setFormatter(format)
    log.addHandler(ch)
    
    time_stamper = AccurateTimestamp(TIME_SERVERS)
    
    min_time = -3600.0
    max_time = 0.0
    min_offset = -0.01
    max_offset = 0.01
    
    time_data = [0.0]
    offset_data = [0.0]
    offset_predicted_data = [0.0]
    timestamps = [time.time()]
        
    fig_size = plt.rcParams["figure.figsize"]
    fig_size[0] = 12
    fig_size[1] = 5
    plt.rcParams["figure.figsize"] = fig_size
        
    figure, ax = plt.subplots()
        
    line_offsets = Line2D(time_data, offset_data, color='blue')
    line_predicted = Line2D(time_data, offset_predicted_data, color='red')
    ax.add_line(line_offsets)
    ax.add_line(line_predicted)
    ax.set_xlim(min_time, max_time)
    #ax.set_ylim(min_offset,max_offset)
    ax.set_title('NTP Offsets and Predictions')
    ax.set_ylabel('Seconds')
    ax.grid('on') 

    plt.xlabel('Seconds in Past')
    plt.legend(['NTP offset', 'Predicted Offset'], loc='upper left')

    while not time_stamper.running:
        time.sleep(1.0)
    
    while True:
        corrected_time = time_stamper.GetNtpCorrectedTimestamp()
        predicted_offset = time_stamper.GetNtpOffsetEstimate()
        last_offset = time_stamper.last_offset
        logging.info('Offset Estimate %s Accurate Time %s',predicted_offset,datetime.datetime.fromtimestamp(corrected_time))
        
        t_now = time.time()

               
        t_diff = t_now - timestamps[0]
        for i in range(len(time_data)):
            time_data[i] -= t_diff
            timestamps[i] -= t_diff
            
        time_data = [0.0] + time_data
        offset_data = [last_offset] + offset_data
        offset_predicted_data = [predicted_offset] + offset_predicted_data
        timestamps = [t_now] + timestamps

        while time_data[-1] < min_time:
            del time_data[-1]
            del offset_data[-1]
            del offset_predicted_data[-1]
            del timestamps[-1]
            
        line_offsets.set_data(time_data, offset_data)
        line_predicted.set_data(time_data, offset_predicted_data)
        
        ymin = min(offset_data) - 0.025
        ymax = max(offset_data) + 0.025
        
        ax.set_ylim(ymin,ymax)
                     
        figure.canvas.draw()
        figure.canvas.flush_events()

        time.sleep(10.0)
    
    
if __name__ == '__main__':
    main()
        