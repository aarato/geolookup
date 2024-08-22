# Geolookup
Geolookup based on GeoLite2 Free Geolocation Data

## Installation & Usage
Script will print out the geolocation of all IP addresses (1 per line) in the ips.txt file.
You need to create a license.txt file with a free API key from the [GeoLite2](https://dev.maxmind.com/geoip/geolite2-free-geolocation-data) website.The script will download the up-to-date database from Maxmind automatically, if it is older than 24 hours.
```
git clone https://github.com/aarato/geolookup
cd geolookup
pip install -r requirements.txt
echo "My_License_Key_From_Maxmind" > license.txt
python3 index.py
```
