#!/usr/bin/python

from optparse import OptionParser
import netsnmp
import string
import sys
import httplib
import os

#sys.exit(0)
# Parsing argurments
parser = OptionParser()
parser.add_option("-H", dest="host", type="string",
                  help="Hostname/IP Address of device", metavar=' ')

parser.add_option("-c", dest="community", type="string",
                  help="Community string", metavar=' ')

parser.add_option("-t", dest="hostname", type="string",
                  help="Host name", metavar=' ', default='HCMPxxx')

(options, args) = parser.parse_args()

# OID
AC_Volt_Input= ".1.3.6.1.4.1.21940.2.3.1.2.1.0"
DC_Volt_Output= ".1.3.6.1.4.1.21940.2.4.2.1.0"
Batt_Curr= ".1.3.6.1.4.1.21940.2.4.2.14.0"
Batt_Remain= ".1.3.6.1.4.1.21940.2.4.2.17.0"
AC_Alarm= ".1.3.6.1.4.1.21940.2.11.10.0"
# AC_Alarm
# 1-AC Voltage High, 
# 2-AC Voltage Low,
# 3-AC Phase Lost,
# 4-AC Current High,
# 5-AC Frequency High
# 6-AC Frequency Low
Alarm_Relay= ".1.3.6.1.4.1.21940.2.11.1.0"
# 8-GPIP4
# 16-GPIP5
# 32-GPIP6
# 64-MCB
Battery_Status =         ".1.3.6.1.4.1.21940.2.11.9.0"  
        # 1-Power Save Active,
        # 8-Fast Charge
        # 16-Battery Test


# Query SNMP

if not options.host or not options.community: 
        parser.print_help()
        sys.exit(3)
else:
        sess = netsnmp.Session(Version = 1, DestHost = options.host, Community = options.community, Timeout=1000000, Retries=1)
        Var1 =  sess.get(netsnmp.VarList(AC_Volt_Input))
        Var2 =  sess.get(netsnmp.VarList(DC_Volt_Output))
        Var3 =  sess.get(netsnmp.VarList(Batt_Curr))
        Var4 =  sess.get(netsnmp.VarList(Batt_Remain))
        Var5 =  sess.get(netsnmp.VarList(AC_Alarm))
        Var6 =  sess.get(netsnmp.VarList(Alarm_Relay))
        Var7 =  sess.get(netsnmp.VarList(Battery_Status))
        result =  Var1 + Var2 + Var3 + Var4 + Var5 + Var6 + Var7

if result[4] == None:
        print 'UNKNOW: Host not responding to SNMP request or wrong frimware version !'
        sys.exit(3)

status = ''

status_code = 0
msg =''
crit_msg=''

AC_Volt_Input = float(result[0])/1000
DC_Volt_Output = float(result[1])/1000
Batt_Curr = float(result[2])/1000
Batt_Remain = float(result[3])/10
AC_Alarm = int(result[4])
Alarm_Relay = int(result[5])
Battery_Status = int(result[6])

if ((AC_Volt_Input) >= 3276):
        if AC_Alarm & 0:
                AC_Volt_Input= 220
        else:
                AC_Volt_Input= 0

# AC_Alarm
# 0-none alarm
# 1-AC Voltage High, 
# 2-AC Voltage Low,
# 4-AC Phase Lost,
# 8-AC Current High,
# 16-AC Frequency High
# 32-AC Frequency Low

# 8-GPIP4
# 16-GPIP5
# 64-MCB
if (AC_Alarm & 4): 
        status = status + 'CUP DIEN - CHAY BINH'
        status_code = 2
        conn = httplib.HTTPConnection("powersupply.fpt.vn")
        conn.request("GET", "/WebService.asmx/GetStatusMonitorGeneratior?status=2&POP=" + options.hostname)
else :
        if Battery_Status & 16 :  
                        status = status + ' - Battery-Test !'
                        status_code = 1 
        if (Alarm_Relay & 0):
                        status = status + 'DANG CO DIEN LUOI AC'
                        status_code = 0
                        conn = httplib.HTTPConnection("powersupply.fpt.vn")
                        conn.request("GET", "/WebService.asmx/GetStatusMonitorGeneratior?status=0&POP=" + options.hostname)
        if (Alarm_Relay & 16): # 
                        status = status + 'DANG CO DIEN LUOI-DANG CHAY MAY PHAT'
                        status_code = 1
                        conn = httplib.HTTPConnection("powersupply.fpt.vn")
                        conn.request("GET", "/WebService.asmx/GetStatusMonitorGeneratior?status=3&POP=" + options.hostname)
        if (Alarm_Relay & 24): #(relay_ac == '1')
                        status = status + 'CUP DIEN-DANG CHAY MAY PHAT'
                        status_code = 1
                        conn = httplib.HTTPConnection("powersupply.fpt.vn")
                        conn.request("GET", "/WebService.asmx/GetStatusMonitorGeneratior?status=1&POP=" + options.hostname)

msg = status + ' - AC-input=' + str(AC_Volt_Input) + ', DC-output=' + str(DC_Volt_Output) + ', Batt-curr=' + str(Batt_Curr) + ', Batt-remain=' + str(Batt_Remain)

print msg
sys.exit(status_code)

#truyen du lieu qua inside :
#CUP DIEN - CHAY BINH -> 2
#DANG CO DIEN LUOI AC -> 0
#DANG CO DIEN LUOI-DANG CHAY MAY PHAT ->3
#CUP DIEN-DANG CHAY MAY PHAT -> 1
#Replay_AC hong