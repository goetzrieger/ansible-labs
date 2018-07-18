#!/usr/bin/python2
#
# initial version by Christian Jung
#
# get the list of GUID's used in Ravello
# write a lab list adoc file and an Ansible inventory
#
# Usage:
# Change user name and app pattern (should match your Ravello apps as regex)
# Run
# 
# To check if all apps are up and accessible by SSH:
# ANSIBLE_HOST_KEY_CHECKING=False ansible all -i lab_list.inventory -m ping -u lab-user --key-file=id_rsa -o
#
# If SSH password auth is used swap --key-file to --ask-pass

import sys
import getopt
import getpass
import os
import requests
import re
import json

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser  # ver. < 3.0

def usage():
    """ print usage information
    """
    print "Usage:"
    print "-u username"
    print "-p password"
   
try:
    opts, args = getopt.getopt(sys.argv[1:], "u:p:")
except getopt.GetoptError as err:
    # print help information and exit:
    print str("Unknown option")  # will print something like "option -a not recognized"
    usage()
    sys.exit(2)

username = '<identity domain>/<Ravello username>'
password = None
# pattern to filter the app, e.g.:
apppattern = 'EMEA-SA-RHPDS-DEM-account-SUMMIT-L1086'

for o, a in opts:
    if o == "-u":
        username = a
    elif o == "-p":
        password  = a
    else:
        print "unhandled option"
        usage()
        sys.exit(2)

if username == None:
    username = raw_input("Enter Ravello Username: ")

if password == None:
    password = getpass.getpass("Enter Password: ")
    
# start session and authenticate
session=requests.Session()
headers={ 'Content-Type': 'application/json', 'Accept': 'application/json'}
session.post('https://cloud.ravellosystems.com/api/v1/login', auth=(username, password))

# query list of applications in organization
result=session.get('https://cloud.ravellosystems.com/api/v1/applications', headers = headers)
applicationslist=result.json()
# Pretty print the response
#print(json.dumps(result.json(), indent=2))
# define pattern to filter for one blueprint
regex = '(.*)' + re.escape(apppattern) + '-(.*)'
# push all ids for one bp pattern to list
labapps = []
count = 0
file = open("lab_list.adoc","w")
file2 = open("lab_list.inventory","w")
print "|Seat No|GUID|External Hostnames"
file.write('[width="70%"]\n')
file.write('[cols="1,1,3"]\n')
file.write("|===\n")
file.write("|Seat No|GUID|External Hostnames\n\n")
for application in applicationslist:
    match = re.search(regex, application['name'], re.I)
    if match:
        count += 1
        #print "Name: " + application['name']
        hostname = "control-"+match.group(2)+".rhpds.opentlc.com"
        print "|", count, "|", match.group(2), "|", hostname, "|" 
        file.write("|" + str(count) + "|" + match.group(2) + "|" + hostname + "\n")
        file2.write(match.group(2) + " ansible_host=" + hostname + "\n")
file.write("|===\n")
file.close() 
file2.close()
