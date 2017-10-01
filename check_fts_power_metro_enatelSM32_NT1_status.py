#!/usr/bin/python

from optparse import OptionParser
import netsnmp
import string
import sys

# Parsing argurments
parser = OptionParser()
parser.add_option("-H", dest="host", type="string",
                  help="Hostname/IP Address of device", metavar=' ')

parser.add_option("-c", dest="community", type="string",
                  help="Community string", metavar=' ')
                                  
parser.add_option("-t", dest="hostname", type="string",
                 help="Host name", metavar=' ', default='HCMPTEST')

(options, args) = parser.parse_args()

# OID
AC_Alarm=                  ".1.3.6.1.4.1.21940.2.11.10.0" 
        # 1-AC Voltage High, 
        # 2-AC Voltage Low,
        # 3-AC Phase Lost,
        # 4-AC Current High,
        # 5-AC Frequency High
        # 6-AC Frequency Low
Load_Curr=                 ".1.3.6.1.4.1.21940.2.4.2.13.0"
Battery_Alarm =            ".1.3.6.1.4.1.21940.2.11.8.0" 
        # 1-System Load Current High,
        # 64-Battery Temperature HigH,
        # 128-Battery Temperature High,
        # 256-Battery Temperature Sensor Fault
        # 4096-attery MCB 1 open
        # 8192-Battery MCB 2 open
Alarm_relay=             ".1.3.6.1.4.1.21940.2.11.1.0"
        # 8-GPIP4
        # 16-GPIP5
        # 32-GPIP6
        # 64-MCB
# OID Batt
Battery_Status =         ".1.3.6.1.4.1.21940.2.11.9.0"  
        # 1-Power Save Active,
        # 8-Fast Charge
        # 16-Battery Test
        # 32-Battery Discharge
        # 64-Battery Test Fail
        # 1024-LVD Fail
Batt_Curr=                 ".1.3.6.1.4.1.21940.2.4.2.14.0"
Batt_Main=                 ".1.3.6.1.4.1.21940.2.4.2.17.0"
Rectifier=                 ".1.3.6.1.4.1.21940.2.11.3.0" 
        # 4-Rectifier Over Temperature
        # 8-Rectifier Fan Fail
        # 16-Rectifier Current Limit
        # 32-Rectifier Over Voltage
        # 64-Rectifier Brownout
        # 128-Rectifier Postmate
        # 512-Rectifier Temperature Sense Fail
        # 8192-Rectifier Shutdown
        # 16384-Rectifier EEPROM Fail
        # 32768-Rectifier Soft Starting
Rectifier_Lost=                 ".1.3.6.1.4.1.21940.2.11.6.0"
	# 1-Rectifier Non-Urgent Fail
	# 2-Rectifier Urgent Fail
	# 4-All Rectifiers Failed
	# 8-Urgent Rectifier Missing
	# 16-Non-Urgent Rectifier Missing
# OID LVD
LVD_Disconnect=            ".1.3.6.1.4.1.21940.2.5.4.5.1.0" 
LVD_Reconnect=             ".1.3.6.1.4.1.21940.2.5.4.5.2.0" 
# OID DC
DC_Alarm=                  ".1.3.6.1.4.1.21940.2.11.7.0"  
        # 1-Low Voltage Bus 1
        # 2-Low Float Bus 1
        # 4-High Voltage Bus 1
        # 8-High Float Bus 1
        # 256-LVD 1 Operate
        # 512-LVD 2 Operate
        # 2048-LVD 3 Operate

# Query SNMP

if not options.host or not options.community: 
    parser.print_help()
    sys.exit(3)
else :
	sess = netsnmp.Session(Version = 1, DestHost = options.host, Community = options.community, Timeout=1000000, Retries=1)
	var1 =  sess.get(netsnmp.VarList(Battery_Alarm))                        #0
	var2 =  sess.get(netsnmp.VarList(Alarm_relay))                          #1
	var3 =  sess.get(netsnmp.VarList(Battery_Status))               #2
	var4 =  sess.get(netsnmp.VarList(Batt_Curr))                    #3
	var5 =  sess.get(netsnmp.VarList(Batt_Main))                            #4
	var6 =  sess.get(netsnmp.VarList(Rectifier))                            #5
	var7 =  sess.get(netsnmp.VarList(LVD_Disconnect))               #6
	var8 =  sess.get(netsnmp.VarList(DC_Alarm))                     #7
	var9 =  sess.get(netsnmp.VarList(Load_Curr))                    #8
	var10 =  sess.get(netsnmp.VarList(LVD_Reconnect))               #9
	var11 =  sess.get(netsnmp.VarList(AC_Alarm))
	var12 =  sess.get(netsnmp.VarList(Rectifier_Lost))                      #11

