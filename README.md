# ansible_vsphere_change_vm_nic
Ansible module to change the NIC of a VMware VM

## Notice

The VM needs to already have one (and only one) NIC.

## Requirements

* pyvmomi
* Ansible

## How to use

Add this custom module to your Ansible library directory.

    - name: Change VM NIC
      vsphere_change_vm_nic:
        host: "{{esx_hostname}}"
        user: "{{esx_username}}"
        password: "{{esx_password}}"
        vm_name: "{{esx_VMname}}"
        network_name: "{{esx_nic_name}}"
        is_VDS: True


## TODO

* Module documentation
* Multi nic
* Add nic (not just change)

## Sponsor

Sentinelo (http://sentinelo.com/en/index.php)
