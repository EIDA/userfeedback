import os
import argparse
import datetime
import random
import time
from obspy.clients.fdsn import RoutingClient
from obspy import UTCDateTime
from obspy import Stream


def main():
    # Default values for start and end time (last year)
    sy = datetime.datetime.now().year - 1
    ey = sy

    desc = 'Script to check accessibility of data through all EIDA nodes.'
    parser = argparse.ArgumentParser(description=desc)
    parser.add_argument('-s', '--start', default=sy, type=int,
                        help='Year to start the test.')
    parser.add_argument('-e', '--end', default=ey, type=int,
                        help='Year to end the test.')
    parser.add_argument('--days', default=5, type=int,
                        help='How many days to randomly pick from the year.')
    parser.add_argument('--hours', default=2, type=int,
                        help='How many hours to randomly pick from each day.')
    parser.add_argument('--minutes', default=10, type=int,
                        help='Length of each individual download request in minutes.')
    parser.add_argument('-t', '--timeout', default=30, type=int,
                        help='Number of seconds to be used as a timeout for the HTTP calls.')
    parser.add_argument('-a', '--authentication', default=os.path.expanduser('~/.eidatoken'),
                        help='File containing the token to use during the authentication process')

    args = parser.parse_args()

    # Create a client to the EIDA Routing Service
    token = os.path.expanduser('~/.eidatoken')  # path to personal eida token here
    rsClient = RoutingClient("eida-routing", credentials={'EIDA_TOKEN': token})

    downloaded = []

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

                    # Keep track of the amount of time per request
                    reqstart = time.time()
                    data = Stream()

                    # Days should be restricted to the days in which the stream is open
                    realstart = max(t0, cha.start_date)
                    realend = min(t1, cha.end_date) if cha.end_date is not None else t1
                    totaldays = int((realend - realstart) / (60 * 60 * 24))

                    # We have less days in the epoch than samples to select
                    if totaldays <= args.days:
                        print('%d/%d; Skipped because of a short epoch; %d %s %s %s' % (curchannel, totchannels, y, net.code, sta.code, cha.code))
                        continue

                    days = random.sample(range(1, totaldays+1), args.days)

                    hours = random.sample(range(0, 24),
                                          args.hours)  # create random set of hours and days for download test
                    hours_with_data = 0

                    # for day in tqdm(days) : #  loop through all the random days
                    for day in days:  # loop through all the random days
                        for hour in hours:  # loop through all the random hours (same for each day)
                            # start = UTCDateTime('%d-%03dT%02d:00:00' % (y, day, hour))
                            start = realstart + day * (60*60*24) + hour * (60*60)
                            end = start + (args.minutes * 60)
                            print(y, net.code, sta.code, cha.code, start, end)

                            try:
                                # get the data
                                data_temp = rsClient.get_waveforms(network=net.code,
                                                                   station=sta.code,
                                                                   channel=cha.code,
                                                                   starttime=start,
                                                                   endtime=end)
                                data_temp.trim(starttime=start, endtime=end)
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
                    print('%d/%d; %8.2f min; %d %s %s %s; perc received %3.1f' % (curchannel, totchannels, minutes, y, net.code, sta.code, cha.code, percentage_covered * 100.0))
                    downloaded.append([y, net.code, sta.code, cha.code, percentage_covered * 100, minutes])

                    with open('results.txt', 'a') as fout:
                        for l in downloaded:
                            to_write = '%d %s %s %s %f %f' % (l[0], l[1], l[2], l[3], l[4], l[5])
                            fout.write(to_write + '\n')


if __name__ == '__main__':
    main()