result = var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12

if result[0] == None:
        print 'UNKNOW: Host not responding to SNMP request or wrong frimware version !'
        sys.exit(3)

#print result

status = ''
statusX = ''
#status_code 0 ung voi OK, 1 voi WARNING, 2 voi CRITICAL, 3 voi UNKNOW
status_code = 0
msg =''
crit_msg=''

Battery_Alarm = int(result[0])
Alarm_relay = int(result[1])
Battery_Status = int(result[2])
Batt_Curr = float(result[3])
Batt_Main = int(result[4])/10
Rectifier = int(result[5])
LVD_Disconnect = int(result[6])/1000
DC_Alarm = int(result[7])
Load_Curr = float(result[8])/1000
LVD_Reconnect = int(result[9])/1000
AC_Alarm = int(result[10])
Rectifier_Lost = int(result[11])

# AC_Alarm
# 1-AC Voltage High, 
# 2-AC Voltage Low,
# 3-AC Phase Lost,
# 4-AC Current High,
# 5-AC Frequency High
# 6-AC Frequency Low
if AC_Alarm == 1 : status = status + ' - AC-Voltage-High !'; status_code = 1;
if AC_Alarm == 2 : status = status + ' - AC-Voltage-Low !'; status_code = 1;
if AC_Alarm == 4 : status = status + ' - AC-Current-High !'; status_code = 1;
if AC_Alarm == 5 : status = status + ' - AC-Frequency-High !'; status_code = 1;
if AC_Alarm == 6 : status = status + ' - AC-Frequency-Low !'; status_code = 1;

# Battery_Alarm
# 1-System Load Current High,
# 64-Battery Temperature HigH,
# 128-Battery Temperature High,
# 256-Battery Temperature Sensor Fault
# 4096-attery MCB 1 open
# 8192-Battery MCB 2 open
if Battery_Alarm & 1 : status = status + ' - System-Load-Current-High !'; status_code = 1;
if Battery_Alarm & 64 : status = status + ' - Battery-Temperature-Low!'; status_code = 1;
if Battery_Alarm & 128 : status = status + ' - Battery-Temperature-High!'; status_code = 1;
if Battery_Alarm & 256 : status = status + ' - Battery-Temperature-Sensor-Fault!'; status_code = 1;
if Battery_Alarm & 4096 : status = status + ' - Check-Battery-CB1!'; status_code = 1; 
if Battery_Alarm & 8192 : status = status + ' - Check-Battery-CB2!'; status_code = 1; 

if Alarm_relay & 64: status = status + ' - Check-MCB-Load!'; status_code = 1; 

# Battery_Status
# 1-Power Save Active,
# 8-Fast Charge
# 16-Battery Test
# 32-Battery Discharge
# 64-Battery Test Fail
# 1024-LVD Fail
if Battery_Status & 1 : status = status + ' - Power-Save-Active !'; status_code = 1;
if Battery_Status & 8 : status = status + ' - Battery-Fast-Charge !'; status_code = 1;
if Battery_Status & 32 and AC_Alarm <> 3 : status = status + ' - Batterydischarge !'; status_code = 1;
if Battery_Status & 64 : status = status + ' - Battery-Test-Fail !'; status_code = 1;
if Battery_Status & 1024 : status = status + ' - LVD-Fail!'; status_code = 1;

