from termcolor import colored
from enum import Enum
from datetime import datetime
from datetime import timedelta

import time
import msvcrt
import sys
import os

# Enviroiment variables
main_color = 'red'
sec_color = 'yellow'
log_dir = 'logs/' 
log_prefix = ''

##################
# Data structure #
##################

n_subj = 4
class Subj(Enum):
    ACSO = 1
    ANL2 = 2
    OEMT = 3
    LOGALG = 4
    TIMEOFF = 5

    @staticmethod
    def from_str(s):
        for sub in Subj:
            if s == sub.name:
                return sub
        raise Exception('Invalid subject name')

class Activity:
    sub = Subj(5)
    start_time = datetime.min
    end_time = datetime.min
    
    def __init__(self, sub):
        self.sub = sub
        self.start_time = datetime.now() 
        self.end_time = datetime.min
    def end(self):
        self.end_time = datetime.now()
    def get_timedelta(self):
        if self.end_time == datetime.min:
            return timedelta.min
        return self.end_time - self.start_time
    def print(self):
        print(self.sub.name + '\t\t' + time_stamp(self.start_time) + '   \t' + time_stamp(self.end_time) + '   \t' + timedelta_stamp(self.get_timedelta()))
    def logstr(self):
        return self.sub.name + '\t\t' + time_stamp(self.start_time) + '   \t' + time_stamp(self.end_time) + '   \t' + timedelta_stamp(self.get_timedelta())

class Stats():
    start_time = datetime.min
    end_time = datetime.min
    log_file = ''
    activity_list = []    

    subj_total_time = []
    
    study_time = timedelta()
    timeoff_time = timedelta()
    study_timeoff_ratio = 0.0

    def __init__(self):
        self.start_time = datetime.now()
        self.log_file = log_dir + log_prefix + date_stamp(self.start_time) + '[' + str(self.start_time.hour) + ']' + '.txt'
    
    def end(self):
        self.end_time = datetime.now()
    
    def delete_last_activity(self): # So che è brutto ma non ho voglia
        last = self.activity_list.pop()
        self.activity_list.pop()
        self.activity_list.append(last)

    def add_manual_activity(self):
        valid = False
        sub = Subj(5)
        while valid == False:
            s = input('Subject: ')
            valid = True
            try:
                sub = Subj.from_str(s)
            except:
                print('Invalid subject name')
                valid = False
        # This part doesn't do exceptions handling
        sstr = input('Start Time: ')
        slist = sstr.split(':')
        starttime = datetime.now()
        starttime.hour=int(slist[0])
        starttime.minute=int(slist[1])
        starttime.second=int(slist[2])
        
        sstr = input('End Time: ')
        slist = sstr.split(':')
        endtime = datetime.now()
        endtime.hour=int(slist[0])
        endtime.minute=int(slist[1])
        endtime.second=int(slist[2])
        
        act = Activity(sub, start_time=starttime, end_time=endtime)
        old_act = self.activity_list.pop()
        self.activity_list.append(act)
        self.activity_list.append(old_act) # Does this so the activity running can be continued
        

    def log(self):
        log = open(self.log_file, "w+")
        log.write(date_stamp(self.start_time) + '\n')
        log.write(time_stamp(self.start_time) + '\n')
        log.write(time_stamp(self.end_time) + '\n')
        for act in self.activity_list:
            log.write(act.logstr() + '\n')
        log.write('###\n')
        for stat in self.subj_total_time:
            log.write(stat[0].name + ':    \t' + timedelta_stamp(stat[1]) + '\n')
        log.write('###\n')
        log.write('ST: ' + timedelta_stamp(self.study_time) + '\n')
        log.write('TO: ' + timedelta_stamp(self.timeoff_time) + '\n')
        log.write('S/T: ' + str(self.study_timeoff_ratio) + '\n')
        log.close()
    
    def compute_stats(self):
        for sub in Subj:
            self.subj_total_time.append([sub, timedelta()])
        for act in self.activity_list:
            i = 0
            while act.sub != (self.subj_total_time[i])[0]:
                i = i + 1
            (self.subj_total_time[i])[1] = (self.subj_total_time[i])[1] + act.get_timedelta()
        for stat in self.subj_total_time:
            if stat[0] != Subj.TIMEOFF:
                self.study_time = self.study_time + stat[1]
            else:
                self.timeoff_time = stat[1]
        self.study_timeoff_ratio = self.study_time / self.timeoff_time 

    def print(self):
        print('Session Stats:                   log: "' + self.log_file + '"')
        print(date_stamp(self.start_time))
        print(time_stamp(self.start_time) + ' - ' + time_stamp(self.end_time))
        print()
        for stat in self.subj_total_time:
            print(stat[0].name + ':    \t' + timedelta_stamp(stat[1]))
        print()
        print('Total study time: ' + timedelta_stamp(self.study_time))
        print('Total time off time: ' + timedelta_stamp(self.timeoff_time))
        print()
        print('Study / Timeoff ratio: ' + str(self.study_timeoff_ratio))
        

