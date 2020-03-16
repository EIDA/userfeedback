import os
import json
import argparse
import datetime
import random
import time
import requests
from obspy.clients.fdsn import RoutingClient
from obspy import UTCDateTime
from obspy import Stream


def wfcatalog(net, sta, cha, start, end):
    params = dict()
    params['network'] = net
    params['station'] = sta
    params['channel'] = cha
    # No time can be included in these parameters because the WFCatalog
    # at BGR seems to have problems with it
    params['start'] = '%d-%02d-%02d' % (start.year, start.month, start.day)
    params['end'] = '%d-%02d-%02d' % (end.year, end.month, end.day)
    params['format'] = 'post'
    params['service'] = 'wfcatalog'
    r = requests.get('http://www.orfeus-eu.org/eidaws/routing/1/query', params)
    if r.status_code == 200:
        wfcurl = r.content.decode('utf-8').splitlines()[0]
    else:
        raise Exception('No routing information for WFCatalog: %s' % params)

    del params['format']
    del params['service']
    params['include'] = 'sample'
    params['longestonly'] = 'false'
    params['minimumlength'] = 0.0
    r = requests.get(wfcurl, params)

    if r.status_code == 200:
        metrics = json.loads(r.content.decode('utf-8'))
        # print(metrics)
    else:
        raise Exception('No metrics for %s.%s %s' % (net, sta, start))
        # print 'Retrieved metrics for', network.code, station.code

    return metrics


