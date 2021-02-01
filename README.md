# Ansible Collection - respiro.illumio

This is a collection of Ansible modules to manage workloads in Illumio PCE. This is the initial version and more modules will be added in the future.

## Installation

To use the ansible modules, you have to install the following python modules.

```
pip install requests
```
This collections is packaged under ansible-galaxy, so to install it you need to run the following command:

```
ansible-galaxy collection install respiro.illumio
```

## Features

* Add unmanaged workloads to PCE
* Add managed workload to PCE * 
* Assign labels to workloads (both managed & unmanaged)
* Add single label data to Illumio PCE
* Add multiple label data using csv file
* Get the list of labels from PCE
* Update the name (value) of existing label

***NOTES:***

  *: Although this is technically not a feature built in to this collection, it is still required to enable some modules to function correctly, instruction will be provided below, no prerequisite required

## Modules

* ``` create_label  ```: This module adds labels to PCE. User can add single label information by supplying the type and name of the label or add multiple labels by giving the path to the CSV file.
* ``` display_label_info  ```: This module retrieves label information from PCE
* ``` create_umw  ```: Adds the unmanaged workloads from the CSV file to PCE and assigned labels from the same CSV file
* ``` assign_labels  ```: This module assigns labels to workloads.
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

* To assign/edit workloads' labels

```csv
hostname,role,app,env,loc
<workload hostname>,<role label>,<application label>,<environment label>,<location label>
<workload hostname>,<role label>,<application label>,<environment label>,<location label>
.
.
```
## Examples: using the modules
Here are some of the example of using the modules

All modules are ran through **localhost**

<br>

* **To get label data from PCE**

```yaml
---
- name: Get label info
  hosts: localhost
  tasks:
    - name: Display the list of label
      respiro.illumio.display_label_info:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "poc1.illum.io"
        org_id: "80"
        type: "all"
      register: data

    - name: output data
      debug:
        msg: '{{ data }}'
```

<br>

---

<br>

* **To add labels to PCE using csv file**

```yaml
---
- name: Add label from csv file to PCE
  hosts: localhost
  tasks:
    - name: Add label to PCE
      respiro.illumio.create_label:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "poc1.illum.io"
        org_id: "80"
        path: "label.csv"
      register: data 

    - name: output data
      debug:
        msg: '{{ data }}'
```

<br>

---

<br>

* **To add single label information to PCE**

```yaml
---
- name: Add single label to PCE
  hosts: localhost
  tasks:
    - name: Add label to PCE
      respiro.illumio.create_label:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "poc1.illum.io"
        org_id: "80"
        type: "loc"
        name: "new_location"
      register: data 

    - name: output data
      debug:
        msg: '{{ data }}'
```

<br>

---

<br>

* **To add unmanaged workloads with labels to PCE**

Please note that unmanaged workloads can't be upgraded into managed workload, user will need to follow 
intructions below to create a managed workload

```yaml
---
- name: Add unmanaged workload
  hosts: localhost
  tasks:
    - name: Add workload to PCE
      respiro.illumio.create_umw:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "poc1.illum.io"
        org_id: "80"
        workload: "unmanaged_workload.csv"
      register: data 

    - name: output data
      debug:
        msg: '{{ data }}'
```

<br>

---

<br>

* **To add managed workload to PCE** 

All that required for any OS (virtual or physical) to become a managed workload is to have 
a VEN installed on it using the script provided by the PCE

1. First head to PCE and create a Pairing Profile (Pairing Profile is a configuration that allow user 
to apply properties to the workload as they pair with the PCE; Labels, policies, etc. are applied this way)

2. Generate a pairing key/activation code for that Profile

3. A pairing script containing the key will be generated automatically once the key is created

4. Copy the script (for Windows or Linux)

5. Run the script on target machine

    - For Windows: run on **PowerShell** (`win_shell`) as **Administrator** (`become: true`)

    - For Linux: run on **Linux CLI** (`script`) as **Root** (`become: true`)

6. The VEN will automatically pair the machine to the PCE if the installation is successful<br>

<br>

The newly added machine displayed on the PCE will get all the information the VEN collected:

* Name (taken from the name of the machine)

* Interfaces

* IP

* OS

* ...

* ...

* **Labels** and **policies** are dictated by the Pairing Profile<br>

<br>

Please note that managed workload can't be downgraded into unmanaged workload, 
unpairing the VEN will remove the workload from the PCE

The example below is for **Linux**, the code will need to be adapted to work for Windows

*This script will need to be run on **target machines** instead of localhost, required ssh connection* 

```yaml
---
- name: setup managed workload
  hosts: test_server
  tasks:
    - name: install VEN on linux machine
      become: true
      script: "linux_script.sh"
      register: test_output

    - name: dump test output
      debug:
        msg: '{{ test_output }}'
```

<br>

---

<br>

* **Adding unmanaged and managed workloads in the same playbook**

    * The **hosts** should be the intended managed workloads (target machines to installed pairing script)

    * The task for unmanaged workload required `delegate_to: localhost` to only activate on localhost

    * The task for installing VEN required `become: true` to act as root or administrator

```yaml
---
- name: adding workloads
  hosts: test_server
  tasks:
    - name: add an umw to the pce
      respiro.illumio.create_umw:
        pce: "poc1.illum.io"
        org_id: "86"
        username: "api_1e454dv85ev8d18b"
        auth_secret: "ff5df1ef552397878frfr8758r8tgf5d6e"
        workload: "test_addingUMW.csv"
      delegate_to: localhost
      register: test_output

    - name: dump test output
      debug:
        msg: '{{ test_output }}'

    - name: install VEN on linux machine
      become: true
      script: "linux_script.sh"
      register: test_output

    - name: dump test output
      debug:
        msg: '{{ test_output }}'
```

<br>

---

<br>

* **Assign labels to workloads**

```yaml
---
- name: Assign labels to workloads
  hosts: localhost
  tasks:
    - name: Assign labels to workloads
      respiro.illumio.assign_labels:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "poc1.illum.io"
        org_id: "80"
        workload: 'workload.csv'
      register: data

    - name: output data
      debug:
        msg: '{{ data }}'
```

<br>

---

<br>

* **Creating workloads and assigning labels in the same playbook**

    * It's recommended that a pause of approximately 8-15 seconds should take place right after the tasks used to create workloads (both managed and unmanaged); This allows the PCE some times to update the new information to the system

    * Without the pause, there is a high chance that the labels won't be applied (since the new workloads wasn't updated yet) and user will need to rerun the task to assign labels

```yaml
---
- name: adding workloads and assigning labels
  hosts: localhost
  tasks:
    - name: add an umw to the pce
      respiro.illumio.create_umw:
        pce: "poc1.illum.io"
        org_id: "86"
        username: "api_1e454dv85ev8d18b"
        auth_secret: "ff5df1ef552397878frfr8758r8tgf5d6e"
        workload: "test_addingUMW.csv"
      register: test_output

    - name: dump test output
      debug:
        msg: '{{ test_output }}'

    - name: Pause to allow time for the PCE to update new information
      pause:
        seconds: 15

    - name: Assign labels to workloads
      respiro.illumio.assign_labels:
        username: "api_12321323cf4545"
        auth_secret: "097jhdjksb9387384hjd3384bnfj93"
        pce: "poc1.illum.io"
        org_id: "80"
        workload: 'workload.csv'
      register: data

    - name: output data
      debug:
        msg: '{{ data }}'
```

<br>

---

<br>

* **Update existing label's name**

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






