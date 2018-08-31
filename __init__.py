# -*- coding: utf-8 -*-
import time


from modules.core.props import Property, StepProperty
from modules.core.step import StepBase
from modules import cbpi

@cbpi.step
class BoilStepWithCountdownReminders(StepBase):
    '''
    BoilStep with reminders that are set relative to end of boil
    '''
    # Properties
    temp = Property.Number("Temperature", configurable=True, default_value=100, description="Target temperature for boiling")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the boiling step takes place")
    timer = Property.Number("Timer in Minutes", configurable=True, default_value=90, description="Timer is started when target temperature is reached")
    hop_1 = Property.Number("Hop 1 Addition", configurable=True, description="Fist Hop alert")
    hop_1_added = Property.Number("",default_value=None)
    hop_2 = Property.Number("Hop 2 Addition", configurable=True, description="Second Hop alert")
    hop_2_added = Property.Number("", default_value=None)
    hop_3 = Property.Number("Hop 3 Addition", configurable=True)
    hop_3_added = Property.Number("", default_value=None, description="Third Hop alert")
    hop_4 = Property.Number("Hop 4 Addition", configurable=True)
    hop_4_added = Property.Number("", default_value=None, description="Fourth Hop alert")
    hop_5 = Property.Number("Hop 5 Addition", configurable=True)
    hop_5_added = Property.Number("", default_value=None, description="Fifth Hop alert")
    hop_timer_mode = Property.Select("Hop timer mode", options=["Stopwatch", "Countdown"], description="Stopwatch counts time from start of boil, Countdown counts time to end of boil.")

    def init(self):
        '''
        Initialize Step. This method is called once at the beginning of the step
        :return:
        '''
        self.set_target_temp(self.temp, self.kettle)

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

    def check_hop_timer(self, number, value):
        if self.__getattribute__("hop_%s_added" % number) is not True:
            do_message = False

            if self.hop_timer_mode == "Countdown" and time.time() > (self.timer_end - (int(value) * 60)):
                do_message = True
            elif time.time() > (self.timer_end - (int(self.timer) * 60 - int(value) * 60)):
                do_message = True

            if do_message:
                self.__setattr__("hop_%s_added" % number, True)
                self.notify("Hop Alert", "Please add Hop %s" % number, timeout=None)

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
                self.check_hop_timer(1, self.hop_1)
                self.check_hop_timer(2, self.hop_2)
                self.check_hop_timer(3, self.hop_3)
                self.check_hop_timer(4, self.hop_4)
                self.check_hop_timer(5, self.hop_5)
        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            self.notify("Boil Step Completed!", "Starting the next step", timeout=None)
            self.next()