def main():
    # Default values for start and end time (last year)
    sy = datetime.datetime.now().year - 1
    ey = sy

    desc = 'Script to check accessibility of data through all EIDA nodes.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-s', '--start', default=sy, type=int,
                        help='Year to start the test (default=last year).')
    parser.add_argument('-e', '--end', default=ey, type=int,
                        help='Year to end the test (default=last year).')
    parser.add_argument('--days', default=5, type=int,
                        help='How many days to randomly pick from the year (default=5).')
    parser.add_argument('--hours', default=2, type=int,
                        help='How many hours to randomly pick from each day (default=2).')
    parser.add_argument('--minutes', default=10, type=int,
                        help='Length of each individual download request in minutes (default=10).')
    parser.add_argument('-t', '--timeout', default=30, type=int,
                        help='Number of seconds to be used as a timeout for the HTTP calls (default=30).')
    parser.add_argument('-x', '--exclude', default=None,
                        help='List of comma-separated networks to be excluded from this test (e.g. XX,YY,ZZ).')
    parser.add_argument('-a', '--authentication', default=os.path.expanduser('~/.eidatoken'),
                        help='File containing the token to use during the authentication process (default=~/.eidatoken).')

    args = parser.parse_args()

    # List of networks to exclude
    if args.exclude is not None:
        nets2exclude = list(map(str.strip, args.exclude.split(',')))
    else:
        nets2exclude = list()

    # Create a client to the EIDA Routing Service
    token = os.path.expanduser('~/.eidatoken')  # path to personal eida token here
    rsClient = RoutingClient("eida-routing", credentials={'EIDA_TOKEN': token})

    for y in range(args.start, args.end+1):
        print('Processing year %d' % y)
        t0 = UTCDateTime(y, 1, 1)
        t1 = UTCDateTime(y, 12, 31)

        # Do not include restricted streams
        st = rsClient.get_stations(level='channel', channel='BHZ,HHZ', starttime=t0, endtime=t1,
                                   includerestricted=False, timeout=args.timeout)
        totchannels = len(st.get_contents()['channels'])

        print('# %s' % st.get_contents()['channels'])
        print('# %d channels found' % len(st.get_contents()['channels']))

        curchannel = 0
        for net in st:
            for sta in net:
                for cha in sta:
                    downloaded = []
                    curchannel += 1

                    if net.code in nets2exclude:
                        print('%d/%d; Network %s is blacklisted'
                              % (curchannel, totchannels, net.code))
                        continue
                    # Keep track of the amount of time per request
                    reqstart = time.time()
                    data = Stream()

                    # Days should be restricted to the days in which the stream is open
                    realstart = max(t0, cha.start_date)
                    realend = min(t1, cha.end_date) if cha.end_date is not None else t1
                    totaldays = int((realend - realstart) / (60 * 60 * 24))

                    # We have less days in the epoch than samples to select
                    if totaldays <= args.days:
                        print('%d/%d; Skipped because of a short epoch; %d %s %s %s'
                              % (curchannel, totchannels, y, net.code, sta.code, cha.code))
                        continue

                    days = random.sample(range(1, totaldays+1), args.days)

                    hours = random.sample(range(0, 24),
                                          args.hours)  # create random set of hours and days for download test
                    hours_with_data = 0
                    days_with_metrics = 0

                    # Get the inventory for the whole year to test
                    inventory = rsClient.get_stations(network=net.code,
                                                      station=sta.code,
                                                      channel=cha.code,
                                                      starttime=realstart,
                                                      endtime=realend,
                                                      level='response')

                    metadataProblem = False

                    # for day in tqdm(days) : #  loop through all the random days
                    for day in days:  # loop through all the random days
                        # Check WFCatalog for that day
                        try:
                            auxstart = realstart + day * (60*60*24)
                            auxend = realstart + (day+1) * (60*60*24)
                            metrics = wfcatalog(net.code, sta.code, cha.code, auxstart, auxend)
                            days_with_metrics += 1
                        except Exception as e:
                            print(e)

                        for hour in hours:  # loop through all the random hours (same for each day)
                            # start = UTCDateTime('%d-%03dT%02d:00:00' % (y, day, hour))
                            start = realstart + day * (60*60*24) + hour * (60*60)
                            end = start + (args.minutes * 60)
                            # print(y, net.code, sta.code, cha.code, start, end)

                            try:
                                # get the data
                                data_temp = rsClient.get_waveforms(network=net.code,
                                                                   station=sta.code,
                                                                   channel=cha.code,
                                                                   starttime=start,
                                                                   endtime=end)
                                data_temp.trim(starttime=start, endtime=end)

                                data_temp.remove_response(inventory=inventory)
                                if data_temp.data[0] != data_temp.data[0]:
                                    metadataProblem = True
                                    print('Error with metadata!')

                                data += data_temp

                                data_exists = 'yes'
                                hours_with_data += 1
                            except Exception as e:
                                # print(year, channel, nodename, network, station, day, hour, e)
                                # print('----------------------------')
                                data_exists = 'no'

                    full_time = args.days * args.hours * args.minutes * 60

                    if hours_with_data > 0:  # check how much data was downloaded
                        locs = []
                        for tr in data:
                            locs.append(tr.stats.location)

                        locs = list(set(locs))
                        if len(locs) > 1:
                            completeness_by_loc = [[], [], []]
                            for loc in locs:
                                data_temp = data.copy().select(location=loc)
                                total_time_covered = 0
                                for tr in data_temp:
                                    time_covered = min(tr.stats.endtime - tr.stats.starttime,
                                                       args.minutes*60.0)
                                    total_time_covered += time_covered

                                percentage_covered = total_time_covered / full_time
                                completeness_by_loc[0].append(loc)
                                completeness_by_loc[1].append(total_time_covered)
                                completeness_by_loc[2].append(percentage_covered)
                            percentage_covered = max(completeness_by_loc[2])
                            total_time_covered = max(completeness_by_loc[1])

                        else:
                            total_time_covered = 0
                            for tr in data:
                                # Maximum of time is what we requested. If the DC sends
                                # more we consider only the requested time
                                time_covered = min(tr.stats.endtime - tr.stats.starttime,
                                                   args.minutes * 60.0)
                                total_time_covered += time_covered

                            percentage_covered = total_time_covered / full_time

                    else:
                        total_time_covered = 0.0
                        percentage_covered = 0.0

                    minutes = (time.time()-reqstart)/60.0
                    print('%d/%d; %8.2f min; %d %s %s %s; perc received %3.1f; perc w/metrics %3.1f; %s' %
                          (curchannel, totchannels, minutes, y, net.code, sta.code, cha.code,
                           percentage_covered * 100.0, days_with_metrics*100.0/args.days,
                           'ERROR' if metadataProblem else 'OK'))
                    downloaded.append([y, net.code, sta.code, cha.code, percentage_covered * 100, minutes,
                                       days_with_metrics*100.0/args.days, 'ERROR' if metadataProblem else 'OK'])

                    with open('results.txt', 'a') as fout:
                        for l in downloaded:
                            to_write = '%d %s %s %s %f %f %f %s' % (l[0], l[1], l[2], l[3], l[4], l[5], l[6], l[7])
                            fout.write(to_write + '\n')


if __name__ == '__main__':
    main()
