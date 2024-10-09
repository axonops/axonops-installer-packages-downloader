# axonops-installer-packages-downloader

AxonOps installation is generally performed using either YUM or APT package managers as described in https://axonops.com/docs/installation-starter/axon-server/axonserver_install/.

In some cases, you may be interested in downloading the latest packages from these repositories. The scripts in this project allow you to download the packages from the AxonOps repositories.

## Requirements
Python3 is installed on your machine.

## YUM - RPM Packages Downloader
Use the following set of commands to download the latest AxonOps packages to your machine.
```
python3 axonops_rpm_packages_downloader.py
```

## APT - DEB Packages Downloader
Use the following set of commands to download the latest AxonOps packages to your machine.
```
python3 axonops_deb_packages_downloader.py
```
