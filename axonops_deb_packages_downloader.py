#!/usr/bin/python3
import os
import urllib.request

# Set variables
APT_REPO_URL = "https://packages.axonops.com/apt"
DIST = "axonops-apt"
COMPONENT = "main"
PACKAGES = [
    "axon-server",
    "axon-agent",
    "axon-dash",
    "axon-dse5.1-agent",  # Ensure this is checked under amd64/arm64
    "axon-cassandra3.11-agent",
    "axon-cassandra4.0-agent",
    "axon-cassandra4.0-agent-jdk8",
    "axon-cassandra4.1-agent",
    "axon-cassandra4.1-agent-jdk8",
    "axon-cassandra5.0-agent"
]

# Separate architectures for cassandra and dse6.x packages (all architecture)
CASSANDRA_DSE6_ARCH = ["all"]
# Separate architectures for other packages (amd64 and arm64)
OTHER_ARCHS = ["amd64", "arm64"]

# Helper function to download files using urllib
def download_file(url, dest):
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}
        request = urllib.request.Request(url, headers=headers)
        with urllib.request.urlopen(request) as response:
            with open(dest, 'wb') as out_file:
                out_file.write(response.read())
        print(f"Downloaded {url} to {dest}")
        return True
    except urllib.error.URLError as e:
        print(f"Failed to download {url}: {e.reason}")
        return False

# Version comparison by splitting and comparing each part as an integer
def compare_versions(version1, version2):
    v1_parts = list(map(int, version1.split('.')))
    v2_parts = list(map(int, version2.split('.')))
    return v1_parts > v2_parts

# Determine which architectures to use based on package name
def get_architectures_for_package(package_name):
    # Only cassandra and dse6.x packages should be searched in the 'all' architecture
    if "cassandra" in package_name or ("dse" in package_name and "6." in package_name):
        return CASSANDRA_DSE6_ARCH
    else:
        return OTHER_ARCHS

# Step 1: Download and search through all architectures
def download_packages_for_arch(arch):
    packages_url = f"{APT_REPO_URL}/dists/{DIST}/{COMPONENT}/binary-{arch}/Packages"
    print(f"Downloading {packages_url} for architecture {arch}...")
    return download_file(packages_url, f"Packages_{arch}")

# Step 2: Parse the Packages file to find the latest version of each package
def get_latest_package_version(package_name, arch):
    with open(f"Packages_{arch}", "r") as f:
        lines = f.readlines()

    current_package = {}
    latest_version = None
    latest_package = None

    # Loop through the lines in the Packages file
    for line in lines:
        if line.startswith("Package: "):
            current_package["name"] = line.split(": ")[1].strip()
        elif line.startswith("Version: "):
            current_package["version"] = line.split(": ")[1].strip()
        elif line.startswith("Architecture: "):
            current_package["arch"] = line.split(": ")[1].strip()
        elif line.startswith("Filename: "):
            current_package["filename"] = line.split(": ")[1].strip()

        # Check if we have all required fields
        if all(key in current_package for key in ["name", "version", "arch", "filename"]):
            if current_package["name"] == package_name and current_package["arch"] == arch:
                # Compare versions numerically
                if latest_version is None or compare_versions(current_package["version"], latest_version):
                    latest_version = current_package["version"]
                    latest_package = current_package.copy()
            current_package = {}  # Reset for next package

    if latest_package:
        return latest_package
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
                cleaned_filename = deb_file.split('_')[0] + '_' + deb_file.split('_')[1] + '_' + deb_file.split('_')[2] + '.deb'

                # Download the latest .deb file
                print(f"Downloading {cleaned_filename} from {deb_url}...")
                download_file(deb_url, cleaned_filename)
                print(f"Download complete: {cleaned_filename}")

# Clean up
print("Cleaning up...")
for arch in set(CASSANDRA_DSE6_ARCH + OTHER_ARCHS):
    if os.path.exists(f"Packages_{arch}"):
        os.remove(f"Packages_{arch}")

print("All downloads complete.")

