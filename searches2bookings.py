
import csv
import argparse
import sys

SEARCHES_FILE = "searches.csv"
BOOKINGS_FILE = "bookings.csv"

OUTPUT_FILE = "searches_output.csv"

def do_it():
    
  with open(SEARCHES_FILE, 'rb') as searches_csv, open(BOOKINGS_FILE, 'rb') as bookings_csv, open(OUTPUT_FILE, 'w') as output_csv:
    searchreader = csv.DictReader(searches_csv, delimiter='^', quoting=csv.QUOTE_MINIMAL)
    bookingreader = csv.DictReader(bookings_csv, delimiter='^', quoting=csv.QUOTE_MINIMAL)

    bookings_set = set()
    # Cache the bookings data in a dictionary
    for l, row in enumerate(bookingreader):
        if l % 10000 == 0:
            print "Process bookings row", l

        bookings_set.add((row['dep_port'].strip(), row['arr_port'].strip()))
           
    col_booking = 'booking'
    fieldnames = searchreader.fieldnames + [col_booking]
    outputwriter = csv.DictWriter(output_csv, delimiter='^', quoting=csv.QUOTE_MINIMAL, fieldnames=fieldnames)
    outputwriter.writeheader()
    for l, row in enumerate(searchreader):
        if l % 10000 == 0:
            print "Process searches row", l

        row[col_booking] = int((row['Origin'], row['Destination']) in bookings_set)    
        outputwriter.writerow(row)
    
    

if __name__=='__main__':
  parser = argparse.ArgumentParser(description='Create a csv files for show bookings conversion')

  args = parser.parse_args()
  
  do_it()
  