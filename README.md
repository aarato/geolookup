# Geolookup
Geolookup based on GeoLite2 Free Geolocation Data

## Installation & Usage
Script will print out the geolocation of all IP addresses (1 per line) in the ips.txt file.
The database will be downloaded from Maxmind if it is older than 24 hours the first time you run the script.
'''
git clone https://github.com/aarato/geolookup
cd geolookup
pip install -r requirements
python3 index.py
'''
