# Ansible Collection - respiro.illumio

This is a collection of Ansible modules to manage workloads in PCE. This is the initial version of the collection containing modules to add new labels, retrieve labels, and add unmanaged workloads to Illumio PCE. 

## Installation

To use the modules, you have to install the request module, aiohttp module.

```
pip install requests
```
```
pip install aiohttp
```
This collections is packaged under ansible-galaxy, so to install it you need to run following command:

```ansible
ansible-galaxy collection install respiro.illumio
```

## Features

* Add single label data to Illumio PCE
* Add multiple label data using csv file
* Get the list of labels in Illumio PCE
* Add unmanaged workloads to Illumio PCE
* Assign labels to unmanaged workloads to Illumio PCE

## Modules

* ``` create_label  ```: This module adds labels to PCE. User can add single label information by supplying the type and name of the label or add multiple labels by giving the path to the CSV file.
* ``` display_label_info  ```: This module retrieves label information from PCE
* ``` create_umw  ```: Adds the unmanaged workloads from the CSV file to PCE and assigned labels from the same CSV file

## CSV file format

* To add labels to PCE, the following CSV file format must be followed:

```csv
type,name
<type>,<name>
<type>,<name>
.
.
.
```

* To add unmanaged workloads to PCE, the following CSV file format must be followed:

```csv
name,hostname,username,password,ip,role,app,env,loc
<workload name>,<workload hostname>,<workload login>,<workload password>,<ip>,<role_label>,<app_label>,<env_label>,<loc_label>
<workload name>,<workload hostname>,<workload login>,<workload password>,<ip>,<role_label>,<app_label>,<env_label>,<loc_label>
.
.
.
```
## Examples: using the modules
Here are some of the example of using the modules

```yaml
---
name: Display label info
hosts: localhost
tasks:
 - name: Display the list of label
   respiro.illumio.display_label_info:
      user: "api_12321323cf4545"
      password: "097jhdjksb9387384hjd3384bnfj93"
      pce: "https://poc1.illum.io"
      org_href: "orgs/80"
      type: "all"
   register: data

 - name: output data
   debug:
      msg: '{{ data }}'
```

```yaml
---
name: Add label to PCE
hosts: localhost
tasks:
 - name: Add label to PCE
   respiro.illumio.create_label:
     user: "api_12321323cf4545"
     password: "097jhdjksb9387384hjd3384bnfj93"
     pce: "https://poc1.illum.io"
     org_href: "orgs/80"
     path: "label.csv"
   register: data 

 - name: output data
   debug:
      msg: '{{ data }}'
```
```yaml
---
name: Add unmanaged workload
hosts: localhost
tasks:
 - name: Add workload to PCE
   respiro.illumio.create_umw:
     user: "api_12321323cf4545"
     password: "097jhdjksb9387384hjd3384bnfj93"
     pce: "https://poc1.illum.io"
     org_href: "orgs/80"
     workload: "unmanaged_workload.csv"
   register: data 

 - name: output data
   debug:
      msg: '{{ data }}'
```






