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

batt_curr= ".1.3.6.1.4.1.21940.2.4.1.14.0"
main= ".1.3.6.1.4.1.21940.2.2.11.2"
rectifier= ".1.3.6.1.4.1.21940.2.2.4.0"
MCBLoad= ".1.3.6.1.4.1.21940.2.2.2.6"
batt_temp_fault= ".1.3.6.1.4.1.21940.2.2.9.8"
fastcharge= ".1.3.6.1.4.1.21940.2.2.10.3"
MCB1= ".1.3.6.1.4.1.21940.2.2.9.12"
MCB2= ".1.3.6.1.4.1.21940.2.2.9.13"
acphaselost= ".1.3.6.1.4.1.21940.2.2.11.2"
peripheralcommsfaile= ".1.3.6.1.4.1.21940.2.2.10.9"
rec_temp= ".1.3.6.1.4.1.21940.2.2.4.2"
rec_fan= ".1.3.6.1.4.1.21940.2.2.4.3"

Urgent_Rectifier_Fail = ".1.3.6.1.4.1.21940.2.2.7.1"
rectifierpostmate = ".1.3.6.1.4.1.21940.2.2.4.7"
rectcommsfail = ".1.3.6.1.4.1.21940.2.2.7.3"
batterydischarge = ".1.3.6.1.4.1.21940.2.2.10.5"
lvd1operate = ".1.3.6.1.4.1.21940.2.2.8.8"
lvdfail = ".1.3.6.1.4.1.21940.2.2.10.10"
batt_test_fail = ".1.3.6.1.4.1.21940.2.2.10.6"

# Query SNMP

if not options.host or not options.community: 
    parser.print_help()
    sys.exit(3)
else:
	sess = netsnmp.Session(Version = 1, DestHost = options.host, Community = options.community, Timeout=1000000, Retries=1)
	var1 =  sess.get(netsnmp.VarList(batt_curr)) #0
	var2 =  sess.get(netsnmp.VarList(main))      #1
	var3 =  sess.get(netsnmp.VarList(rectifier)) #2
	var4 =  sess.get(netsnmp.VarList(MCBLoad))   #3
	var5 =  sess.get(netsnmp.VarList(batt_temp_fault))  #4
	var6 =  sess.get(netsnmp.VarList(fastcharge))       #5
	var7 =  sess.get(netsnmp.VarList(MCB1))             #6
	var8 =  sess.get(netsnmp.VarList(MCB2))             #7
	var9 =  sess.get(netsnmp.VarList(acphaselost))      #8
	var10 =  sess.get(netsnmp.VarList(peripheralcommsfaile))  #9
	var11 =  sess.get(netsnmp.VarList(rec_temp))              #10
	var12 =  sess.get(netsnmp.VarList(rec_fan))               #11
	var13 =  sess.get(netsnmp.VarList(Urgent_Rectifier_Fail)) #12
	var14 =  sess.get(netsnmp.VarList(rectifierpostmate))     #13 
	var15 =  sess.get(netsnmp.VarList(rectcommsfail))         #14 
	var16 =  sess.get(netsnmp.VarList(batterydischarge))      #15
	var17 =  sess.get(netsnmp.VarList(lvd1operate))           #16
	var18 =  sess.get(netsnmp.VarList(lvdfail))           	  #17
	var19 =  sess.get(netsnmp.VarList(batt_test_fail)) 		  #18

result = var1 + var2 + var3 + var4 + var5 + var6 + var7 + var8 + var9 + var10 + var11 + var12 + var13 + var14 + var15 + var16 + var17 + var18 + var19 

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

batt_curr = int(result[0])
main = int(result[1])
rectifier = float(result[2])
MCBLoad = float(result[3])
batt_temp_fault = int(result[4])
fastcharge = int(result[5])
acphaselost = int(result[8])

if MCBLoad >0: status = status + ' - Check MCB Load!'; status_code = 1; # statusX = 'CRITICAL - Check power system!';
if int(result[6]) >0: status = status + ' - Check Battery CB1!'; status_code = 1; # statusX = 'CRITICAL - Check power system!';
if int(result[7]) >0: status = status + ' - Check Battery CB2!'; status_code = 1; # statusX = 'CRITICAL - Check power system!';
if (rectifier >0) and (acphaselost == 0): status = status + ' - Rectifier failed!'; status_code = 1; # statusX = 'CRITICAL - Check power system!';
if batt_temp_fault >0: status = status + ' - Battery Temperature Fault!'; status_code = 1; # statusX = 'CRITICAL - Check power system!';
if (int(result[9]) >0) and (acphaselost == 0): status = status + ' - Peripheral Device Comms Fail!'; status_code = 1;
if int(result[10]) >0: status = status + ' - Rec_Temperature!'; status_code = 1;
if int(result[11]) >0: status = status + ' - Rec_Fan Fault!'; status_code = 1;
if (int(result[12]) >0) and (acphaselost == 0): status = status + ' - Urgent_Rectifier_Fail !'; status_code = 1;
if (int(result[13]) >0) and (acphaselost == 0): status = status + ' - rectifierpostmate !'; status_code = 1;
if (int(result[14]) >0) and (acphaselost == 0): status = status + ' - rectcommsfail !'; status_code = 1;
if (int(result[15]) >0) and (acphaselost == 0): status = status + ' - batterydischarge !'; status_code = 1;
if int(result[16]) >0: status = status + ' - lvd1operate !'; status_code = 1;
if int(result[17]) >0: status = status + ' - LVD_fail !'; status_code = 1;
if int(result[18]) >0: status = status + ' - Battery_Test_Fail !'; status_code = 1;
if main >0: status_code = 1; # statusX = 'CRITICAL - Check power system!';



if status_code == 2:
        status = 'CRITICAL - Check power system!' + status
elif status_code == 1:
        status = 'WARNING - Check power system!' + status
else:
        status = 'OK'

# Compose result message
msg = status
print msg
sys.exit(status_code)