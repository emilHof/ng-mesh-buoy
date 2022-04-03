import datetime
import time
import datetime

import adafruit_gps
import config.config as config
from interfaces.database import DBInterface
from interfaces.ports import Port
import asyncio


# sets the data and time format
def _format_datetime(dt):
    return "{:02}:{:02}:{:02}".format(
        dt.tm_hour,
        dt.tm_min,
        dt.tm_sec,
    )


def time_dif_gps(a, b):
    d_second = int(b.second) - int(a.tm_sec)
    d_minute = int(b.minute) - int(a.tm_min) + int(d_second / 60)
    d_hour = int(b.hour) - int(a.tm_hour) + int(d_minute / 60)
    return datetime.time(d_hour%24, d_minute%60, d_second%60)


def time_dif(a, b):
    d_second = int(b.second) - int(a.second)

    d_minute = int(b.minute) - int(a.minute) + int(d_second / 60)

    d_hour = int(b.hour) - int(a.hour) + int(d_minute / 60)

    return datetime.time(d_hour % 24, d_minute % 60, d_second % 60)


def time_add(a, b):
    add_seconds = int(b.second) + int(a.second)

    add_minutes = int(b.minute) + int(a.minute) + int(add_seconds / 60)

    add_hour = int(a.hour) + int(b.hour) + int(add_minutes / 60)

    return datetime.time(hour=(add_hour % 24), minute=(add_minutes % 60), second=(add_seconds % 60))


def get_time_sync():
    gps_time = config.config["time"]["time_stamp"]
    time_last = config.config["time"]["time_last"]
    time_guess = datetime.datetime.now()

    print("print gps time", gps_time)

    time_delta = time_dif(time_last, time_guess)

    time_now = time_add(gps_time, time_delta)

    return time_now


class GPSInterface(Port):

    def __init__(self):
        super().__init__("gps")
        self.gps = adafruit_gps.GPS(self.uart, debug=False)
        self.set_onboard_time()
        self.log = True
        self.db = DBInterface()

    def set_onboard_time(self) -> datetime:
        self.gps.update()
        gps_time = self.get_time_non_conv()
        time_last = datetime.datetime.now() - datetime.timedelta(seconds=1)
        gps_time = datetime.time(gps_time.tm_hour, gps_time.tm_min, gps_time.tm_sec)
        config.config["time"]["time_stamp"] = gps_time
        config.config["time"]["time_last"] = time_last

        return time_last

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
                # Time & date from GPS information
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

    def get_location(self):
        attempts = 0
        while attempts < 10:
            self.gps.update()
            if not self.gps.has_fix:
                print("waiting for fix...")
                time.sleep(1)
                attempts += 1
                continue
            attempts = 10
        lat = "Lat: {0:.6f}".format(self.gps.latitude)
        long = "Long: {0:.6f}".format(self.gps.longitude)
        return lat + " " + long

    def get_time(self):
        attempts = 0
        utc_time = ""
        while attempts < 20:
            self.gps.update()
            if not self.gps.has_fix:
                print("waiting for fix...")
                time.sleep(1)
                attempts += 1
                continue
            utc_time = "{}".format(_format_datetime(self.gps.timestamp_utc))
            attempts = 20
        return utc_time

    def get_time_non_conv(self):
        attempts = 0
        while attempts < 20:
            self.gps.update()
            if not self.gps.has_fix:
                print("waiting for fix...")
                time.sleep(1)
                attempts += 1
                continue
            attempts = 20

        return self.gps.timestamp_utc

    async def log_location_and_time(self):
        self.db.gps_index += 1
        index = self.db.gps_index
        while True:
            if self.log:
                attempts = 0
                while attempts < 5:
                    self.gps.update()
                    if not self.gps.has_fix:
                        print("waiting for fix...")
                        await asyncio.sleep(1)
                        attempts += 1
                        continue
                    attempts = 5
                lat = "Lat: {0:.6f}".format(self.gps.latitude)
                long = "Long: {0:.6f}".format(self.gps.longitude)
                location = lat + " " + long
                utc_time = "Local time: {}".format(_format_datetime(self.gps.timestamp_utc))
                data = (index, location, utc_time)
                err = self.db.write_loc_to_db(data)
                if err is not None:
                    print(err)
                index += 1
                print("committed new "
                      "location and time data to the database:", location)
                await asyncio.sleep(30)
            else:
                await asyncio.sleep(60)
