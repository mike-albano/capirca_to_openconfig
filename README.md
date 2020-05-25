# capirca_openconfig
 Example to show from Capirca pol file to an OpenConfig formattet ACL.

* JSON IETF output from this script: oc_formatted_acl.json
* Capirca policy file: sample_cisco_lab.pol
* Native Capirca output file: sample_cisco_lab.acl

# Quickstart
1. pip3 install pyangbind
2. python3 capirca_to_oc.py

Relies on hardcoded files and assumptions.

## Caprica output
To get the Capirca output of the policy used int his example, run the following
Capirca command:
```
python3 capirca/aclgen.py --policy_file sample_cisco_lab.pol --output_directory ./
```
