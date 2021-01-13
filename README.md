# Ansible Collection - respiro.illumio

This is a collection of Ansible modules to manage workloads in Illumio PCE. This is the initial version and more modules will be added in the future.

## Installation

To use the ansible modules, you have to install the following python modules.

```
pip install requests
pip install aiohttp
pip install pypsexec
pip install paramiko
pip install asyncio
```
This collections is packaged under ansible-galaxy, so to install it you need to run following command:

```
ansible-galaxy collection install respiro.illumio
```

## Features

* Add unmanaged workloads to PCE
* Assign labels to unmanaged workloads
* Add managed workload to PCE * 
* Assign labels to managed workload ** 
* Add single label data to Illumio PCE
* Add multiple label data using csv file
* Get the list of labels from PCE
* Update the name (value) of existing label

***NOTES:***

  *: Although this is technically not a feature built in to this collection, it is still required to enable some modules to function correctly, instruction will be provided below, no prerequisite required

  **: Will only work if the Pairing Profile applied to this managed workload allow  

## Modules

* ``` create_label  ```: This module adds labels to PCE. User can add single label information by supplying the type and name of the label or add multiple labels by giving the path to the CSV file.
* ``` display_label_info  ```: This module retrieves label information from PCE
* ``` create_umw  ```: Adds the unmanaged workloads from the CSV file to PCE and assigned labels from the same CSV file
* ``` assign_managed_labels  ```: This module assigns labels to managed workloads.
* ``` update_label ```: This module updates existing label's name

## CSV file format

Following is the minimum file format requirements for csv file

* To add labels to PCE

```csv
type,name
<type>,<name>
<type>,<name>
.
.
```

* To add unmanaged workloads to PCE with labels

```csv
name,hostname,ip,role,app,env,loc
<name>,<workload hostname>,<ip>,<role label>,<application label>,<environment label>,<location label>
<name>,<workload hostname>,<ip>,<role label>,<application label>,<environment label>,<location label>
.
.
```

* To add managed workloads to PCE

```csv
username,password,ip,os
<workload login username>,<workload password>,<workload ip>,<operating system>
<workload login username>,<workload password>,<workload ip>,<operating system>
.
.
```

* To assign labels to managed workloads

```csv
ip,role,app,env,loc
<managed workload ip>,<role label>,<application label>,<environment label>,<location label>
<managed workload ip>,<role label>,<application label>,<environment label>,<location label>
.
.
```
## Examples: using the modules
Here are some of the example of using the modules

* To get label data from PCE

```yaml
---
- name: Get label info
  hosts: localhost
  tasks:
    - name: Display the list of label
      respiro.illumio.display_label_info:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "https://poc1.illum.io"
        org_id: "80"
        type: "all"
      register: data

    - name: output data
      debug:
         msg: '{{ data }}'
```
* To add labels to PCE using csv file

```yaml
---
- name: Add label from csv file to PCE
  hosts: localhost
  tasks:
    - name: Add label to PCE
      respiro.illumio.create_label:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "https://poc1.illum.io"
        org_id: "80"
        path: "label.csv"
      register: data 

    - name: output data
      debug:
         msg: '{{ data }}'
```
* To add single label information to PCE 

```yaml
---
- name: Add single label to PCE
  hosts: localhost
  tasks:
    - name: Add label to PCE
      respiro.illumio.create_label:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "https://poc1.illum.io"
        org_id: "80"
        type: "loc"
        name: "new_location"
      register: data 

    - name: output data
      debug:
        msg: '{{ data }}'
```
* To add unmanaged workloads with labels to PCE 

```yaml
---
- name: Add unmanaged workload
  hosts: localhost
  tasks:
    - name: Add workload to PCE
      respiro.illumio.create_umw:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "https://poc1.illum.io"
        org_id: "80"
        workload: "unmanaged_workload.csv"
      register: data 

    - name: output data
      debug:
        msg: '{{ data }}'
```
* Deploy VEN to workoads from csv file 

```yaml
---
- name: Deploy VEN to workloads from csv file
  hosts: localhost
  tasks:
    - name: Deploy VEN
      respiro.illumio.assign_ven:
        workload: 'workload.csv'
        linux_script: 'linuxPairing.sh'
      register: data

    - name: output data
      debug:
        msg: '{{ data }}'
```
* Assign labels to managed workoads

```yaml
---
- name: Assign labels to managed workloads
  hosts: localhost
  tasks:
    - name: Assign labels to VEN installed workloads
      respiro.illumio.assign_managed_labels:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "https://poc1.illum.io"
        org_id: "80"
        workload: 'workload.csv'
      register: data

    - name: output data
      debug:
        msg: '{{ data }}'
```
* Update existing label's name

```yaml
---
- name: Update a label
  hosts: localhost
  tasks:
  - name: update label
    respiro.illumio.update_label:
      pce: "poc1.illum.io"
      port: "8443"
      org_id: "80"
      label_id: "439151"
      username: "api_15df8c15v1d8"
      auth_secret: "54gf845v48rwe8wc548v8hr85d9abbe86a6555f8v8w8m85yh8yyy8h"
      new_value: "testing_0"
    register: test_output
  - name: dump test output
    debug:
      msg: '{{ test_output }}'
```






