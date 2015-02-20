# A10 script to parse IP to ID data.
# This script is intended to for A10 Networks IDSentrie appliance.

__author__ = "Luis Nunez"
__license__ = "GPLv3"
__version__ = "0.1.2"
__maintainer__ = "Luis Nunez"
__status__ = "Prototype"

import subprocess
from datetime import datetime, timedelta
import logging
import sys
import csv
from lxml import etree, objectify
from sys import argv


def parseXML(xmlFile):
    csvfile = open('parseXML - a10_delta_data.csv', 'w')
    logging.info('Open a10_delta_data.csv for writing')
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
                #print ld2ip_out
                writer.writerow((ld2ip_out))
                ld2ip_out = []
    print user_ip_count
    print user_activity_count

    csvfile.close()
    logging.info('parse-XML - Closed a10_delta_data.csv')

def build_time():
    A10_time_format = "%Y-%m-%d %H:%M:%S %Z"

    current_datetime = datetime.now()
    print current_datetime
    current_year = current_datetime.year
    current_month = current_datetime.month
    current_day = current_datetime.day
    current_hour = current_datetime.hour
    z = datetime(current_year, current_month, current_day, current_hour, 00)
    diff_datetime = current_datetime - timedelta(hours=1)
    diff_year = diff_datetime.year
    diff_month = diff_datetime.month
    diff_day = diff_datetime.day
    diff_hour = diff_datetime.hour
    x = datetime(diff_year, diff_month, diff_day, diff_hour, 00)
    #d = datetime.strptime(diff_datetime, A10_time_format)

    print "current time: %s" % current_datetime
    print "Zulu time: %s" % diff_datetime.isoformat()
    print "Start hour: %s" % diff_hour
    print "Start time: %s" % diff_datetime.strftime(A10_time_format)+"+0000"
    print "Start request time: %s" % x + " +0000"
    print "End request time: %s" % z + " +0000"
    #print current_datetime.strftime(A10_time_format)
    xx = str(x)
    zz = str(z)
    logging.info('build_time - end')
    return (xx,zz)

def build_request(TS, TE):
    TZ = " +0000"
    A10xml_begin = """<?xml version="1.0" standalone="yes"?>
    <IDSentrieServiceReq>
        <partner_id>a10-id</partner_id>
        <partner_passcode>a10-passwd</partner_passcode>
        <service name="IDSentrieUser" version="1.1">
            <action id="IPIDActivityGet">
                <!-- Type delta | latest | normal | now -->
                <type>delta</type>"""
    TimeStart = "<time_start>" + TS + TZ + "</time_start>"
    TimeEnd = "<time_end>" + TE + TZ + "</time_end>"
    A10xml_end = """
                <return_attribute_list>
                    <user_hostname/>
                    <server_ip/>
                    <server_hostname/>
                    <domain_name/>
                    <dc_name/>
                    <!-- <user_detail view=uim-view-name/> -->
                </return_attribute_list>
                <!-- group_by options username or user_ip -->
                <group_by>user_ip</group_by>
            </action>
        </service>
    </IDSentrieServiceReq>"""
    # Build A10 XML request.
    A10xml_request = A10xml_begin + TimeStart + TimeEnd + A10xml_end
    request_file = open('delta_request1.xml','w')
    request_file.write(A10xml_request)
    print A10xml_request
    request_file.close
    logging.info('build_request - End')

def main():
    logging.basicConfig(filename='a10api.log', level=logging.INFO, format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p')
    logging.info('Started')
    x,z = build_time()
    f = build_request(x,z)
    subprocess.call("curl -X POST -d @delta_request1.xml https://x.x.x.x:2393/xml/request -v -k -o delta_request1_data.xml")
    parseXML('delta_request1_data.xml')
    logging.info('Finished')

if __name__ == "__main__":
    main()