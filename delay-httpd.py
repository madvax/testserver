#!/usr/bin/env python

# =============================================================================
# DESCRIPTION
# This script starts a web server that will delay the response of sending a web
# page by a specified number of seconds. The delay is specified by the calling
# HTTP client program using a RESTful HTTP GET that includes the path
# /delay/integer as part of URL called by the HTTP client; where integer is the
# number of seconds to wait before responding.
#
# -- H. Wilson, March 2018

# Note: To run as a daemon: 
# sudo ./delay-httpd.py >/dev/null 2>&1  &

# =============================================================================
# STANDARD LIBRARY IMPORTS
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import SocketServer
import os
import sys
import time
from getopt import getopt
import socket
import json 
import subporcess

# =============================================================================
# DICTIONARY
VERSION        = "1.2.0"  # Added default eth0 ip address
DEBUG          = False    # Flag for debug operation
VERBOSE        = False    # Flag for verbose operation
FIRST          = 0        # first element in a list
LAST           = -1       # last element in a list
ME             = os.path.split(sys.argv[FIRST])[LAST]        # Name of this file
MY_PATH        = os.path.dirname(os.path.realpath(__file__)) # Path for this file
EXIT_SUCCESS   = 0           # Default success exit code stdlib.h
IP_ADDRESS     = "127.0.0.1" # Default IPv4 Address for the web server
PORT           = 80          # Default port number for the web server, may require root/administrator privileges
HTTP_DATA_FILE = "http_status_codes.json"
TIME_FORMAT    = """
{\"Local weekday name\"             : \"%a\",
 \"Local weekday name\"             : \"%A\",
 \"Local abbreviated month name\"   : \"%b\",
 \"Local full month name\"          : \"%B\",
 \"Local date time representation\" : \"%c\",
 \"Day of the month decimal\"       : \"%d\",
 \"Hour (24-hour)\"                 : \"%H\",
 \"Hour (12-hour)\"                 : \"%I\",
 \"Day of the year decimal\"        : \"%j\",
 \"Month decimal\"                  : \"%m\",
 \"Minute decimal\"                 : \"%M\",
 \"Local AM or PM.\"                : \"%p\",
 \"Second decimal\"                 : \"%S\",
 \"Week number Sunday decimal\"     : \"%U\",
 \"Weekday decimal\"                : \"%w\",
 \"Week number Monday decimal\"     : \"%W\",
 \"Local date representation.\"     : \"%x\",
 \"Locale time representation.\"    : \"%X\",
 \"Year without century decimal\"   : \"%y\",
 \"Year with century decimal\"      : \"%Y\",
 \"Time zone name\"                 : \"%Z\" }"""

# =============================================================================
# DEFINE THE DEFAULT IP_ADDRESS
# Try to use the IPv4 address for the "primary" network interface as the 
# default IP Address.
try:
try:
   s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
   s.connect(("8.8.8.8", 80)) # google-public-dns-a.google.com
   IP_ADDRESS = s.getsockname()[0]
   s.close()
except: pass # If anything goes wrong then 127.0.0.1 will be the default address

