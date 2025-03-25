# AxonOps installers download script

[AxonOps](https://axonops.com/) installation is generally performed using either YUM or APT package managers as described in https://axonops.com/docs/installation-starter/axon-server/axonserver_install/.

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
***

*This project may contain trademarks or logos for projects, products, or services. Any use of third-party trademarks or logos are subject to those third-party's policies. AxonOps is a registered trademark of AxonOps Limited. Apache, Apache Cassandra, Cassandra, Apache Spark, Spark, Apache TinkerPop, TinkerPop, Apache Kafka and Kafka are either registered trademarks or trademarks of the Apache Software Foundation or its subsidiaries in Canada, the United States and/or other countries. Elasticsearch is a trademark of Elasticsearch B.V., registered in the U.S. and in other countries. Docker is a trademark or registered trademark of Docker, Inc. in the United States and/or other countries.*
