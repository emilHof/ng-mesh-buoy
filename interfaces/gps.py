import time
# can only be installed via pip install adafruit-circuitpython-gps (at the moment)
import adafruit_gps
# import serial via PySerial
import serial
import config.config as config
from interfaces.ports import Port


def _format_datetime(datetime):
    return "{:02}/{:02}/{} {:02}:{:02}:{:02}".format(
        datetime.tm_mon,
        datetime.tm_mday,
        datetime.tm_year,
        datetime.tm_hour,
        datetime.tm_min,
        datetime.tm_sec,
    )


class GPSInterface(Port):

    def __init__(self, specific_type):
        super().__init__(specific_type)
        self.gps = adafruit_gps.GPS(self.uart, debug=False)

    def setup_gps(self):
        az = ','
        cz = b','
        dz = az.encode('ASCII')
        if dz == cz:
            print("ENCODING SUCCESSFUL")
        else:
            print("encoding unsuccessful")
        # Turn on the basic GGA and RMC info (what you typically want)
        self.gps.send_command(b"PMTK314,0,1,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0")
        # Turn on just minimum info (RMC only, location):
        # gps.send_command(b'PMTK314,0,1,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # Turn off everything:
        # gps.send_command(b'PMTK314,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # Turn on everything (not all of it is parsed!)
        # gps.send_command(b'PMTK314,1,1,1,1,1,1,0,0,0,0,0,0,0,0,0,0,0,0,0')
        # Set update rate to once every 1000ms (1hz) which is what you typically want.
        self.gps.send_command(b"PMTK220,1000")
        print("gps setup!")

    def print_basics(self):
        last_print = time.monotonic()
        while True:
            # Make sure to call gps.update() every loop iteration and at least twice
            # as fast as data comes from the GPS unit (usually every second).
            # This returns a bool that's true if it parsed new data (you can ignore it
            # though if you don't care and instead look at the has_fix property).
            self.gps.update()
            # Every second print out current location details if there's a fix.
            current = time.monotonic()
            if current - last_print >= 1.0:
                last_print = current
                if not self.gps.has_fix:
                    # Try again if we don't have a fix yet.
                    print("Waiting for fix...")
                    # continue to loop (while)
                    continue
                # print the lat and long to the PI screen up to 6 decimal places
                print("Lat: {0:.6f}".format(self.gps.latitude))
                print("Long: {0:.6f}".format(self.gps.longitude))
                # prepare data for transmission through Radio connected via USB
                # limit decimal places of latitude and longitude
                limited_lat = "{:.6f}".format(self.gps.latitude)
                limited_long = "{:.6f}".format(self.gps.longitude)
                # convert from float to string
                lat_in_string = str(limited_lat)
                long_in_string = str(limited_long)
                # concatenate string
                gps_string = lat_in_string + "," + long_in_string
                # Time & date from GPS informations
                print("Fix timestamp: {}".format(_format_datetime(self.gps.timestamp_utc)))
                # Time & date from internal RTC
                #        print("RTC timestamp: {}".format(_format_datetime(the_rtc.datetime)))
                # Time & date from time.localtime() function
                local_time = time.localtime()
                print("Local time: {}".format(_format_datetime(local_time)))
                # convert from string to bytes
                gps_data = str.encode(gps_string)
                # send data down USB port to radio.
                # data_out_port.write(gps_data)

    def close_gps(self):
        print("Show's over. Close the ports!")
        self.uart.close()

    def get_location(self):
        lat = "Lat: {0:.6f}".format(self.gps.latitude)
        long = "Long: {0:.6f}".format(self.gps.longitude)
        return lat + long
