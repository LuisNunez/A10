# This code parses A10 IP to ID log data(XML) files.
#
#
# version 0.1.0
# prototype

import sys
import csv
from lxml import etree, objectify
from sys import argv


def parseXML(xmlFile):
    csvfile = open('a10id2ip.csv', 'w')

    x = ["user_ip", "username", "time_start", "time_end", "user_hostname",
         "server_ip", "server_hostname", "domain"]
    writer = csv.writer(csvfile, quoting=csv.QUOTE_ALL)
    writer.writerow(x)
    with open(xmlFile) as f:
        xml = f.read()

    root = objectify.fromstring(xml)
    # returns attributes in element node as dict
    attrib = root.attrib

    user_ip_count = 0
    user_activity_count = 0

    # loop over elements and print tag text.
    for appt in root.service.action.getchildren():
        ld2ip_out = []
        for e in appt.getchildren():
            if e.tag == "user_ip":
                user_ip = e.text
            if e.tag == "user_activity":
                ld2ip_out.append(user_ip)
                user_ip_count += 1
                for ee in e.getchildren():
                    if ee.tag == "username":
                        username = ee.text
                        ld2ip_out.append(username)
                    if ee.tag == "time_start":
                        time_start = ee.text
                        ld2ip_out.append(time_start)
                    if ee.tag == "time_end":
                        time_end = ee.text
                        ld2ip_out.append(time_end)
                    if ee.tag == "user_hostname":
                        user_hostname = ee.text
                        ld2ip_out.append(user_hostname)
                    if ee.tag == "server_ip":
                        server_ip = ee.text
                        ld2ip_out.append(server_ip)
                    if ee.tag == "server_hostname":
                        server_hostname = ee.text
                        ld2ip_out.append(server_hostname)
                    if ee.tag == "domain_name":
                        domain_name = ee.text
                        ld2ip_out.append(domain_name)
                    user_activity_count += 1
                print ld2ip_out
                writer.writerow((ld2ip_out))
                ld2ip_out = []
    print user_ip_count
    print user_activity_count

    csvfile.close()
# ----------------------------------------------------------------------
if __name__ == "__main__":
    # f = r'38116.xml'
    f = argv[1]
    parseXML(f)
