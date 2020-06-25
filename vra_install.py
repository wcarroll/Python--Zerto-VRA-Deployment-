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
base_url = "https://"+zvm_ip+":9669/v1"
session = base_url+"/session/add"
vrainstall_url = base_url+"/vras"

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
with open('File location for vras.json', 'r') as f:
   vra_configuration = json.load(f)
f.closed


#Iterate through each host listed in vras JSON
#Gather MoRefs, IPs to POST JSON request 

for host in vra_configuration: 
   datastore_name = vra_configuration.get(host)[0].get('DatastoreName')
   network_name = vra_configuration.get(host)[0].get('PortGroup')
   host_name = host
   memory = vra_configuration.get(host)[0].get('MemoryGB')
   vra_group = vra_configuration.get(host)[0].get('VRAGroup')
   vra_gateway = vra_configuration.get(host)[0].get('StaticInfo')[0]['DefaultGateway']
   vra_subnet = vra_configuration.get(host)[0].get('StaticInfo')[1]['SubnetMask']
   vra_ip = vra_configuration.get(host)[0].get('StaticInfo')[2]['VRAIPAddress']

   #Iterate through all networks returned by Zerto to find MoRef
   for network in network_ids: 
      if network['VirtualizationNetworkName'] == network_name:
         network_moref = network['NetworkIdentifier']
      else: 
         pass
   #Iterate through all hosts returned by Zerto to find MoRef    
   for host in host_ids: 
      if host['VirtualizationHostName'] == host_name: 
         host_moref = host['HostIdentifier']
      else: 
         pass
   #Iterate through all datastores returned by Zerto to find MoRef    
   for datastore in datastore_ids: 
      if datastore['DatastoreName'] == datastore_name:
         datastore_moref = datastore['DatastoreIdentifier']
      else: 
         pass

   #Build VRA dict containing morefs and static IPs
   vra_dict = {
      "DatastoreIdentifier":  datastore_moref,
      "GroupName": vra_group ,
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

   #Convert VRA dict to JSON, post request for install to /vras
   vra_json = json.dumps(vra_dict)
   response = requests.post(vrainstall_url, data=vra_json, headers=headers, verify=False)
   if response.status_code != 200:
      print(response.text)
   #Figure out a way to sleep 30 seconds
   #Print out json status code response 
print("")

