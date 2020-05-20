#importing request, json
#importing HTTPBasicAuth library for ZVM basic authentication 
import requests 
import json 
from requests.auth import HTTPBasicAuth
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

#Declaring Environment variables 
zvm_ip = "192.168.111.20"
zvm_u = "administrator@vsphere.local"
zvm_p = "Zertodata1!" 
base_url = "https://"+zvm_ip+":9669/v1"
session = base_url+"/session/add"

###Functions####
def login(session_url, zvm_user, zvm_password):
   print("Getting ZVM API token...")
   auth_info = "{\r\n\t\"AuthenticationMethod\":1\r\n}"
   headers = {
     'Accept': 'application/json',
     'Content-Type': 'application/json'
   }
   response = requests.post(session_url, headers=headers, data=auth_info, verify=False, auth=HTTPBasicAuth(zvm_user, zvm_password))
   if response.ok: 
      auth_token = response.headers['x-zerto-session']
      print("Api Token: " + auth_token)
      return auth_token
   else: 
      print("HTTP %i - %s, Message %s" % (response.status_code, response.reason, response.text))   

returned_token = login(session, zvm_u, zvm_p)

# Creating Header with x-zerto-session 
headers = {
   'Accept': 'application/json',
   'Content-Type': 'application/json',
   'x-zerto-session': returned_token
}

#Gather ZVM Site ID for future use
site_url = base_url+"/localsite"
site_return = requests.get(site_url, headers=headers, verify=False)
site_return = site_return.json()
site_id = site_return.get('SiteIdentifier')

#Gather network IDs for future use
network_url = base_url + "/virtualizationsites/"+site_id+"/networks"
network_ids = requests.get(network_url, headers=headers, verify=False)
network_ids = network_ids.json()

#Gather host IDs for future use
host_url = base_url + "/virtualizationsites/"+site_id+"/hosts"
host_ids = requests.get(host_url, headers=headers, verify=False)
host_ids = host_ids.json()

#Gather Datastore IDs for future use
datastore_url = base_url + "/virtualizationsites/"+site_id+"/datastores"
datastore_ids = requests.get(datastore_url, headers=headers, verify=False)
datastore_ids = datastore_ids.json()

#Read in JSON configuration file 
with open('C:\\Users\\shaun.finn\\Documents\\SME Role\\Automation\\Deployment\\vra.json', 'r') as f:
   vra_configuration = json.load(f)
f.closed

#Convert configuration to list 
hostnamelist = []


for host in vra_configuration['Hosts']: 
   hostnamelist.append(host)
   count = hostnamelist.count["ESXiHostName"]
   #count = len(hostnamelist["ESXiHostName"])
   #print(hostnamelist["ESXiHostName"][:])

print("")