# =============================================================================
# CLASS HTTP SERVER
class S(BaseHTTPRequestHandler):

   # Improperly overloaded BaseHTTPRequestHandler, sorry for this poor shortcut.
   # TODO: Correctly Super class the BaseHTTPRequestHandler with "super.__init__()"
   """
   # TODO: Correctly superclass the BaseHTTPRequestHandler to allow this to work
   # -------------------------------------------------------------------------- S.__init__()
   def __init__(self):
      # self.response = 200            # Default response code
      # self.content  = 'Content-type' # Default Content header
      # self.type     = 'text/html'    # Default Content Type
      # self.delay    = 0              #
      # self.pageText = "" %(self.response, self.delay)
      pass
   """
   
   # -------------------------------------------------------------------------- S._set_headers()
   def _set_headers(self, response=200):
      # Set and send the HTTP response header over the socket.
      # If the status code is in the list of status codes from the json file then 
      # use that status code, else set and send response status code 400  
      if str(response) in http_status_codes.keys():
         self.send_response(response)
      else:
         self.send_response(400)
      self.send_header('Content-type', 'text/html')
      self.end_headers() 
  

   # -------------------------------------------------------------------------- S.do_GET()
   def do_GET(self):
      """ Process an HTTP GET request.
          Parse and wait the specified delay time. """
      restPath =  str(self.path)

      # --- Process a delay directive  
      if "delay" in restPath:
         if DEBUG: print "Found delay of "
         if DEBUG: print "\"%s\"" %restPath

         try:
            pathParts = restPath.split("/")
            seconds = int(pathParts[LAST])
            time.sleep(seconds)
            self._set_headers(200)    
            self.wfile.write("<html><body><PRE>{\"SUCCESS\": \"200\",\n  \"delay\": \"%d seconds\"}</PRE></body></html>" %seconds)
         except Exception as e:
            message = "Unable to parse delay seconds from path \'%s\'" %restPath
            if DEBUG: print message
            if DEBUG: print e
            self._set_headers(400) # Bad Request         
            self.wfile.write("<html><body><PRE>{\"ERROR\":\n  {\"message\": \"%s\",\n   \"stack_trace\": \"%s\",\n   \"guidance\": \"Path must be of the form /delay/integer\",\n   \"HTTP_Status\":  400\n  }\n}</PRE></body></html>" %(message, str(e)))

      # -- Process a status directive 
      elif "status" in restPath:
         if DEBUG: print "Found status of "
         if DEBUG: print "\"%s\"" %restPath
         try:
            pathParts = restPath.split("/")
            status = pathParts[LAST]
            if DEBUG: print "Parsed status = \"%s\"" %status
            int_status = int(status)
            if DEBUG: print "integer status = %d" %int_status
            
            if status in http_status_codes.keys():
               if DEBUG: print "Found status code!"
               self._set_headers(int_status)
               self.wfile.write("""
<html>
<head>
<title>SUCCESS %s</title>
</head>
<body>
<PRE>
{\"SUCCESS\": \"%s\",
 \"STATUS\" : {\"HTTP_Status\"   : \"%s\",
             \"Message\"       : \"%s\",
             \"Gudance\"       : \"%s\"} }</PRE>
</body>
</html>""" %(status, status, status, http_status_codes[status][FIRST], http_status_codes[status][LAST]))
            else:
               message = "Specified status \"%s\" is not a valid http status" %status
               if DEBUG: print message  
               self._set_headers(400)
               self.wfile.write("""
<html>
<head>
<title>ERROR: Invalid HTTP status code specified in URL</title>
</head>
<body>
<PRE>
{\"ERROR\": {\"message\"     : \"%s\",
           \"guidance\"    : \"invalid http status specified after '/status' in url\",
           \"HTTP_Status\" : \"400\"  } }</PRE>
</body>
</html>""" %message)


         except Exception as e:
            message = "Unable to parse HTTP status from the URL" 
            self._set_headers(400) # Bad Request         
            self.wfile.write("""
<html>
<head>
<title>ERROR: Unable to parse HTTP status from the URL</title>
</head>
<body>
<PRE>
{\"ERROR\": {\"message\"     : \"%s\",
           \"stack_trace\" : \"%s\",
           \"guidance\"    : \"check  url\",
           \"HTTP_Status\" : \"400\"  } }</PRE>
</body>
</html>""" %(message, str(e)))

           
      # -- Process a time directive 
      elif "time" in restPath:
         t = time.strftime(TIME_FORMAT, time.localtime())  
         self._set_headers(200)
         self.wfile.write("""
<html>
<head>
<title>TIME</title>
</head>
<body>
<PRE>
%s
</PRE>
</body>
</html>""" %t)

                                                                                                                          
      else:
         if DEBUG: print "No restful directrives found"
         self.send_response(200)                       # \  TODO: Make this a function call
         self.send_header('Content-type', 'text/html') #  > See _set_headers()
         self.end_headers()                            # /
         self.wfile.write("""
<html>
<head>
<title>Harold's Testing Web Server</title>
<head>
<body>
<!-- Are you really looking at my HTML Source code? -->
<!-- For Support: Harold.Wilson@netscout.com        -->
<h1>Harold's Testing Web Server</h1>
<BR>
<BR>
Append  <CODE>/delay/3</CODE>  to the URL for a three second delay in response.<BR>
Append  <CODE>/status/404</CODE>  to the URL to generate an HTTP response code of 404, <B>All</B> HTTP status codes are supported.<BR>
Append  <CODE>/time</CODE>  to the URL to get time data<BR><BR> 

Example: <A href=\"http://%s:%d/delay/3\">http://%s:%d/delay/3</A><BR><BR>

<B><U>NOTE:</U></B>The '<CODE>:port</CODE>' designation is optional if you are using the standard port 80
</body>
</html>""" %(IP_ADDRESS, PORT, IP_ADDRESS, PORT))

# =============================================================================
# NATIVE FUNCTIONS

# ----------------------------------------------------------------------------- run()
def run(server_class=HTTPServer, handler_class=S, address='127.0.0.1', port=80):
    """ Start the HTTP Server and have it run forever. Control C to exit."""
    server_address = (address, port)
    try:  
       httpd = server_class(server_address, handler_class)
       httpd.serve_forever()
       showMessage( 'Starting httpd...')
    except Exception as e:
       showError("Unable to start web server\n%s" %str(e))
       sys.exit(6)

