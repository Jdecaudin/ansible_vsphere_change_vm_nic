#!/usr/bin/python

"""
Written by Julien Decaudin
Github: https://github.com/Jdecaudin/

Sponsored by : Sentinelo (http://sentinelo.com/en/index.php)

Highly inspired by :
https://github.com/vmware/pyvmomi-community-samples/blob/master/samples/change_vm_vif.py
From Reubenur Rahman
"""

import sys
import json
import atexit

from ansible.module_utils.basic import *

try:
  import pysphere
  from pysphere import *
  from pyVmomi import vim
  from pyVim.connect import SmartConnect, Disconnect
except ImportError:
  print "failed=true, msg=Pysphere module requiered"
  sys.exit(1)

def get_obj(content, vimtype, name):
  """
   Get the vsphere object associated with a given text name
  """
  obj = None
  container = content.viewManager.CreateContainerView(content.rootFolder, vimtype, True)
  for c in container.view:
    if c.name == name:
      obj = c
      break
  return obj

def main():
  module = AnsibleModule(
    argument_spec = dict(
      host         = dict(requred = True),
      user         = dict(required = True),
      password     = dict(required = True),
      vm_name      = dict(required = True),
      network_name = dict(required = True),
      is_VDS       = dict(required = True)
    )
  )

  host         = module.params.get('host')
  user         = module.params.get('user')
  password     = module.params.get('password')
  vm_name      = module.params.get('vm_name')
  network_name = module.params.get('network_name')
  is_VDS       = module.params.get('is_VDS')

  try:
    si = SmartConnect(host=host, user=user, pwd=password, port=443)
    atexit.register(Disconnect, si)
  except IOError, e:
    module.fail_json(msg = 'Failed to connect to %s: %s' % (host, e))

  content       = si.content
  vm            = get_obj(content, [vim.VirtualMachine], vm_name)
  device_change = []

  for device in vm.config.hardware.device:
    if isinstance(device, vim.vm.device.VirtualEthernetCard):
      nicspec                         = vim.vm.device.VirtualDeviceSpec()
      nicspec.operation               =  vim.vm.device.VirtualDeviceSpec.Operation.edit
      nicspec.device                  = device
      nicspec.device.wakeOnLanEnabled = True

      if not is_VDS:
        nicspec.device.backing            = vim.vm.device.VirtualEthernetCard.NetworkBackingInfo()
        nicspec.device.backing.network    = get_obj(content, [vim.Network], network_name)
        nicspec.device.backing.deviceName = network_name
      else:
        network                          = get_obj(content, [vim.dvs.DistributedVirtualPortgroup], network_name)
        dvs_port_connection              = vim.dvs.PortConnection()
        dvs_port_connection.portgroupKey = network.key
        dvs_port_connection.switchUuid   = network.config.distributedVirtualSwitch.uuid
        nicspec.device.backing           = vim.vm.device.VirtualEthernetCard. DistributedVirtualPortBackingInfo()
        nicspec.device.backing.port      = dvs_port_connection

      nicspec.device.connectable                   = vim.vm.device.VirtualDevice.ConnectInfo()
      nicspec.device.connectable.startConnected    = True
      nicspec.device.connectable.allowGuestControl = True
      device_change.append(nicspec)
      break

  config_spec = vim.vm.ConfigSpec(deviceChange=device_change)
  vm.ReconfigVM_Task(config_spec)

  module.exit_json(changed=True)

main()
