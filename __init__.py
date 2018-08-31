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
    # Properties
    temp = Property.Number("Temperature", configurable=True, default_value=100, description="Target temperature for boiling")
    kettle = StepProperty.Kettle("Kettle", description="Kettle in which the boiling step takes place")
    timer = Property.Number("Timer in Minutes", configurable=True, default_value=90, description="Timer is started when target temperature is reached")

    reminder_1 = Property.Number(REMINDER_DESCRIPTIONS[1], configurable=True)
    reminder_1_displayed = Property.Number("",default_value=None)
    reminder_2 = Property.Number("Hop 2 Addition", configurable=True)
    reminder_2_displayed = Property.Number("", default_value=None)
    reminder_3 = Property.Number("Hop 3 Addition", configurable=True)
    reminder_3_displayed = Property.Number("", default_value=None)
    reminder_4 = Property.Number("Hop 4 Addition", configurable=True)
    reminder_4_displayed = Property.Number("", default_value=None)
    reminder_5 = Property.Number("Hop 5 Addition", configurable=True)
    reminder_5_displayed = Property.Number("", default_value=None)

    reminder_6 = Property.Number("Prepare Yeast", configurable=True)
    reminder_6_displayed = Property.Number("", default_value=None, description="Reminder displayed status")
    reminder_7 = Property.Number("Prepare Finings", configurable=True)
    reminder_7_displayed = Property.Number("", default_value=None, description="Reminder displayed status")
    reminder_8 = Property.Number("Prepare Cooling System", configurable=True)
    reminder_8_displayed = Property.Number("", default_value=None, description="Reminder displayed status")
    reminder_9 = Property.Number("Dose Finings", configurable=True)
    reminder_9_displayed = Property.Number("", default_value=None, description="Reminder displayed status")
    reminder_10 = Property.Number("Start Hot-Side Cooling Loop", configurable=True)
    reminder_10_displayed = Property.Number("", default_value=None, description="Reminder displayed status")
    reminder_11 = Property.Number("Prepare Fermenter", configurable=True)
    reminder_11_displayed = Property.Number("", default_value=None, description="Reminder displayed status")


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

    def check_reminder(self, number):
        reminder = getattr(self, "reminder_%s" % number)
        value = reminder.value
        if self.__getattribute__("reminder_%s_displayed" % number) is not True:
            if countdown_time_has_expired(value):
                self.__setattr__("reminder_%s_displayed" % number, True)
                description = reminder.description
                self.notify("Countdown Reminder", description, timeout=None)

    @staticmethod
    def countdown_time_has_expired(value):
        return time.time() > (self.timer_end - (int(value) * 60))

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
                # for i in range(1, 12):
                for i in range(1, 2):
                    self.check_reminder(i)
                # self.check_reminder(1, self.hop_1)
                # self.check_hop_timer(2, self.hop_2)
                # self.check_hop_timer(3, self.hop_3)
                # self.check_hop_timer(4, self.hop_4)
                # self.check_hop_timer(5, self.hop_5)
        # Check if timer finished and go to next step
        if self.is_timer_finished() == True:
            self.notify("Boil Step Completed!", "Starting the next step", timeout=None)
            self.next()