# ----------------------------------------------------------------------------- usage()
def usage():
   """usage() - Prints the usage message on stdout. """
   print "\n\n%s, Version %s, Time Delay Web Server."  %(ME,VERSION)
   print ""
   print "This script starts a web server that will delay the response of sending a web"
   print "page by a specified number of seconds. The delay is specified by the calling"
   print "HTTP client program using a RESTful HTTP GET that includes the path"
   print "'/delay/integer' as part of URL called by the HTTP client; where integer is the"
   print " number of seconds to wait before responding."
   print ""
   print "\nUSAGE: %s [OPTIONS]                                    " %ME
   print "                                                         "
   print "OPTIONS:                                                 "
   print "   -h --help       Display this message.                 "
   print "   -v --verbose    Runs the program in verbose mode, default: %s.        " %VERBOSE
   print "   -d --debug      Runs the program in debug mode (implies verbose)      "
   print "   -i --IP_Address The IPv4 Address to use for the HTTP Server, default %s" %IP_ADDRESS
   print "   -p --port       The port number to use for the HTTP server, default %d" %PORT
   print ""
   print "EXIT CODES:                                              "
   print "   0 - Clean Exit"
   print "   1 - Bad or missing command line argument"
   print "   2 - Invalid port specified, port must be an integer"
   print "   3 - Invalid port specified, port must be an integer between (1025-63354)"
   print "   4 - Invalid IPv4 Address specified"
   print "   5 - You must be root to bind to ports under 1024"
   print "   6 - Unable to start web server "
   print " Other Non-Zero - Failure of some sort or another"
   print "                                                         "
   print "EXAMPLES:                                                "
   print "    TODO - I'll make some examples up later.             "
   print "                                                         "
# ----------------------------------------------------------------------------- showError()
def showError(message):
   """showError(str message) write error message to stderr"""
   message = str(message)
   sys.stderr.write("\n\nERROR -- %s\n\n" %message)
   sys.stderr.flush()
   return

# ----------------------------------------------------------------------------- showWarning()
def showWarning(message):
   """showWarning(str message) write warning message to stderr"""
   message = str(message)
   sys.stderr.write("\n\nWARNING -- %s\n\n" %message)
   sys.stderr.flush()
   return

# ----------------------------------------------------------------------------- showMessage()
def showMessage(message):
   """showMessage(str message) write output message to stdout"""
   message = str(message)
   sys.stdout.write("\n%s\n" %message)
   sys.stdout.flush()
   return

# =============================================================================
# MAIN
if __name__ == "__main__":

   # --- Process any command line arguments
   try:
      arguments = getopt(sys.argv[1:]        ,
                         'hvdp:i:'           ,
                         ['help'         ,
                          'verbose'      ,
                          'debug'        ,
                          'port='        ,
                          'IP_Address =' ]   )
   except:
      showError("Bad command line argument(s)")
      usage()
      sys.exit(2)
   # --- Check for a help option
   for arg in arguments[0]:
      if arg[0]== "-h" or arg[0] == "--help":
         usage()
         sys.exit(EXIT_SUCCESS)
   # --- Check for a verbose option
   for arg in arguments[0]:
      if arg[0]== "-v" or arg[0] == "--verbose":
         VERBOSE = True
   # --- Check for a debug option
   for arg in arguments[0]:
      if arg[0]== "-d" or arg[0] == "--debug":
         DEBUG   = True
         VERBOSE = True
   # --- Check for a "port" or "-p" option
   for arg in arguments[0]:
      if arg[0]== "-p" or arg[0]== "--port":
         try:
            tryPort = int(arg[1])
         except:
            message = "Invalid port specified \"%s\", port must be an integer." %tryPort
            showError(message)
            usage()
            sys.exit(2)
         if tryPort < 65535 and tryPort > 1024:
            PORT = tryPort
         else:
            message = "Invalid port number specified \"%s\", port must be between 1025 and 65534." %tryPort
            showError(message)
            sys.exit(3)
   # --- Check for an "address" or "-a" option
   for arg in arguments[0]:
      if arg[0]== "-i" or arg[0]== "--IP_Address":
         try:
            tryAddress = str(arg[1])
            socket.inet_aton(tryAddress)
            IP_ADDRESS = tryAddress
         except:
            message = "Invalid address specified \"%s\", address must be a valid IPv4 Address." %tryAddress
            showError(message)
            sys.exit(4)



   # --- Read the http status code information from the json file 
   with open(HTTP_DATA_FILE) as fd:
      http_status_codes = json.load(fd)   
   

   if DEBUG:
      print "Address: %s" % IP_ADDRESS
      print "Port   : %d" %PORT
   # --- Root Check - Check to see if you are root for ports under 1024
   if PORT < 1024:
      if os.getuid() != 0:
         sys.stderr.write("\nERROR - You must be root to use ports under 1024 for this server")
         sys.stderr.write("\n        Try: sudo %s\n" %ME )
         sys.stderr.write("\n%s NOT started!\n\n" %ME )

         sys.stderr.flush()
         sys.exit(5)
   # --- Run the HTTP Server
   # Start the HTTP Server and have it run forever. Control C to exit.
   # It may require Administrator/root privileges depending on port and system.
   run(address=IP_ADDRESS, port=PORT)
