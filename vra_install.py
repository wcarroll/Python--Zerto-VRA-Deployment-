#This script is an example script and is not supported under any Zerto support program or service. The author and Zerto further disclaim all implied warranties including, without
#limitation, any implied warranties of merchantability or of fitness for a particular purpose.

#In no event shall Zerto, its authors or anyone else involved in the creation, production or delivery of the scripts be liable for any damages whatsoever (including, without 
#limitation, damages for loss of business profits, business interruption, loss of business information, or other pecuniary loss) arising out of the use of or the inability to use
#the sample scripts or documentation, even if the author or Zerto has been advised of the possibility of such damages. The entire risk arising out of the use or performance of 
#the sample scripts and documentation remains with you.

#importing request, json
#importing HTTPBasicAuth library for ZVM basic authentication 
import requests 
import json
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
from time import sleep

#Declaring Environment variables 
zvm_ip = "ZVM IP"
zvm_u = "ZVM user"
zvm_p = "ZVM password" 
base_url = f"https://{zvm_ip}:9669/v1"
session = f"{base_url}/session/add"
vrainstall_url = f"{base_url}/vras"

###Functions####
def login(session_url, zvm_user, zvm_password):
    print("Getting ZVM API token...")
    auth_info = "{\r\n\t\"AuthenticationMethod\":1\r\n}"
    headers = {
        'Accept': 'application/json',
        'Content-Type': 'application/json'
    }
    response = requests.post(session_url, headers=headers, data=auth_info,
                             verify=False, auth=HTTPBasicAuth(zvm_user, zvm_password))
    if response.ok:
        auth_token = response.headers['x-zerto-session']
        print(f"Api Token: {auth_token}")
        return auth_token
    else:
        print(
            f"HTTP {response.status_code} - {response.reason}, Message {response.text}")

def get_identifiers(url: str, headers: dict):
    results = requests.get(url, headers=headers, verify=False)
    if results.ok:
        return results.json()
    else:
        raise ConnectionError


def get_moref(name: str, identifiers: dict, name_key: str, identifier_key: str):
    for myid in identifiers:
        if myid[name_key] == name:
            return myid[identifier_key]
    return None


returned_token = login(session, zvm_u, zvm_p)

# Creating Header with x-zerto-session 
headers = {
   'Accept': 'application/json',
   'Content-Type': 'application/json',
   'x-zerto-session': returned_token
}

# Gather ZVM Site ID for future use
site_url = f"{base_url}/localsite"
site_return = get_identifiers(site_url, headers)
site_id = site_return.get('SiteIdentifier')

# Gather network IDs for future use
network_url = f"{base_url}/virtualizationsites/{site_id}/networks"
network_ids = get_identifiers(network_url, headers)


# Gather host IDs for future use
host_url = f"{base_url}/virtualizationsites/{site_id}/hosts"
host_ids = get_identifiers(host_url, headers)

# Gather Datastore IDs for future use
datastore_url = f"{base_url}/virtualizationsites/{site_id}/datastores"
datastore_ids = get_identifiers(datastore_url, headers)


# Read in JSON configuration file
with open(configuration_file, 'r') as f:
    vra_configuration = json.load(f)
f.closed


# Iterate through each host listed in vras JSON
# Gather MoRefs, IPs to POST JSON request

for host in vra_configuration['Hosts']:
    datastore_name = host['DatastoreName']
    network_name = host['PortGroup']
    host_name = host['HostName']
    memory = host['MemoryGB']
    vra_group = host['VRAGroup']
    vra_gateway = host['DefaultGateway']
    vra_subnet = host['SubnetMask']
    vra_ip = host['VRAIPAddress']

    # Get each MoRef ID for each required element
    network_moref = get_moref(
        network_name,
        network_ids,
        'VirtualizationNetworkName',
        'NetworkIdentifier'
    )
    host_moref = get_moref(
        host_name,
        host_ids,
        'VirtualizationHostName',
        'HostIdentifier'
    )
    datastore_moref = get_moref(
        datastore_name,
        datastore_ids,
        'DatastoreName',
        'DatastoreIdentifier'
    )
    vra_dict = {
        "DatastoreIdentifier":  datastore_moref,
        "GroupName": vra_group,
        "HostIdentifier":  host_moref,
        "HostRootPassword": None,
        "MemoryInGb":  memory,
        "NetworkIdentifier":  network_moref,
        "UsePublicKeyInsteadOfCredentials": True,
        "VraNetworkDataApi":  {
            "DefaultGateway":  vra_gateway,
            "SubnetMask":  vra_subnet,
            "VraIPAddress":  vra_ip,
            "VraIPConfigurationTypeApi":  "Static"
        }
    }

    # Convert VRA dict to JSON, post request for install to /vras
    vra_json = json.dumps(vra_dict)
    response = requests.post(
        vrainstall_url, data=vra_json, headers=headers, verify=False)
    if response.status_code != 200:
        print(response.text)
    sleep(5)
    # Print out json status code response
print("")
