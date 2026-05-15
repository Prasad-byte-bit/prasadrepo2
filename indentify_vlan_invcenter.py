#!/usr/bin/env python3

# === Imports ===
import ssl
from pyVim.connect import SmartConnect, Disconnect
from pyVmomi import vim
from tabulate import tabulate
import sys
import os

# === CONFIGURATION ===
#VCENTER = 'lvn-zm1w1-vc1.lvn.broadcom.net'
USERNAME = 'BRCMLTD\wasvcuser'
VCENTER = os.getenv("vcenter")
PASSWORD = os.getenv("password")
TARGET_VLAN = os.getenv("TARGET_VLAN")

# === CONNECT TO VCENTER ===
try:
    print(f"\nConnecting to vCenter {VCENTER}...")
    # Ignore SSL certificate validation for self-signed certs
    context = ssl._create_unverified_context()  # <--- critical line
    si = SmartConnect(host=VCENTER, user=USERNAME, pwd=PASSWORD, sslContext=context)
except Exception as e:
    print(f"Failed to connect to vCenter: {e}")
    sys.exit(1)

content = si.RetrieveContent()
results = []

# --- TRAVERSE DATACENTERS, CLUSTERS, HOSTS ---
for datacenter in content.rootFolder.childEntity:
    if not hasattr(datacenter, 'hostFolder'):
        continue
    for cluster in datacenter.hostFolder.childEntity:
        if not hasattr(cluster, 'host'):
            continue
        for host in cluster.host:
            # Standard vSwitch PortGroups
            for pg in host.network:
                if isinstance(pg, vim.Network) and pg.name == TARGET_VLAN:
                    vlan_id = getattr(getattr(pg, 'summary', None), 'vlanId', None)
                    results.append({
                        'vCenter': VCENTER,
                        'Datacenter': datacenter.name,
                        'Cluster': cluster.name,
                        'PortGroup': pg.name,
                        'VLAN_ID': vlan_id,
                        'Switch': 'Standard vSwitch'
                    })

            # Distributed vSwitch PortGroups
            try:
                for dvs_pg in getattr(host.config.network, 'portgroup', []):
                    if dvs_pg.name == TARGET_VLAN:
                        vlan_id = getattr(getattr(dvs_pg, 'spec', None), 'vlanId', None)
                        results.append({
                            'vCenter': VCENTER,
                            'Datacenter': datacenter.name,
                            'Cluster': cluster.name,
                            'PortGroup': dvs_pg.name,
                            'VLAN_ID': vlan_id,
                            'Switch': 'Distributed vSwitch'
                        })
            except AttributeError:
                pass  # Skip if no distributed switch

# --- REMOVE DUPLICATES ---
unique_results = { (r['vCenter'], r['Datacenter'], r['Cluster'], r['PortGroup']): r for r in results }

# --- DISPLAY RESULTS ---
if unique_results:
    print("\nVLAN FOUND:\n")
    table = [v for v in unique_results.values()]
    print(tabulate(table, headers="keys", tablefmt="grid"))
    print(unique_results)
else:
    print(f"\nVLAN '{TARGET_VLAN}' not found in any cluster!")

# --- DISCONNECT VCENTER ---
Disconnect(si)
