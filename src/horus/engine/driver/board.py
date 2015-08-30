# -*- coding: utf-8 -*-
# This file is part of the Horus Project

__author__ = 'Jesús Arroyo Torrens <jesus.arroyo@bq.com>'
__copyright__ = 'Copyright (C) 2014-2015 Mundo Reader S.L.'
__license__ = 'GNU General Public License v2 http://www.gnu.org/licenses/gpl2.html'

import time
import serial
import threading


class WrongFirmware(Exception):

    def __init__(self):
        Exception.__init__(self, _("Wrong Firmware"))


class BoardNotConnected(Exception):

    def __init__(self):
        Exception.__init__(self, _("Board Not Connected"))


class Board(object):

    """Board class. For accessing to the scanner board

    Gcode commands:

        G1 Fnnn : feed rate
        G1 Xnnn : move motor

        M70 Tn  : switch off laser n
        M71 Tn  : switch on laser n

        M50 Tn  : read ldr sensor

    """

    def __init__(self, parent=None, serial_name='/dev/ttyUSB0', baud_rate=115200):
        self.parent = parent
        self.serial_name = serial_name
        self.baud_rate = baud_rate
        self.unplug_callback = None

        self._serial_port = None
        self._is_connected = False
        self._motor_enabled = False
        self._motor_position = 0
        self._motor_relative = 0
        self._motor_speed = 0
        self._motor_acceleration = 0
        self._motor_direction = 1
        self._laser_number = 2
        self._laser_enabled = self._laser_number * [False]
        self._tries = 0  # Check if command fails

    def connect(self):
        """Open serial port and perform handshake"""
        print ">>> Connecting board {0} {1}".format(self.serial_name, self.baud_rate)
        self._is_connected = False
        try:
            self._serial_port = serial.Serial(self.serial_name, self.baud_rate, timeout=2)
            if self._serial_port.isOpen():
                self._reset()  # Force Reset and flush
                version = self._serial_port.readline()
                if version == "Horus 0.1 ['$' for help]\r\n":
                    self.motor_speed(1)
                    self.motor_absolute(0)
                    self._serial_port.timeout = 0.05
                    self._is_connected = True
                    print ">>> Done"
                else:
                    raise WrongFirmware()
            else:
                raise BoardNotConnected()
        except:
            print "Error opening the port {0}\n".format(self.serial_name)
            self._serial_port = None
            raise BoardNotConnected()

    def disconnect(self):
        """Close serial port"""
        if self._is_connected:
            print ">>> Disconnecting board {0}".format(self.serial_name)
            try:
                if self._serial_port is not None:
                    self.lasers_off()
                    self.motor_disable()
                    self._serial_port.close()
                    del self._serial_port
            except serial.SerialException:
                print "Error closing the port {0}\n".format(self.serial_name)
                print ">>> Error"
            self._is_connected = False
            print ">>> Done"

    def set_unplug_callback(self, value):
        self.unplug_callback = value

    def motor_invert(self, value):
        if value:
            self._motor_direction = -1
        else:
            self._motor_direction = +1

    def motor_relative(self, value):
        self._motor_relative = value

    def motor_absolute(self, value):
        self._motor_relative = 0
        self._motor_position = value

    def motor_speed(self, value):
        if self._motor_speed != value:
            self._send_command("G1F{0}".format(value))
            self._motor_speed = value

    def motor_acceleration(self, value):
        if self._motor_acceleration != value:
            self._send_command("$120={0}".format(value))
            self._motor_acceleration = value

    def motor_enable(self):
        if not self._motor_enabled:
            speed = self._motor_speed
            self.motor_speed(1)
            self._send_command("M17")
            time.sleep(0.3)
            self.motor_speed(speed)
            self._motor_enabled = True

    def motor_disable(self):
        if self._motor_enabled:
            self._send_command("M18")
            self._motor_enabled = False

    def motor_move(self, nonblocking=False, callback=None):
        self._motor_position += self._motor_relative * self._motor_direction
        self.send_command("G1X{0}".format(self._motor_position), nonblocking, callback)

    def laser_on(self, index):
        if not self._laser_enabled[index]:
            if self._send_command("M71T"+str(index+1)) != '':
                self._laser_enabled[index] = True

    def laser_off(self, index):
        if self._laser_enabled[index]:
            if self._send_command("M70T"+str(index+1)) != '':
                self._laser_enabled[index] = False

    def lasers_on(self):
        for i in xrange(self._laser_number):
            self.laser_on(i)

    def lasers_off(self):
        for i in xrange(self._laser_number):
            self.laser_off(i)

    def ldr_sensor(self, pin):
        value = self._send_command("M50T" + pin, read_lines=True).split("\n")[0]
        try:
            return int(value)
        except ValueError:
            return 0

    def send_command(self, req, nonblocking=False, callback=None, read_lines=False):
        if nonblocking:
            threading.Thread(target=self._send_command, args=(req, callback, read_lines)).start()
        else:
            self._send_command(req, callback, read_lines)

    def _send_command(self, req, callback=None, read_lines=False):
        """Sends the request and returns the response"""
        ret = ''
        if self._is_connected and req != '':
            if self._serial_port is not None and self._serial_port.isOpen():
                try:
                    self._serial_port.flushInput()
                    self._serial_port.flushOutput()
                    self._serial_port.write(req + "\r\n")
                    while ret == '':  # TODO: add timeout
                        if read_lines:
                            ret = ''.join(self._serial_port.readlines())
                        else:
                            ret = ''.join(self._serial_port.readline())
                        time.sleep(0.01)
                    self._success()
                except:
                    if callback is not None:
                        callback(ret)
                    self._fail()
            else:
                self._fail()
        if callback is not None:
            callback(ret)
        return ret

    def _success(self):
        self._tries = 0

    def _fail(self):
        self._tries += 1
        if self._tries >= 1:
            self._tries = 0
            if self.unplug_callback is not None and \
               self.parent is not None and \
               not self.parent.unplugged:
                self.parent.unplugged = True
                self.unplug_callback()

    def _reset(self):
        self._serial_port.flushInput()
        self._serial_port.flushOutput()
        self._serial_port.write("\x18\r\n")  # Ctrl-x
        self._serial_port.readline()