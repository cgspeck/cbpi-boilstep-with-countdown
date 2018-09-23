# -*- coding: utf-8 -*-
import logging
import time

from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi

@cbpi.step
class BoilStepWithCountdownReminders(StepBase):
    '''
    BoilStep with reminders that are set relative to end of boil
    '''
    REMINDER_NAMES = [
        "Hop 1 Addition",
        "Hop 2 Addition",
        "Hop 3 Addition",
        "Hop 4 Addition",
        "Hop 5 Addition",
        "Prepare yeast",
        "Prepare finings",
        "Prepare cooling system",   
        "Dose finings",
        "Start hot-side cooling loop",
        "Prepare fermenter"        
    ]
    REMINDER_EPILOGE_ADD = " as minutes boiltime to the end"
    REMINDER_EPILOGE_PREP = " as minutes before end"
    
    # Properties
    temp = Property.Number("Temperature", configurable=True, default_value=99, description="Target temperature for boiling")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the boiling step takes place")
    timer = Property.Number("Timer in Minutes", configurable=True, default_value=90, description="Timer is started when target temperature is reached")

    reminder_00 = Property.Number(REMINDER_NAMES[0]+REMINDER_EPILOGE_ADD, configurable=True, description="Fill in times like in common recepies, e.g. Boil for 80 Minutes fill in 80")
    reminder_00_displayed = Property.Number("", default_value=None, description="Reminder displayed status")
    reminder_01 = Property.Number(REMINDER_NAMES[1]+REMINDER_EPILOGE_ADD, configurable=True)
    reminder_01_displayed = Property.Number("",default_value=None)
    reminder_02 = Property.Number(REMINDER_NAMES[2]+REMINDER_EPILOGE_ADD, configurable=True)
    reminder_02_displayed = Property.Number("", default_value=None)
    reminder_03 = Property.Number(REMINDER_NAMES[3]+REMINDER_EPILOGE_ADD, configurable=True)
    reminder_03_displayed = Property.Number("", default_value=None)
    reminder_04 = Property.Number(REMINDER_NAMES[4]+REMINDER_EPILOGE_ADD, configurable=True)
    reminder_04_displayed = Property.Number("", default_value=None)
    reminder_05 = Property.Number(REMINDER_NAMES[5]+REMINDER_EPILOGE_ADD, configurable=True)
    reminder_05_displayed = Property.Number("", default_value=None)
    reminder_06 = Property.Number(REMINDER_NAMES[6]+REMINDER_EPILOGE_PREP, configurable=True)
    reminder_06_displayed = Property.Number("", default_value=None, description="Reminder displayed status")
    reminder_07 = Property.Number(REMINDER_NAMES[7]+REMINDER_EPILOGE_PREP, configurable=True)
    reminder_07_displayed = Property.Number("", default_value=None, description="Reminder displayed status")
    reminder_08 = Property.Number(REMINDER_NAMES[8]+REMINDER_EPILOGE_PREP, configurable=True)
    reminder_08_displayed = Property.Number("", default_value=None, description="Reminder displayed status")
    reminder_09 = Property.Number(REMINDER_NAMES[9]+REMINDER_EPILOGE_PREP, configurable=True)
    reminder_09_displayed = Property.Number("", default_value=None, description="Reminder displayed status")
    reminder_10 = Property.Number(REMINDER_NAMES[10]+REMINDER_EPILOGE_PREP, configurable=True)
    reminder_10_displayed = Property.Number("", default_value=None, description="Reminder displayed status")

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return:
        '''
        self.set_target_temp(self.temp, self.kettle)
        self._logger = logging.getLogger(type(self).__name__)

    @cbpi.action("Start Timer Now")
    def start(self):
        '''
        :return:
        '''
        if self.is_timer_finished() is None:
            self.start_timer(int(self.timer) * 60)

    def reset(self):
        self.stop_timer()
        self.set_target_temp(self.temp, self.kettle)

    def finish(self):
        self.set_target_temp(0, self.kettle)

    def check_reminder(self, number):
        raw_value = self.__getattribute__("reminder_%02d" % number)

        if isinstance(raw_value, unicode) and raw_value != '' and self.__getattribute__("reminder_%02d_displayed" % number) is not True:
            value = int(raw_value)
            if self.countdown_time_has_expired(value):
                self.__setattr__("reminder_%02d_displayed" % number, True)
                reminder = self.REMINDER_NAMES[number]
                self.notify("Countdown Reminder", reminder, timeout=None)

    def countdown_time_has_expired(self, value):
        return time.time() > (self.timer_end - (value * 60))

    def execute(self):
        '''
        This method is executed in an interval
        :return:
        '''
        # Check if Target Temp is reached
        if self.get_kettle_temp(self.kettle) >= float(self.temp):
            # Check if Timer is Running
            if self.is_timer_finished() is None:
                self.start_timer(int(self.timer) * 60)
            else:
                for i in range(11):
                    self.check_reminder(i)

        if self.is_timer_finished() == True:
            self.notify("Boil Step Completed!", "Starting the next step", timeout=None)
            self.next()
