from platform import platform
import requests
import os
import sys
import datetime
from nornir import InitNornir
from nornir_netmiko.tasks import netmiko_send_command
from nornir_utils.plugins.functions import print_result
from nornir.core.task import Result
from nornir.core.exceptions import NornirExecutionError
import logging
import urllib3


os.chdir(os.path.dirname(os.path.abspath(sys.argv[0])))
path = os.getcwd()


def make_api_request(url, method, headers=None, data=None):
    try:
        if method == 'GET':
            response = requests.get(
                url, verify=False, headers=headers, timeout=10)
        elif method == 'POST':
            response = requests.post(
                url, verify=False, headers=headers, data=data, timeout=10)
        elif method == 'DELETE':
            response = requests.delete(
                url, verify=False, headers=headers, data=data, timeout=10)
        else:
            raise ValueError("Invalid HTTP method")

        if response.status_code in (500, 404, 403):
            return response

        response.raise_for_status()
        return response
    except requests.exceptions.RequestException as http_error:
        print(f"An error occurred: {http_error}")
        return None


# Function to write data to text based file
def save_config_to_file(dev_type, hostname, config):
    filename = f"{hostname}_{dateTime}.cfg"
    try:
        if dev_type == "ssh":
            with open(os.path.join(BACKUP_DIR, filename), "w", encoding="utf-8") as config_file:
                config_file.write(config)
            print(f"{hostname} >>> backup file was created successfully!")
            config_file.close()
        elif dev_type == "http":
            urllib3.disable_warnings()
            with open(os.path.join(BACKUP_DIR, filename), "wb") as config_file:
                config_file.write(config.content)
            print(f"{hostname} >>> backup file was created successfully!")
            config_file.close()
        else:
            print("Unsupported device type!")
    except FileNotFoundError as write_error:
        print(write_error)


def get_juniper_backups() -> Result:
    print("**************************** Juniper_SSH ****************************")
    try:
        junos = nr.filter(platform="juniper_junos")
        screenos = nr.filter(platform="juniper_screenos")
        if junos.inventory.hosts:
            print(f"{junos.inventory.hosts} reading configuration. Please wait...")
            backup_results = junos.run(
                task=netmiko_send_command,
                command_string="show config | display set", read_timeout=120, severity_level=logging.DEBUG)
            print_result(backup_results)
            for host in backup_results:
                if host not in backup_results.failed_hosts:
                    save_config_to_file(
                        dev_type="ssh",
                        hostname=host,
                        config=backup_results[host][0].result,)
        if screenos.inventory.hosts:
            print(f"{screenos.inventory.hosts} reading configuration. Please wait...")
            screenos.run(task=netmiko_send_command,
                         command_string="set console page 0")
            backup_results = screenos.run(
                task=netmiko_send_command,
                # expect_string=r"--- more ---" >>>
                # After the get config command, we must enter the space key to continue displaying the output
                command_string="get config", expect_string=r">", read_timeout=120, severity_level=logging.DEBUG)
            screenos.run(task=netmiko_send_command,
                         command_string="unset console page")
            print_result(backup_results)
            for host in backup_results:
                if host not in backup_results.failed_hosts:
                    save_config_to_file(
                        dev_type="ssh",
                        hostname=host,
                        config=backup_results[host][0].result,)
        else:
            print("No device found!")
    except NornirExecutionError:
        print("Nornir Error")


# Function to get backup from fortinet device with API
def get_fortinet_backups() -> Result:
    print("**************************** Fortinet_HTTP ****************************")
    try:
        fortinet_http = nr.filter(platform="fortinet", type="http")
        if fortinet_http.inventory.hosts:
            for host in fortinet_http.inventory.hosts:
                print(host)
                hostname = fortinet_http.inventory.hosts[host].hostname
                port = fortinet_http.inventory.hosts[host].port
                access_token = fortinet_http.inventory.hosts[host].password
                forti_url = f"https://{hostname}:{port}/api/v2/monitor/system/config/backup?scope=global"
                # print(forti_url)
                headers = {"Authorization": "Bearer " + access_token, }
                data = make_api_request(forti_url, "GET", headers)
                if data.status_code == 200:
                    save_config_to_file(dev_type="http", hostname=host, config=data)
                else:
                    print(data.status_code, data.reason)
        else:
            print("No device found!")
    except NornirExecutionError as nornir_error:
        print("Nornir Error", nornir_error)


def get_fortinet_ssh_backup() -> Result:
    print("**************************** Fortinet_SSH ****************************")
    try:
        fortinet_ssh = nr.filter(platform="fortinet", type="ssh")
        if fortinet_ssh.inventory.hosts:
            print(
                f"{fortinet_ssh.inventory.hosts} reading configuration. Please wait...")
            backup_results = fortinet_ssh.run(
                task=netmiko_send_command,
                command_string="show full-configuration", read_timeout=120, severity_level=logging.DEBUG)
            # print(backup_results.failed)
            # print(f"{backup_results.failed_hosts.keys()[0]} failed!")
            print_result(backup_results)
            for host in backup_results:
                if host not in backup_results.failed_hosts:
                    save_config_to_file(
                        dev_type="ssh",
                        hostname=host,
                        config=backup_results[host][0].result,)
        else:
            print("No device found!")
    except NornirExecutionError:
        print("Nornir Error")


def get_cisco_ftd_backup() -> Result:
    print("**************************** Cisco_FTD_SSH ****************************")
    try:
        cisco_ftd = nr.filter(platform="cisco_ftd", type="ssh")
        if cisco_ftd.inventory.hosts:
            print(
                f"{cisco_ftd.inventory.hosts} reading configuration. Please wait...")
            backup_results = cisco_ftd.run(
                task=netmiko_send_command,
                command_string="show running-config", severity_level=logging.DEBUG)
            print_result(backup_results)
            for host in backup_results:
                if host not in backup_results.failed_hosts:
                    save_config_to_file(
                        dev_type="ssh",
                        hostname=host,
                        config=backup_results[host][0].result,)
        else:
            print("No device found!")
    except NornirExecutionError:
        print("Nornir Error")


if __name__ == "__main__":
    print(path)
    # For Linux ------------------------------------
    # nr = InitNornir('/PyScripts/Nornir/config.yaml',
    #             core={"raise_on_error": True})
    # BACKUP_DIR = "/Backup_Devices"
    # For Linux ------------------------------------
    nr = InitNornir('config.yaml')
    BACKUP_DIR = "."
    dateTime = datetime.datetime.today().strftime('%Y_%m_%d_%H_%M')
    get_juniper_backups()
    get_fortinet_backups()
    get_fortinet_ssh_backup()
    get_cisco_ftd_backup()
    
