# Multi-Vendor Firewall Backup Script
This script is designed to automate the backup process of configurations for Multi-Vendor Firewalls. It utilizes the Nornir framework along with Netmiko to retrieve and save configurations from Juniper (Junos OS and ScreenOS), Fortinet, and Cisco Firepower FTD devices. The script supports both RestAPI and SSH methods for retrieving configurations, making it versatile and adaptable to different firewall models.
### Prerequisites
Before using this script, ensure you have the following prerequisites in place:

#### Python Environment:

- Python 3.x installed on your machine.
- Required Python packages installed. You can install them using pip:
```console
pip install nornir netmiko
```

**Network Inventory:**

Create a YAML inventory file (inventory.yaml) with the details of your firewall devices. Here's a sample format:
```console
---
FW1:
  hostname: 192.168.1.112
  username: admin
  password: admin
  port: 22
  platform: juniper_junos
  data:
      site: 1
      role: firewall
      type: network_device

FW2:
  hostname: 192.168.1.113
  username: admin
  password: admin
  port: 22
  platform: fortinet
  data:
      site: 2
      role: firewall
      type: http
```
### Usage

Clone this GitHub repository to your local machine.

Update the inventory file (inventory.yaml) with your firewall device details.

Run the script using the following command:

```console
python MultivendorBackup.py
```
The script will connect to each device based on the provided inventory and retrieve and save their configurations in separate text files.
### Supported Vendors and Methods
**Vendors:**
Juniper:

-Junos OS

-ScreenOS
Fortinet

Cisco Firepower FTD

**Methods:**
RestAPI
SSH


![Screenshot 2022-08-22 160338](https://user-images.githubusercontent.com/75830370/185911967-e7b802ae-51a7-4643-812c-124f152bc18b.png)

