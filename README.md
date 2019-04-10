# Feedback from EIDA users

At EIDA we are trying to improve the communication with our users by providing official channels to report problems or questions. This space will be taken as a first (experimental) approach to see if you feel comfortable reporting and tracking your issues by means of this tool.

## Guidelines
Please keep in mind the following guidelines before reporting a problem.

1. Do a search first in the Issue Tracker to see if someone else already reported the same problem.
1. Try to use the most reasonable template from the ones we provide in order for us to properly assign a responsible person for your issue.
1. Take a look at the examples provided here, the documentation at the Orfeus website and in the EIDA Authentication Service to understand how you are suppose to use/access different resources.

## Examples of code to access data

### Obspy
In the following example the RoutingClient from Obspy is used to access data from all EIDA. In addition, the parameter credentials is passed with details about the EIDA the token.

It is highly recommended to use **always** the token with the client. Even if you are requesting open data. That prevents errors like not providing a token due to a misunderstanding about the data being open/restricted. And on the other hand it helps data centres to understand better user needs by means of more detailed statistics.

    >>> from obspy.clients.fdsn import RoutingClient
    >>> from obspy import UTCDateTime
    
    >>> rsClient = RoutingClient("eida-routing", credentials={'EIDA_TOKEN': '/Users/javier/.eidatoken'})
    >>> st = rsClient.get_waveforms(network="Z3", channel="HHZ", starttime=UTCDateTime(2016, 3, 1), endtime=UTCDateTime(2016, 3, 1, 0, 2, 0))
    >>> print(st)
    
    165 Trace(s) in Stream:
    
    Z3.A022A..HHZ | 2016-03-01 - 2016-03-01T00:02:01.540000Z | 100.0 Hz, 12396 samples
    
    (163 other traces)...
    
    Z3.A216A.00.HHZ | 2016-03-01 - 2016-03-01T00:02:00.000000Z | 100.0 Hz, 12001 samples

### fdsnws_fetch
The fdsnws_fetch is the main command line client provided by the fdsnwsscripts package. On one hand, this client was designed to mantaing backwards compatibility with the old arclink_fetch, so that users can seamlessly switch from Arclink requests to the new web services. But it is also important to mention that this client supports all recent developments from EIDA, including the usage of the EIDA token, and the provision of a proper citation in a paper for the requested data.

    $ fdsnws_fetch -vvv -N Z3 -C "HHZ" -s "2016-03-01" -e "2016-03-01T00:02:00" -o data.mseed 
    using token in /home/javier/.eidatoken:
    {"valid_until": "2019-04-20T12:33:43.663076Z", "cn": "Javier Quinteros", "memberof": "/epos/alparray;/epos;/", "sn": "Quinteros", "issued": "2019-03-21T12:33:43.663083Z", "mail": "javier@gfz-potsdam.de", "givenName": "Javier", "expiration": "1m"}
    
    getting routes from http://geofon.gfz-potsdam.de/eidaws/routing/1/query?network=Z3&....
    authenticating at https://erde.geophysik.uni-muenchen.de/fdsnws/dataselect/1/auth
    authenticating at https://www.orfeus-eu.org/fdsnws/dataselect/1/auth
    authenticating at https://eida.ethz.ch/fdsnws/dataselect/1/auth
    authenticating at https://webservices.ingv.it/fdsnws/dataselect/1/auth
    authenticating at https://ws.resif.fr/fdsnws/dataselect/1/auth
    
    authentication at https://erde.geophysik.uni-muenchen.de/fdsnws/dataselect/1/auth successful
    getting data from http://erde.geophysik.uni-muenchen.de/fdsnws/dataselect/1/queryauth
    got 516608 bytes (mseed) from http://erde.geophysik.uni-muenchen.de/.../queryauth
    
    authentication at https://ws.resif.fr/fdsnws/dataselect/1/auth successful
    getting data from http://ws.resif.fr/fdsnws/dataselect/1/queryauth
    got 90112 bytes (mseed) from http://ws.resif.fr/fdsnws/dataselect/1/queryauth 
    
    authentication at https://eida.ethz.ch/fdsnws/dataselect/1/auth successful
    getting data from http://eida.ethz.ch/fdsnws/dataselect/1/queryauth
    got 293888 bytes (mseed) from http://eida.ethz.ch/.../1/queryauth
    
    authentication at https://www.orfeus-eu.org/fdsnws/dataselect/1/auth successful
    getting data from http://www.orfeus-eu.org/fdsnws/dataselect/1/queryauth
    got 950272 bytes (mseed) from http://www.orfeus-eu.org/fdsnws/dataselect/1/queryauth
    
    received no data from http://webservices.ingv.it/fdsnws/dataselect/1/queryauth 

