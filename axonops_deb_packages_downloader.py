#!/usr/bin/python3
import os
import requests
import re
from packaging import version
import difflib

# Set variables
APT_REPO_URL = "https://packages.axonops.com/apt"
DIST = "axonops-apt"
COMPONENT = "main"
PACKAGES = [
    "axon-server",
    "axon-agent",
    "axon-dash",
    "axon-dse5.1-agent",
    "axon-cassandra3.11-agent",
    "axon-cassandra4.0-agent",
    "axon-cassandra4.0-agent-jdk8",
    "axon-cassandra4.1-agent",
    "axon-cassandra4.1-agent-jdk8",
    "axon-cassandra5.0-agent"
]

# Separate architectures for packages
CASSANDRA_DSE_ARCH = ["all"]
OTHER_ARCHS = ["amd64", "arm64"]

# Helper function to download files
def download_file(url, dest):
    response = requests.get(url, stream=True)
    if response.status_code == 200:
        with open(dest, 'wb') as f:
            f.write(response.content)
    else:
        print(f"Failed to download {url}. Status code: {response.status_code}")
        return False
    return True

# Determine which architectures to use based on package name
def get_architectures_for_package(package_name):
    if "cassandra" in package_name or "dse" in package_name:
        return CASSANDRA_DSE_ARCH
    else:
        return OTHER_ARCHS

# Step 1: Download and search through all architectures
def download_packages_for_arch(arch):
    packages_url = f"{APT_REPO_URL}/dists/{DIST}/{COMPONENT}/binary-{arch}/Packages"
    print(f"Downloading {packages_url} for architecture {arch}...")
    if not download_file(packages_url, f"Packages_{arch}"):
        print(f"Error: Unable to download {packages_url}.")
        return False
    return True

# Step 2: Parse the Packages file to find the latest version of each package
def get_latest_package_version(package_name, arch):
    with open(f"Packages_{arch}", "r") as f:
        lines = f.readlines()

    # Regular expression to match package entries
    current_package = {}
    package_regex = re.compile(r"^Package: (.+)$")
    version_regex = re.compile(r"^Version: (.+)$")
    arch_regex = re.compile(r"^Architecture: (.+)$")
    filename_regex = re.compile(r"^Filename: (.+)$")

    latest_version = None
    latest_package = None

    # List of found package names for fuzzy matching
    available_packages = []

    # Loop through the lines in the Packages file
    for line in lines:
        # Find package name
        package_match = package_regex.match(line)
        if package_match:
            current_package["name"] = package_match.group(1)
            available_packages.append(current_package["name"])  # Collect for fuzzy matching
        
        # Find version
        version_match = version_regex.match(line)
        if version_match:
            current_package["version"] = version_match.group(1)
        
        # Find architecture
        arch_match = arch_regex.match(line)
        if arch_match:
            current_package["arch"] = arch_match.group(1)
        
        # Find filename (URL path to the .deb file)
        filename_match = filename_regex.match(line)
        if filename_match:
            current_package["filename"] = filename_match.group(1)
        
        # If we have a complete package entry, compare the version and update if necessary
        if all(key in current_package for key in ["name", "version", "arch", "filename"]):
            if current_package["name"] == package_name and current_package["arch"] == arch:
                current_version = current_package["version"]
                # Use packaging.version to ensure correct version comparison
                if latest_version is None or version.parse(current_version) > version.parse(latest_version):
                    latest_version = current_version
                    latest_package = current_package.copy()

            # Reset current_package for the next package entry
            current_package = {}

    if latest_package:
        return latest_package
    else:
        # Attempt to fuzzy match package name if no exact match was found
        closest_match = difflib.get_close_matches(package_name, available_packages, n=1, cutoff=0.7)
        if closest_match:
            print(f"Warning: No exact match found for {package_name} in {arch}, but found a close match: {closest_match[0]}")
        else:
            print(f"Error: No valid versions found for {package_name} (searched in {arch})")
        return None

# Step 3: Download the latest version of each package from appropriate architectures
for package_name in PACKAGES:
    archs = get_architectures_for_package(package_name)
    for arch in archs:
        if download_packages_for_arch(arch):
            print(f"Finding the latest version of {package_name} in {arch}...")
            package_info = get_latest_package_version(package_name, arch)

            if package_info:
                package_path = package_info["filename"]
                deb_url = f"{APT_REPO_URL}/{package_path}"
                deb_file = os.path.basename(package_path)

                # Clean the filename by removing the hash or long string towards the end
                cleaned_filename = re.sub(r'_[a-f0-9]+\.deb$', '.deb', deb_file)

                # Download the latest .deb file
                print(f"Downloading {cleaned_filename} from {deb_url}...")
                download_file(deb_url, cleaned_filename)
                print(f"Download complete: {cleaned_filename}")

# Clean up
print("Cleaning up...")
for arch in set(CASSANDRA_DSE_ARCH + OTHER_ARCHS):
    if os.path.exists(f"Packages_{arch}"):
        os.remove(f"Packages_{arch}")

print("All downloads complete.")

