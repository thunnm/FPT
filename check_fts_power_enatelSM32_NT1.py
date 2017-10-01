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
                 help="Host name", metavar=' ', default='HCMPABC')

(options, args) = parser.parse_args()

# OID
Ac_Volt_Input= ".1.3.6.1.4.1.21940.2.3.1.2.1.0"
Dc_Volt_Output= ".1.3.6.1.4.1.21940.2.4.2.1.0"
System_Curr= ".1.3.6.1.4.1.21940.2.4.2.2.0"
Load_Curr= ".1.3.6.1.4.1.21940.2.4.2.13.0"
Batt_Curr= ".1.3.6.1.4.1.21940.2.4.2.14.0"
Batt_Remain= ".1.3.6.1.4.1.21940.2.4.2.17.0"
#Battery_Charge_Current= ".1.3.6.1.4.1.21940.2.5.2.4.0" #NOT
Batt_Temp= ".1.3.6.1.4.1.21940.2.4.2.15.0"
LVD_Disconnect= ".1.3.6.1.4.1.21940.2.5.4.5.1.0" 
LVD_Reconnect= ".1.3.6.1.4.1.21940.2.5.4.5.2.0" 

# Query SNMP

if not options.host or not options.community: 
    parser.print_help()
    sys.exit(3)
else:
        sess = netsnmp.Session(Version = 1, DestHost = options.host, Community = options.community, Timeout=1000000, Retries=3)
        var1 =  sess.get(netsnmp.VarList(Ac_Volt_Input))
        var2 =  sess.get(netsnmp.VarList(Dc_Volt_Output))
        var3 =  sess.get(netsnmp.VarList(System_Curr))
        var4 =  sess.get(netsnmp.VarList(Load_Curr))
        var5 =  sess.get(netsnmp.VarList(Batt_Curr))
        var6 =  sess.get(netsnmp.VarList(Batt_Remain))
        var7 =  sess.get(netsnmp.VarList(Batt_Temp))
        var8 =  sess.get(netsnmp.VarList(LVD_Disconnect))
        var9 =  sess.get(netsnmp.VarList(LVD_Reconnect))

result = var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9

if result[0] == None:
        print 'UNKNOW: Host not responding to SNMP request or wrong frimware version !'
        sys.exit(3)

#print result

status = ''
#status_code 0 ung voi OK, 1 voi WARNING, 2 voi CRITICAL, 3 voi UNKNOW
status_code = 0
msg =''

Ac_Volt_Input = float(result[0])/1000
Dc_Volt_Output = float(result[1])/1000
System_Curr = float(result[2])/1000
Load_Curr = float(result[3])/1000
if result[4] <> None:
        Batt_Curr = float(result[4])/1000
else:
        Batt_Curr = 0
Batt_Remain = float(result[5])/10
Batt_Temp = float(result[6])/10
LVD_Disconnect = int(result[7])/1000
LVD_Reconnect = int(result[8])/1000 

if Ac_Volt_Input >= 3276:
        if Batt_Curr >= 0:
                Ac_Volt_Input= 220
        else:
                Ac_Volt_Input= 0

if Ac_Volt_Input >= 260: status = status + ' AC-input= ' + str(Ac_Volt_Input); 
if Dc_Volt_Output <= 46: status = status + ' DC-output= ' + str(Dc_Volt_Output); 
if Dc_Volt_Output > 54.5: status = status + ' DC-output= ' + str(Dc_Volt_Output); 
if System_Curr >= 90: status = status + ' System-curr= ' + str(System_Curr); 
if Load_Curr >=60: status = status + ' Load-curr= ' + str(Load_Curr); 
if Batt_Curr >= 40: status = status + ' Batt-curr= ' + str(Batt_Curr); 
if Batt_Remain <= 40: status = status + ' Batt-remain=' + str(Batt_Remain); 
if Batt_Temp >= 45: status = status + ' Batt-Temp=' + str(Batt_Temp);
if LVD_Reconnect != 48 : status = status + ' - LVD-reconnect-setpoint = ' + str(LVD_Reconnect);
if LVD_Disconnect != 43 : status = status + ' - LVD-disconnect-setpoint = ' + str(LVD_Disconnect);
if status == '':
    status = '. ===> OK'; status_code = 0
else:
    status = '. ===> WARNING:' + status; status_code = 1

# Compose result message
msg = 'AC-input=' + str(Ac_Volt_Input) + ', DC-output=' + str(Dc_Volt_Output) + ', System-curr=' + str(System_Curr) + ', Load-curr=' + str(Load_Curr) + ', Batt-curr=' + str(Batt_Curr) + ', Batt-remain=' + str(Batt_Remain) + ', Batt-Temp=' + str(Batt_Temp) + status

print msg
sys.exit(status_code)