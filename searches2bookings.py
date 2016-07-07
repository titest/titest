
import csv
import argparse
import sys
import cPickle as pickle
import os.path
from datetime import datetime

SEARCHES_FILE = "searches.csv"
BOOKINGS_FILE = "bookings.csv"
DICT_FILE = "dict.p"
OUTPUT_FILE = "searches_matched.csv"
DATE_FORMAT = '%Y-%m-%d'

def do_it():
  """ Create a file searches_output.csv with an extra column showing booking match
    Algorithm works as following
    First pass: Build a dictionary to cache the  booking data
    This is serialized into a file in order to minimize execution time between re-run
    Second pass: Go through the search file and try to match each search with a booking
  """    
  with open(SEARCHES_FILE, 'rb') as searches_csv, open(BOOKINGS_FILE, 'rb') as bookings_csv, open(OUTPUT_FILE, 'wb') as output_csv:
    searchreader = csv.DictReader(searches_csv, delimiter='^', quoting=csv.QUOTE_MINIMAL)
    bookingreader = csv.DictReader(bookings_csv, delimiter='^', quoting=csv.QUOTE_MINIMAL)

    bookings_dict = {}
    

    if (os.path.isfile(DICT_FILE)):
        print "Load existing bookings dictionary"
        with open(DICT_FILE, 'rb') as dict_p:
            bookings_dict = pickle.load(dict_p)
    else:
        # Cache the bookings data in a dictionary
        for l, row in enumerate(bookingreader):
            if l % 10000 == 0:
                print "Process bookings row", l

            row_nb = l + 2
            
            # Remove the booking if it is a cancellation (pax <= 0)
            if row['pax'] is not None and int(row['pax'].strip()) > 0:
                date_booking = row['cre_date           '].strip().split()[0]
                date_flight = row['brd_time           '].strip().split()[0]
                # Remove bookings whose creation date is after flight date or if dates cannot be parsed
                try:
                    if datetime.strptime(date_booking, DATE_FORMAT) > datetime.strptime(date_flight, DATE_FORMAT):
                        continue
                except: continue
                key = (row['route          '].strip(), date_flight)
                rloc = row['rloc          ']
                # Build a dict of dicts to have two keys indexation level
                # First level: route, departure date
                # Second level: booking creation date
                if key not in bookings_dict:
                    bookings_dict[key] = {}
                
                bookings_dict[key].update({date_booking: (row['rloc          '].strip(), row_nb)})
        
        with open(DICT_FILE, 'wb') as dict_p:
            pickle.dump(bookings_dict, dict_p)
    
    col_booking = 'booking'
    fieldnames = searchreader.fieldnames + [col_booking]
    outputwriter = csv.DictWriter(output_csv, delimiter='^', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
    outputwriter.writeheader()
    row_nb = 0
    matching_count = 0
    
    for l, row in enumerate(searchreader):
        try:
            row_nb = l + 2
            if l % 10000 == 0:
                print "Process searches row", l
                      
            
            origin = row['Origin'].strip()
            dest = row['Destination'].strip()
            
            dest_cur = origin
            route = origin
            seg_count = 0
            date_flight = row['Seg1Date'].strip()
            assert(origin == row['Seg1Departure'].strip()), "Origin mismatch at {}".format(row_nb)
            
            # Create the search route of the outbound
            while dest_cur != dest:
                seg_count += 1
                assert(seg_count <= 6), "Seg overflow in route at {}".format(row_nb)
                
                key_depart = "Seg{0}Departure".format(seg_count)
                key_arrival = "Seg{0}Arrival".format(seg_count)
                
                origin_cur = row[key_depart].strip()
                #Case where vias are not arriving/leaving at same airport
                if dest_cur != origin_cur:
                    route += origin_cur
                    
                dest_cur = row[key_arrival].strip()
                route += dest_cur
            
            if row['RoundTrip'] == '1':
                assert(seg_count < int(row['NbSegments'])), "Round trip wrong segment count at {0} {1} at {2}".format(seg_count, row['NbSegments'], row_nb)
                    
            # Do the check only on the outbound, we suppose that there cannot be a booking for inbound with no booking for outbound
            key = (route, date_flight)
            search_date = row['Date'].strip()

            if key in bookings_dict:
                # We consider a matching only if the search date and the booking creation date meet this inequality:
                # search date <= booking date <= flight date
                # A stricter condition would be to have search and booking date equal
                row[col_booking] = 0
                # Case where search_date == booking creation date
                if search_date in bookings_dict[key]:
                    row[col_booking] = 1
                    matching_count += 1
                else:
                    dateobj_search = datetime.strptime(search_date, DATE_FORMAT)
                    dateobj_flight = datetime.strptime(date_flight, DATE_FORMAT)
                    for date_booking, rloc in bookings_dict[key].iteritems():
                        dateobj_booking = datetime.strptime(date_booking, DATE_FORMAT)
                        assert(dateobj_booking <= dateobj_flight), "Booking/Flight date in wrong order"

                        if dateobj_search <= dateobj_booking:
                            row[col_booking] = 1
                            matching_count += 1
                            break

            
            outputwriter.writerow(row)
        
        # Some rows are delimited by ',' instead of '^' -> they are disregarded
        except Exception as e:
            continue
            
    print "END Total searches/bookings matched:{0}/{1} ".format(matching_count, row_nb - 1) 
    

if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Create a csv files for show bookings conversion')

  args = parser.parse_args()
  
  do_it()
  