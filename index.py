import geoip2.database
import requests
import sys
import os
import tarfile
import time

# Replace these with your actual MaxMind license key
license_key = ''

# Paths to the extracted GeoLite2 ASN and City .mmdb files
license_file = "license.txt"
output_directory="."
asn_edition_id = 'GeoLite2-ASN'  # or 'GeoLite2-ASN'
city_edition_id = 'GeoLite2-City'  # or 'GeoLite2-City'
asn_mmdb_file = 'GeoLite2-ASN.mmdb'
asn_mmdb_tar_gz = 'GeoLite2-ASN.tar.gz'
city_mmdb_file = 'GeoLite2-City.mmdb'
city_mmdb_tar_gz = 'GeoLite2-City.tar.gz'
ip_file = 'ips.txt'

# Function to perform the geolookup for a single IP
def lookup_ip(ip_address, asn_mmdb_file, city_mmdb_file):
    with geoip2.database.Reader(asn_mmdb_file) as asn_reader, geoip2.database.Reader(city_mmdb_file) as city_reader:
        try:
            # Get ASN information
            asn_response = asn_reader.asn(ip_address)
            asn_org = asn_response.autonomous_system_organization
            network = asn_response.network
            
            # Get City information
            city_response = city_reader.city(ip_address)
            country = city_response.country.name
            city = city_response.city.name
            
            # Output the results
            print(f'{ip_address},{network},{asn_org},{country},{city}')
        
        except geoip2.errors.AddressNotFoundError:
            print(f'{ip_address},NOT_FOUND,NOT_FOUND,NOT_FOUND,NOT_FOUND')
        except ValueError:
            print(f'{ip_address},INVALID,INVALID,INVALID,INVALID')

# Function to perform the geolookup for a file with multiple IP addresses, 1 per line
def process_ip_file(ip_file, asn_mmdb_file, city_mmdb_file):
    with open(ip_file, 'r') as file:
        for line in file:
            ip_address = line.strip()  # Remove any leading/trailing whitespace
            if ip_address:  # Check if line is not empty
                lookup_ip(ip_address, asn_mmdb_file, city_mmdb_file)

# Check if the file is older than 24 hours
def file_is_recent(filepath, max_age_seconds=24 * 60 * 60):
    if os.path.exists(filepath):
        file_age = time.time() - os.path.getmtime(filepath)
        return file_age < max_age_seconds
    return False

# Function to read the license file
def read_license_file(license_file):
    if not os.path.exists(license_file):
        sys.exit(f"Error: The file '{license_file}' does not exist. Please create the file and try again.")
    
    try:
        with open(license_file, 'r') as file:
            license_content = file.read().strip()  # Read the file and strip any leading/trailing whitespace
            return license_content
    except IOError as e:
        sys.exit(f"An error occurred while reading '{license_file}': {e}")

# Download the tar.gz file if it's not recent
def download_database(tar_gz_file, edition_id, license_key):
    url = f'https://download.maxmind.com/app/geoip_download?edition_id={edition_id}&license_key={license_key}&suffix=tar.gz'

    response = requests.get(url, stream=True)

    if response.status_code == 200:
        with open(tar_gz_file, 'wb') as file:
            for chunk in response.iter_content(chunk_size=8192):
                file.write(chunk)
        print(f'{tar_gz_file} downloaded successfully.')
    else:
        print(f'Failed to download the database. Status code: {response.status_code}')


# Extract mmdb file from a downloaded tar.gz file
def extract_mmdb(tar_gz_file, output_directory):
    # Open the .tar.gz file
    with tarfile.open(tar_gz_file, "r:gz") as tar:
        # Iterate through the members of the tar file
        for member in tar.getmembers():
            # Check if the member is a .mmdb file
            if member.name.endswith(".mmdb"):
                # Extract the .mmdb file only, ignoring the directory structure
                member.name = os.path.basename(member.name)
                tar.extract(member, path=output_directory)
                print(f'Extracted {member.name} to {output_directory}')
                return os.path.join(output_directory, member.name)
        print("No .mmdb file found in the archive.")

license_key = read_license_file(license_file)

# Download Maxmind ASN DB if not older than 24 hours
if not file_is_recent(asn_mmdb_tar_gz):
    print(f'{asn_mmdb_tar_gz} is older than 24 hours or does not exist. Downloading the latest version...')
    download_database(asn_mmdb_tar_gz, asn_edition_id, license_key)
    extract_mmdb(asn_mmdb_tar_gz, output_directory)
# else:
#     print(f'{asn_mmdb_tar_gz} is up-to-date (less than 24 hours old).')

# Download Maxmind City DB if not older than 24 hours
if not file_is_recent(city_mmdb_tar_gz):
    print(f'{city_mmdb_tar_gz} is older than 24 hours or does not exist. Downloading the latest version...')
    download_database(city_mmdb_tar_gz, city_edition_id, license_key)
    extract_mmdb(city_mmdb_tar_gz, output_directory)
# else:
#     print(f'{city_mmdb_tar_gz} is up-to-date (less than 24 hours old).')

if not os.path.exists(ip_file):
    sys.exit(f"An I/O error occurred while reading '{ip_file}'")
process_ip_file(ip_file, asn_mmdb_file, city_mmdb_file)