############################
# Graphical User Interface #
############################

# Print helper functions 
def time_stamp(time):
    if time == datetime.min:
        return '  ----  '
    return str(time.hour) + ':' + str(time.minute) + ':' + str(time.second)
def date_stamp(date):
    if date == datetime.min:
        return '  ----  '
    return str(date.day) + '-' + str(date.month) + '-' + str(date.year)
def timedelta_stamp(time):
    if time == timedelta.min:
        return '  ----  '
    return str(time).split('.')[0]

def clear():
    os.system('cls')

# Main screen writer function
def gui(selected):
    clear()
    print(colored('Session Clock', main_color))
    print('\t\t\t\t\t\t\t' + colored(time_stamp(session_stats.start_time), sec_color) + '\n')

    for i in range(1, n_subj + 1):
        sub = Subj(i)
        if sub.value == selected:
            print('[' + colored(str(sub.value), main_color) + '] ' + sub.name + '   ', end='')
        else:
            print('[' + str(sub.value) + '] ' + sub.name + '   ', end='')
    print()
    if selected == Subj.TIMEOFF.value:
        print('[' + colored('p', main_color) + '] ' + 'TIME OFF')
    else:
        print('[p] TIME OFF')
    print('[x] EXIT')

    print('\n\nActivity List:')
    print('Name            Start           End             Time')
    for act in session_stats.activity_list:
        act.print()


#####################
# Program Execution #
#####################


# Session data init
session_stats = Stats()

sel = 5 # Start the program in TimeOff
session_stats.activity_list.append(Activity(Subj(sel))) # Loads the firs TimeOff
while True:
    gui(sel)
    # Wait and read input
    c = msvcrt.getch().decode('utf-8')
    if c == '\000' or c == '\xe0' or c == 'x': # Exit program
        session_stats.activity_list[session_stats.activity_list.__len__() - 1].end() # End the last activity
        session_stats.end() # Finalize session stats
        session_stats.compute_stats()
        session_stats.log()
        gui(0)
        print('\n\n')
        session_stats.print()
        break
    if c == '\b': # Delete last activity
        session_stats.delete_last_activity()
    if c == 'm': # Insert manual activity
        session_stats.add_manual_activity()
    # Input conversion
    try:
        sel = int(c)
    except:
        sel = 0
    if c == 'p': # Pause
        sel = 5
    
    valid_selection = False
    if sel >= 1 and sel <= n_subj + 1: # For TIMEOFF
        valid_selection = True
    
    if valid_selection == True:
        session_stats.activity_list[session_stats.activity_list.__len__() - 1].end() # Ends the previous activity
        session_stats.activity_list.append(Activity(Subj(sel)))
        
print('\nClosing session...')
time.sleep(1)

