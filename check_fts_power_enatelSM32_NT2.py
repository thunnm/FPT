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
ac_volt_input= ".1.3.6.1.4.1.21940.2.3.1.2.1.0"
dc_volt_output= ".1.3.6.1.4.1.21940.2.4.2.1.0"
system_curr= ".1.3.6.1.4.1.21940.2.4.2.2.0"
load_curr= ".1.3.6.1.4.1.21940.2.4.2.13.0"
batt_curr= ".1.3.6.1.4.1.21940.2.4.2.14.0"
batt_remain= ".1.3.6.1.4.1.21940.2.4.2.17.0"
Battery_Charge_Current= ".1.3.6.1.4.1.21940.2.5.2.4.0" #Current charge batt
batt_temp= ".1.3.6.1.4.1.21940.2.4.2.15.0"
LVD_Disconnect= ".1.3.6.1.4.1.21940.2.5.4.5.1.0" 
LVD_Reconnect= ".1.3.6.1.4.1.21940.2.5.4.5.2.0" 
Rectnumber= ".1.3.6.1.4.1.21940.2.5.3.3.0"
Battery_Type= ".1.3.6.1.4.1.21940.2.5.7.1.0"

# Query SNMP

if not options.host or not options.community: 
    parser.print_help()
    sys.exit(3)
else:
        sess = netsnmp.Session(Version = 1, DestHost = options.host, Community = options.community, Timeout=1000000, Retries=3)
        var1 =  sess.get(netsnmp.VarList(ac_volt_input))
        var2 =  sess.get(netsnmp.VarList(dc_volt_output))
        var3 =  sess.get(netsnmp.VarList(system_curr))
        var4 =  sess.get(netsnmp.VarList(load_curr))
        var5 =  sess.get(netsnmp.VarList(batt_curr))
        var6 =  sess.get(netsnmp.VarList(batt_remain))
        var7 =  sess.get(netsnmp.VarList(Battery_Charge_Current))
        var8 =  sess.get(netsnmp.VarList(batt_temp))
        var9 =  sess.get(netsnmp.VarList(LVD_Disconnect))
        var10 =  sess.get(netsnmp.VarList(LVD_Reconnect))
        var11 =  sess.get(netsnmp.VarList(Rectnumber))
        var12 =  sess.get(netsnmp.VarList(Battery_Type))

result = var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12

if result[0] == None:
        print 'UNKNOW: Host not responding to SNMP request or wrong frimware version !'
        sys.exit(3)

#print result

status = ''
#status_code 0 ung voi OK, 1 voi WARNING, 2 voi CRITICAL, 3 voi UNKNOW
status_code = 0
msg =''

ac_volt_input = float(result[0])/1000
dc_volt_output = float(result[1])/1000
system_curr = float(result[2])/1000
load_curr = float(result[3])/1000
if result[4] <> None:
        batt_curr = float(result[4])/1000
else:
        batt_curr = 0
batt_remain = float(result[5])/10
Battery_Charge_Current = int(result[6])
batt_temp = float(result[7])/10
LVD_Disconnect = int(result[8])/1000
LVD_Reconnect = int(result[9])/1000 
Rectnumber = int(result[10]) 
Battery_Type = int(result[11])/10

if ac_volt_input >= 3276:
        if batt_curr >= 0:
                ac_volt_input= 220
        else:
                ac_volt_input= 0

if ac_volt_input >= 260: status = status + ' AC-input= ' + str(ac_volt_input); 
if dc_volt_output <= 46: status = status + ' DC-output= ' + str(dc_volt_output); 
if dc_volt_output > 54.5: status = status + ' DC-output= ' + str(dc_volt_output); 
if system_curr >= 90: status = status + ' System-curr= ' + str(system_curr); 
if load_curr >=60: status = status + ' Load-curr= ' + str(load_curr); 
if batt_curr >= 40: status = status + ' Batt-curr= ' + str(batt_curr); 
if batt_remain <= 40: status = status + ' Batt-remain=' + str(batt_remain); 
if batt_temp >= 45: status = status + ' Batt-Temp=' + str(batt_temp);
if Battery_Charge_Current > 10 : status = status + ' - Battery-Charge-Current = '+ str(Battery_Charge_Current);  
if Battery_Charge_Current < 5: status = status + ' - Battery-Charge-Current = ' + str(Battery_Charge_Current); 
if LVD_Reconnect != 48 : status = status + ' - LVD-reconnect-setpoint = ' + str(LVD_Reconnect);
if LVD_Disconnect != 43 : status = status + ' - LVD-disconnect-setpoint = ' + str(LVD_Disconnect);
if status == '':
    status = '. ===> OK'; status_code = 0
else:
    status = '. ===> WARNING:' + status; status_code = 1

# Compose result message
msg = 'AC-input=' + str(ac_volt_input) + ', DC-output=' + str(dc_volt_output) + ', System-curr=' + str(system_curr) + ', Load-curr=' + str(load_curr) + ', Batt-curr=' + str(batt_curr) + ', Batt-remain=' + str(batt_remain) + ', Batt-curr-limit=' + str(Battery_Charge_Current) + ', Batt-Temp=' + str(batt_temp) + ', Rectnumber=' + str(Rectnumber) + ', Battery_Type=' + str(Battery_Type)  + status

print msg
sys.exit(status_code)
