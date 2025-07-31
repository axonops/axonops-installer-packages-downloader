#!/usr/bin/python3
import os
import urllib.request
import gzip
import xml.etree.ElementTree as ET

# Set variables
REPO_URL = "https://packages.axonops.com/yum/"
PACKAGES = [
    "axon-server",
    "axon-agent",
    "axon-dash",
    "axon-dash-pdf",
    "axon-dash-pdf2",
    "axon-dse5.1-agent",  # Ensure this is checked under amd64/arm64
    "axon-dse6.7-agent",  # Ensure this is checked under amd64/arm64
    "axon-dse6.8-agent",  # Ensure this is checked under amd64/arm64
    "axon-dse6.9-agent",  # Ensure this is checked under amd64/arm64
    "axon-cassandra3.11-agent",
    "axon-cassandra4.0-agent",
    "axon-cassandra4.0-agent-jdk8",
    "axon-cassandra4.1-agent",
    "axon-cassandra4.1-agent-jdk8",
    "axon-cassandra5.0-agent-jdk11",
    "axon-cassandra5.0-agent-jdk17"
]
ARCHS = ["x86_64", "noarch"]  # Search for both x86_64 and noarch packages

# Helper function to download files using urllib with user-agent
def download_file(url, dest):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            with open(dest, 'wb') as out_file:
                out_file.write(response.read())
        print(f"Downloaded {url} to {dest}")
    except urllib.error.URLError as e:
        print(f"Failed to download {url}: {e.reason}")

# Version comparison function
def compare_versions(version1, version2):
    # Split the version strings and compare as integers
    v1_parts = list(map(int, version1.split('.')))
    v2_parts = list(map(int, version2.split('.')))
    return v1_parts > v2_parts

# Step 1: Download the repomd.xml
print("Downloading repomd.xml...")
repomd_url = os.path.join(REPO_URL, "repodata/repomd.xml")
download_file(repomd_url, "repomd.xml")

# Parse repomd.xml to find primary.xml.gz location
tree = ET.parse("repomd.xml")
root = tree.getroot()
namespace = {'repo': 'http://linux.duke.edu/metadata/repo'}

primary_location = root.find(".//repo:data[@type='primary']/repo:location", namespace).attrib['href']
print(f"Found primary.xml.gz at {primary_location}")

# Step 2: Download primary.xml.gz
primary_url = os.path.join(REPO_URL, primary_location)
print("Downloading primary.xml.gz...")
download_file(primary_url, "primary.xml.gz")

# Step 3: Extract primary.xml.gz
with gzip.open("primary.xml.gz", "rb") as f_in:
    with open("primary.xml", "wb") as f_out:
        f_out.write(f_in.read())

# Step 4: Parse primary.xml to find the latest version of each package
tree = ET.parse("primary.xml")
root = tree.getroot()
namespace = {'common': 'http://linux.duke.edu/metadata/common'}

# Function to get the latest package version
def get_latest_package_version(package_name):
    latest_package = None
    latest_version = None

    # Search for packages in both x86_64 and noarch
    for arch in ARCHS:
        packages = root.findall(f".//common:package[common:name='{package_name}'][common:arch='{arch}']", namespace)
        for package in packages:
            version_element = package.find("common:version", namespace)
            ver = version_element.attrib['ver']  # Use version string
            if latest_version is None or compare_versions(ver, latest_version):
                latest_version = ver
                latest_package = package

    if latest_package is None:
        print(f"Error: No packages found for {package_name}")
        return None

    location_element = latest_package.find("common:location", namespace)
    package_path = location_element.attrib['href']
    return package_path

# Step 5: Download the latest package for each specified package
for package_name in PACKAGES:
    print(f"Finding the latest version of {package_name}...")
    package_path = get_latest_package_version(package_name)

    if package_path:
        # Download the latest package
        print(f"Downloading the latest {package_name} package: {package_path}")
        package_url = os.path.join(REPO_URL, package_path)
        rpm_file = os.path.basename(package_path)

        # Strip the long hash from the beginning
        clean_rpm_file = '-'.join(rpm_file.split('-')[1:])
        download_file(package_url, clean_rpm_file)

        print(f"Download complete: {clean_rpm_file}")

# Clean up
print("Cleaning up...")
os.remove("repomd.xml")
os.remove("primary.xml")
os.remove("primary.xml.gz")

print("All downloads complete.")