# Rectifier
# 4-Rectifier Over Temperature
# 8-Rectifier Fan Fail
# 16-Rectifier Current Limit
# 32-Rectifier Over Voltage
# 64-Rectifier Brownout
# 128-Rectifier Postmate
# 512-Rectifier Temperature Sense Fail
# 8192-Rectifier Shutdown
# 16384-Rectifier EEPROM Fail
# 32768-Rectifier Soft Starting
if (Rectifier & 4 ) and ( AC_Alarm <> 3 ): status = status + ' - Rectifier-Over-Temperature!'; status_code = 1;
if (Rectifier & 8 ) and ( AC_Alarm <> 3 ) : status = status + ' - Rectifier-Fan-Fail!'; status_code = 1;
if (Rectifier & 16 ) and ( AC_Alarm <> 3 ) : status = status + ' - Rectifier-Current-Limit !'; status_code = 1;
if (Rectifier & 32 ) and ( AC_Alarm <> 3 ) : status = status + ' - Rectifier-Over-Voltage!'; status_code = 1;
if (Rectifier & 64 ) and ( AC_Alarm <> 3 ) : status = status + ' - Rectifier-Brownout !'; status_code = 1;
if (Rectifier & 128 ) and ( AC_Alarm <> 3 ) : status = status + ' - Rectifier-Postmate !'; status_code = 1;
if (Rectifier & 512 ) and ( AC_Alarm <> 3 ) : status = status + ' - Rectifier-Temperature-Sense-Fail !'; status_code = 1;
if (Rectifier & 8192 ) and ( AC_Alarm <> 3 ) : status = status + ' - Rectifier-Shutdown !'; status_code = 1;
if (Rectifier & 16384 ) and ( AC_Alarm <> 3 ) : status = status + ' - Rectifier-EEPROM-Fail !'; status_code = 1;
if (Rectifier & 32768 ) and ( AC_Alarm <> 3 ) : status = status + ' - Rectifier-Soft-Starting !'; status_code = 1;

# Rectifier_Lost
# 1-Rectifier Non-Urgent Fail
# 2-Rectifier Urgent Fail
# 4-All Rectifiers Failed
# 8-Urgent Rectifier Missing
# 16-Non-Urgent Rectifier Missing
if (Rectifier_Lost & 1 ) and (AC_Alarm & 4) == 0: status = status + ' - Rectifier Non-Urgent Fail !'; status_code = 1;
if (Rectifier_Lost & 2 ) and (AC_Alarm & 4) == 0: status = status + ' - Rectifier Urgent Fail !'; status_code = 1;
if (Rectifier_Lost & 4 ) and (AC_Alarm & 4) == 0: status = status + ' - All Rectifiers Failed!'; status_code = 1;
if (Rectifier_Lost & 8 ) and (AC_Alarm & 4) == 0: status = status + ' - Urgent Rectifier Missing!'; status_code = 1;
if (Rectifier_Lost & 16 ) and (AC_Alarm & 4) == 0: status = status + ' - Non-Urgent Rectifier Missing !'; status_code = 1;

# DC_Alarm
# 1-Low Voltage Bus 1
# 2-Low Float Bus 1
# 4-High Voltage Bus 1
# 8-High Float Bus 1
# 256-LVD 1 Operate
# 512-LVD 2 Operate
# 2048-LVD 3 Operate
if DC_Alarm & 1 and ( AC_Alarm <> 3 ) : status = status + ' - DC-Low-Voltage-Bus-1 !'; status_code = 1;
if DC_Alarm & 2 and ( AC_Alarm <> 3 ) : status = status + ' - DC-Low-Float-Bus-1 !'; status_code = 1;
if DC_Alarm & 4 and ( AC_Alarm <> 3 ) : status = status + ' - DC-High-Voltage-Bus-1 !'; status_code = 1;
if DC_Alarm & 8 and ( AC_Alarm <> 3 ) : status = status + ' - DC-High-Float-Bus-1 ! '; status_code = 1;
if DC_Alarm & 256 : status = status + ' - LVD-1-Openrate !'; status_code = 1;
if DC_Alarm & 512 : status = status + ' - LVD-2-Openrate !'; status_code = 1;
if DC_Alarm & 2048 : status = status + ' - LVD-3-Openrate !'; status_code = 1;


if LVD_Reconnect <> 48 : status = status + ' - LVD-reconnect-Fail!'; status_code = 1;
if LVD_Disconnect <> 43 : status = status + ' - LVD-disconnect-Fail!'; status_code = 1;

if status_code == 2:
        status = 'CRITICAL - ' + status
elif status_code == 1:
        status = 'WARNING - ' + status
else:
        status = 'OK'

# Compose result message
msg = status
print msg
sys.exit(status_code)