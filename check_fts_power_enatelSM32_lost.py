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
ac_volt_input= ".1.3.6.1.4.1.21940.2.3.1.2.1.0"
dc_volt_output= ".1.3.6.1.4.1.21940.2.4.2.1.0"
#batt_curr= ".1.3.6.1.4.1.21940.2.4.2.14.0"
batt_curr= ".1.3.6.1.4.1.21940.2.4.1.14.0"
batt_remain= ".1.3.6.1.4.1.21940.2.4.2.17.0"
#batt_curr_limit= ".1.3.6.1.4.1.21940.2.4.2.15.0"
acphaselost= ".1.3.6.1.4.1.21940.2.2.11.2"
alarm_input4= ".1.3.6.1.4.1.21940.2.2.2.3"
alarm_input5= ".1.3.6.1.4.1.21940.2.2.2.4"
batt_test = ".1.3.6.1.4.1.21940.2.2.10.4"


# Query SNMP

if not options.host or not options.community: 
        parser.print_help()
        sys.exit(3)
else:
        sess = netsnmp.Session(Version = 1, DestHost = options.host, Community = options.community, Timeout=1000000, Retries=1)
        Var1 =  sess.get(netsnmp.VarList(ac_volt_input))
        Var2 =  sess.get(netsnmp.VarList(dc_volt_output))
        Var3 =  sess.get(netsnmp.VarList(batt_curr))
        Var4 =  sess.get(netsnmp.VarList(batt_remain))
        Var5 =  sess.get(netsnmp.VarList(acphaselost))
        Var6 =  sess.get(netsnmp.VarList(alarm_input4))
        Var7 =  sess.get(netsnmp.VarList(alarm_input5))
        Var8 =  sess.get(netsnmp.VarList(batt_test))                         
        result =  Var1 + Var2 + Var3 + Var4 + Var5 + Var6 + Var7 + Var8

if result[4] == None:
        print 'UNKNOW: Host not responding to SNMP request or wrong frimware version !'
        sys.exit(3)

status = ''

status_code = 0
msg =''
crit_msg=''

ac_volt_input = float(result[0])/1000
dc_volt_output = float(result[1])/1000
batt_curr = int(result[2])
acphaselost = int(result[4])
relay_ac = result[5];
relay_mpd = result[6];

#Kiem tra dien luoi
if ((ac_volt_input) >= 3276):
        if acphaselost == 0:
                ac_volt_input= 220
        else:
                ac_volt_input= 0

if (acphaselost == 1): 
        status = status + 'CUP DIEN - CHAY BINH'
        status_code = 2
        conn = httplib.HTTPConnection("powersupply.fpt.vn")
        conn.request("GET", "/WebService.asmx/GetStatusMonitorGeneratior?status=2&POP=" + options.hostname)
elif (acphaselost == 0):
        if int(result[7]) >0: 
                status = status + ' - Battery_Test !'
                status_code = 1
        else:
                if (relay_ac == '0'):
                        if (relay_mpd == '0'):
                                status = status + 'DANG CO DIEN LUOI AC'
                                status_code = 0
                                conn = httplib.HTTPConnection("powersupply.fpt.vn")
                                conn.request("GET", "/WebService.asmx/GetStatusMonitorGeneratior?status=0&POP=" + options.hostname)
                        else : # (relay_mpd == '1')
                                status = status + 'DANG CO DIEN LUOI-DANG CHAY MAY PHAT'
                                status_code = 1
                                conn = httplib.HTTPConnection("powersupply.fpt.vn")
                                conn.request("GET", "/WebService.asmx/GetStatusMonitorGeneratior?status=3&POP=" + options.hostname)
                else : #(relay_ac == '1')
                        if (relay_mpd == '1'):
                                status = status + 'CUP DIEN-DANG CHAY MAY PHAT'
                                status_code = 1
                                conn = httplib.HTTPConnection("powersupply.fpt.vn")
                                conn.request("GET", "/WebService.asmx/GetStatusMonitorGeneratior?status=1&POP=" + options.hostname)
                        else : #(relay_mpd == '0')
                                status = status + 'Relay_AC hong'
                                status_code = 1
else:
        status = status + 'truong hop khac-kiem tra lai cac relay,nguon'
        status_code = 1




msg = status + ' - AC-input=' + str(ac_volt_input) + ', DC-output=' + str(dc_volt_output) + ', Batt-curr=' + str(batt_curr) + ', Batt-remain=' + result[3]

print msg
sys.exit(status_code)

#truyen du lieu qua inside :
#CUP DIEN - CHAY BINH -> 2
#DANG CO DIEN LUOI AC -> 0
#DANG CO DIEN LUOI-DANG CHAY MAY PHAT ->3
#CUP DIEN-DANG CHAY MAY PHAT -> 1
#Replay_AC hong