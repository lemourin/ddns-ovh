#!/usr/bin/env python3

import ovh
import os
import json
import requests
import subprocess
import sys


def get_host_ip():
    return subprocess.run(
        ["dig", "+short", "myip.opendns.com", "@resolver1.opendns.com"], check=True, capture_output=True).stdout.decode('utf-8').strip()


def get_domain_ip(domain_name):
    return subprocess.run(["dig", "+short", domain_name, "A"], check=True, capture_output=True).stdout.decode('utf-8').strip()


if len(sys.argv) < 3:
    print(f"Usage: {sys.argv[0]} domain subdomains...")
    exit(1)

DOMAIN = sys.argv[1]
SUB_DOMAINS = sys.argv[2:]
HOST_IP = get_host_ip()

client = ovh.Client(
    endpoint=os.getenv("OVH_ENDPOINT"),
    application_key=os.getenv("OVH_APPLICATION_KEY"),
    application_secret=os.getenv("OVH_APPLICATION_SECRET"),
    consumer_key=os.getenv("OVH_CONSUMER_KEY"),
)

record_updated = False
for sub_domain in SUB_DOMAINS:
    domain_name = DOMAIN if len(sub_domain) == 0 else f"{sub_domain}.{DOMAIN}"
    sub_domain_ip = get_domain_ip(domain_name)

    if HOST_IP == sub_domain_ip:
        continue

    record_params = {
        "fieldType": "A",
        "subDomain": sub_domain,
        "target": HOST_IP
    }
    record_ids = client.get(
        f"/domain/zone/{DOMAIN}/record", fieldType='A', subDomain=sub_domain)
    if len(record_ids) > 0:
        client.put(
            f"/domain/zone/{DOMAIN}/record/{record_ids[0]}", **record_params)
    else:
        client.post(f"/domain/zone/{DOMAIN}/record", **record_params)
    record_updated = True


if record_updated:
    client.post(f"/domain/zone/{DOMAIN}/refresh")
