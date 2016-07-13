# titest

## Exercise 1

```
awk 'END {print NR}' searches.csv
20390199
awk 'END {print NR}' bookings.csv
10000011
```

## Exercise 2

Python version:
Exercise2.ipynb

or
Bash version:
```
awk -F^ 'NR>1{arr[$13]+=$35} END {for (i in arr) {print i,arr[i]}}' bookings.csv | sort -r -g -k2 | head -n 10 | awk '{code=$1;nb=$2;"curl -s \"http://api.geonames.org/searchJSON?q="$1"\&maxRows=1&fcode=AIRP&username=demo\" "| getline; print code, "\t", gensub(/.*"toponymName":"([^"]+)".*/,"\\1","g"), "\t", nb}'

LHR      London Heathrow Airport         88809
MCO      Orlando International Airport   70930
LAX      Los Angeles International Airport       70530
LAS      Las Américas International Airport      69630
JFK      John F. Kennedy International Airport   66270
CDG      Paris Charles de Gaulle Airport         64490
BKK      Suvarnabhumi Airport    59460
MIA      Maseru-Mia      58150
SFO      San Francisco International Airport     58000
DXB      Dubai International Airport     55590
```

## Exercise 3

See Exercise3.ipynb

## Bonus exercise: Match searches with bookings

```
python searches2bookings.py

Will produce searches_matched.csv
```

## Bonus exercise: Write a Web Service

Create data file with:
```
echo "Code, Paxes" > airports.csv
awk -F^ 'NR>1{arr[$13]+=$35} END {for (i in arr) {print i,arr[i]}}' bookings.csv | sort -r -g -k2 | awk '{print $1, ", ", $2}' >> airports.csv
```

Run the server with:
```
python simplejsonserver.py 8080 127.0.0.1 &
```

Test client call (with n=10 for instance):
```
curl -s -X GET "http://127.0.0.1:8080/api/v1/getpaxes/10" -H “Content-Type: application/json”
```
