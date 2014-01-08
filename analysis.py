""" Module for analyzing data produced by cell testing hardware

Author: Rich Winslow
Principal Investigators: Prof. Paul Wright, Prof. James Evans
University: University of California, Berkeley

classes:
    Ardustat:
        methods:
            __init__(*filename)
            get_cycle_data()
            plot_voltage()
            plot_current()
            plot_capacity()
            plot_power()

"""

import numpy
import matplotlib.pyplot as plt


class Ardustat:
    """ Analyzes data produced from Ardustats

    Separates data into individual cycles for analysis. Will determine charge
    and discharge capacity along with charge and discharge power.

    __init__:
        filepath = Path to data

    default attributes:
        time_index = 0
            Column in .dat file that corresponds to time
        voltage_index = 5
            Column in .dat file that corresponds to voltage
        current_index = 8
            Column in .dat file that corresponds to current

    """

    time_index = 0
    voltage_index = 5
    current_index = 8

    def __init__(self, filepath, **kwargs):
        """ Opens file and processes all data

        Retrieves time, voltage, and current data from file. Time is converted
        from milliseconds to hours.

        Cycle data is calculated and analyzed.

        """

        self.filepath = filepath

        self.time = []
        self.voltage = []
        self.current = []

        with open(filepath) as f:
            rows = f.readlines()

            for row in rows:
                count = 0
                for index, value in enumerate(row.split(' ')):
                    if index == self.time_index:
                        self.time.append(float(value))
                    elif index == self.voltage_index:
                        self.voltage.append(float(value))
                    elif index == self.current_index:
                        self.current.append(float(value))

            self.time = [(x-self.time[0])/3600000 for x in self.time]
            self.get_cycle_data()

    def get_cycle_data(self):
        """ Analyzes current data to find cycle boundaries

        Builds lists for time, voltage, and current based on the cycles found
        by analyzing the current profile. Discharge/charge is determined by the
        sign of the current. When it switches from (+) to (-) (or vice versa)
        a boundary is found and the accumulated data is recorded as a single
        cycle.

        After finding the individual cycles, the data is numerically
        integrated with trapezoids (numpy.trapz())

        The absolute value of all current data is used instead of the negative
        values produced by the Ardustats.

        Creates the following attributes:
            Time, voltage, and current data points for each identified charge
            cycle:
                self.time_cycles_raw_charge
                self.voltage_cycles_raw_charge
                self.current_cycles_raw_charge
                self.charge_capacity
                self.charge_power

            Time, voltage, and current data points for each identified
            discharge cycle:
                self.time_cycles_raw_discharge
                self.voltage_cycles_raw_discharge
                self.current_cycles_raw_discharge
                self.discharge_capacity
                self.discharge_power

        """

        # Variable initialization
        self.time_cycles_raw_charge = []
        self.voltage_cycles_raw_charge = []
        self.current_cycles_raw_charge = []
        self.charge_capacity = []
        self.charge_power = []

        self.time_cycles_raw_discharge = []
        self.voltage_cycles_raw_discharge = []
        self.current_cycles_raw_discharge = []
        self.discharge_capacity = []
        self.discharge_power = []

        time_group = []
        voltage_group = []
        current_group = []

        # Data binning and assignment
        for index in range(len(self.current)-1):
            time_group.append(self.time[index])
            voltage_group.append(self.voltage[index])
            current_group.append(self.current[index])

            if self.current[index+1] > 0 and self.current[index] < 0:
                current_group = [numpy.abs(value) for value in current_group]

                self.time_cycles_raw_charge.append(time_group)
                self.voltage_cycles_raw_charge.append(voltage_group)
                self.current_cycles_raw_charge.append(current_group)

                time_group = []
                voltage_group = []
                current_group = []

            elif self.current[index+1] < 0 and self.current[index] > 0:
                current_group = [numpy.abs(value) for value in current_group]

                self.time_cycles_raw_discharge.append(time_group)
                self.voltage_cycles_raw_discharge.append(voltage_group)
                self.current_cycles_raw_discharge.append(current_group)

                time_group = []
                voltage_group = []
                current_group = []

        # Numeric integration
        for index in range(len(self.current_cycles_raw_discharge)):
            time = self.time_cycles_raw_discharge[index]
            voltage = self.voltage_cycles_raw_discharge[index]
            current = self.current_cycles_raw_discharge[index]
            power = [voltage[index]*current[index]
                     for index in range(len(current))]

            self.discharge_capacity.append(numpy.trapz(current, x=time))
            self.discharge_power.append(numpy.trapz(power, x=time))

        for index in range(len(self.current_cycles_raw_charge)):
            time = self.time_cycles_raw_charge[index]
            voltage = self.voltage_cycles_raw_charge[index]
            current = self.current_cycles_raw_charge[index]
            power = [voltage[index]*current[index]
                     for index in range(len(current))]

            self.charge_capacity.append(numpy.trapz(current, x=time))
            self.charge_power.append(numpy.trapz(power, x=time))

    def plot_voltage(self):
        """ Plots voltage versus time """

        plt.plot(self.time, self.voltage)

        plt.xlabel('Time (h)')
        plt.ylabel('Voltage (V)')
        plt.title('Voltage v. Time - ' + self.filepath)
        plt.show()

    def plot_current(self):
        """ Plots current versus time """

        plt.plot(self.time, self.current)

        plt.xlabel('Time (h)')
        plt.ylabel('Current (mA)')
        plt.title('Current v. Time - ' + self.filepath)
        plt.show()

    def plot_capacity(self):
        """ Plots charge and discharge capacity versus cycle """

        plt.plot(self.discharge_capacity, 'o', label='Discharge')
        plt.plot(self.charge_capacity, 'o', label='Charge')

        plt.xlabel('Cycle')
        plt.ylabel('Capacity (mAh)')
        plt.title('Capacity v. Time - ' + self.filepath)
        plt.legend()
        plt.show()

    def plot_power(self):
        """ Plots charge and discharge power versus cycle """

        plt.plot(self.discharge_power, 'o', label='Discharge')
        plt.plot(self.charge_power, 'o', label='Charge')

        plt.title('Power v. Time - ' + self.filepath)
        plt.xlabel('Cycle')
        plt.ylabel('Power (mWh)')
        plt.legend()
        plt.show()
