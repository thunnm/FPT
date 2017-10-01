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
#parser.add_option("--temp", dest="temp", type="int",
#                  help="Temperature threshold", metavar=' ', default=37)

#parser.add_option("--humid", dest="humid", type="int",
#                  help="Humidity threshold", metavar=' ', default=50)

(options, args) = parser.parse_args()

# OID

batt_curr= ".1.3.6.1.4.1.21940.1.2.2.3.0"
main= ".1.3.6.1.4.1.21940.1.2.1.4.0"
rectifier= ".1.3.6.1.4.1.21940.1.2.1.5.0"
batt_breaker= ".1.3.6.1.4.1.21940.1.2.1.2.0"
spd= ".1.3.6.1.4.1.21940.1.2.1.1.0"
rec_missing= ".1.3.6.1.4.1.21940.1.2.1.50.0"
ac_phase1_lost= ".1.3.6.1.4.1.21940.1.2.1.24.0"
ac_volt_input1= ".1.3.6.1.4.1.21940.1.2.2.8.0"
ac_phase1_high= ".1.3.6.1.4.1.21940.1.2.1.19.0"

lvd1disconnectsetpoint= ".1.3.6.1.4.1.21940.1.3.4.1.0"
lvd1reconnectsetpoint= ".1.3.6.1.4.1.21940.1.3.4.2.0"
# Query SNMP

if not options.host or not options.community: 
    parser.print_help()
    sys.exit(3)
else:
        sess = netsnmp.Session(Version = 1, DestHost = options.host, Community = options.community, Timeout=1000000, Retries=1)
        var1 =  sess.get(netsnmp.VarList(batt_curr))
        var2 =  sess.get(netsnmp.VarList(main))
        var3 =  sess.get(netsnmp.VarList(rectifier))
        var4 =  sess.get(netsnmp.VarList(batt_breaker))
        var5 =  sess.get(netsnmp.VarList(spd))
        var6 =  sess.get(netsnmp.VarList(rec_missing))
        var7 =  sess.get(netsnmp.VarList(ac_phase1_lost))
        var8 =  sess.get(netsnmp.VarList(ac_volt_input1))
        var9 =  sess.get(netsnmp.VarList(ac_phase1_high))
        var10 =  sess.get(netsnmp.VarList(lvd1disconnectsetpoint))
        var11 =  sess.get(netsnmp.VarList(lvd1reconnectsetpoint))


result = var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11

#print result

status = ''
statusX = ''
#status_code 0 ung voi OK, 1 voi WARNING, 2 voi CRITICAL, 3 voi UNKNOW
status_code = 0
msg =''
crit_msg=''

batt_curr = int(result[0])
main = int(result[1])
rectifier = int(result[2])
batt_breaker = int(result[3])
spd = int(result[4])
rec_missing = int(result[5])
ac_phase1_lost = int(result[6])
ac_volt_input1 = float(result[7])
ac_phase1_high = int(result[8])

if batt_breaker >0: status = status + ' - Check Battery CB!'; status_code = 1; statusX = ' WARNING - Check power system!';
if (rectifier >0) and (ac_phase1_lost == 0) : status = status + ' - Rectifier failed!'; status_code = 1; statusX = ' WARNING - Check power system!';
if spd >0: status = status + ' - SPD failed!'; status_code = 1; statusX = ' WARNING - Check power system!';
if rec_missing >0: status = status + ' - Rectifier missing!'; status_code = 1; statusX = ' WARNING - Check power system!';
if ac_phase1_lost == 0 and ac_volt_input1 < 10: status = status + ' - Check AC Board Monitor!'; status_code = 1; statusX = ' WARNING - Check power system!';
if ac_phase1_high == 0 and ac_volt_input1 > 260: status = status + ' - Check AC Board Monitor!'; status_code = 1; statusX = ' WARNING - Check power system!';
if result[9] <> "43.00": status = status + ' - Check LVD disconnect setpoint Config!'; status_code = 1; statusX = ' WARNING - Check power system!';
if result[10] <> "48.00": status = status + ' - Check LVD reconnect setpoint Config!'; status_code = 1; statusX = ' WARNING - Check power system!';
if main >0 and ac_phase1_lost ==0: status_code = 1; statusX = ' WARNING - Check power system!';

if (status == '') and (statusX == ''): 
        status = 'OK'
else:
        status = statusX + status;

# Compose result message
msg = status
print msg
sys.exit(status_code)