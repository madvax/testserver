# testserver
test server

The Python script "delay-http.py" is a testing web server.

You can use it in three ways:

1.) You can specify a number of seconds to delay the respose of
    a web page using the /delay in the url. To use this feature
    run the script then, to get a three second delay use this
    URL:  http:/localhost/delay/3
    The server will wait three sconds before sending the response.
    The server's response should look something like this:
   
    {"SUCCESS": "200",
     "delay": "3 seconds"}

2.) You can force an HTTP response from server using  /status 
    in the URL. To use this feature run the script and  
    use this URL: http://localhost/status/500
    The server will respond with an HTTP response code of 500 
    and send the response below:

    {"SUCCESS": "500",
     "STATUS" : {"HTTP_Status" : "500",
                "Message"      : "Internal Server Error",
                "Gudance"      : "A generic error message, given when an unexpected condition was encountered and no more specific message is suitable."} }

3.) You can also have the server provide larger JSON strings by 
    using /time in the url. To use this feature start the script 
    and use this URL: http://localhost/time
    The web server will return an HTTP status of 200 and provide 
    the servers local time is the form below:

    {"Local weekday name"             : "Fri",
     "Local weekday name"             : "Friday",
     "Local abbreviated month name"   : "Apr",
     "Local full month name"          : "April",
     "Local date time representation" : "Fri Apr 13 20:24:07 2018",
     "Day of the month decimal"       : "13",
     "Hour (24-hour)"                 : "20",
     "Hour (12-hour)"                 : "08",
     "Day of the year decimal"        : "103",
     "Month decimal"                  : "04",
     "Minute decimal"                 : "24",
     "Local AM or PM."                : "PM",
     "Second decimal"                 : "07",
     "Week number Sunday decimal"     : "14",
     "Weekday decimal"                : "5",
     "Week number Monday decimal"     : "15",
     "Local date representation."     : "04/13/18",
     "Locale time representation."    : "20:24:07",
     "Year without century decimal"   : "18",
     "Year with century decimal"      : "2018",
     "Time zone name"                 : "UTC" }
 
When executing the script you can specify an IP address and port 
nubmer to bind the server to using command line arguments. 

USAGE: delay-httpd.py 

OPTIONS:

   -h --help       Display this message.


   -v --verbose    Runs the program in verbose mode

   -d --debug      Runs the program in debug mode (implies verbose)

   -i --IP_Address The IPv4 Address to use for the HTTP Server

   -p --port       The port number to use for the HTTP server

EXIT CODES:

  0 - Clean Exit

  1 - Bad or missing command line argument

  2 - Invalid port specified, port must be an integer

  3 - Invalid port specified, port must be an integer between (1025-63354)

  4 - Invalid IPv4 Address specified

  5 - You must be root to bind to ports under 1024

  6 - Unable to start web server

  Other Non-Zero - Failure of some sort or another

NOTE: Some ports require administrator/root access to bind the server.

EXAMPLES:

To run the server in the background or as a deamon process
on mist Linux systems use this:

sudo ./delay-httpd.py -i 129.196.196.183 > /dev/null 2>&1  &






 

