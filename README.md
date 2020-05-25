# capirca_to_openconfig
 Simple Example to show from Capirca pol file to an OpenConfig formattet ACL.

 If you'd prefer to just look at the files, they are included here:
* oc_formatted_acl.json -- JSON IETF output from this script.
* sample_cisco_lab.pol -- Capirca policy file
* sample_cisco_lab.acl -- Native Capirca output file

# Quickstart
1. pip3 install pyangbind
2. python3 capirca_to_oc.py

Relies on hardcoded files and assumptions.

## Caprica output
To get the Capirca output of the policy used in this example, run the following
Capirca command:
```
python3 capirca/aclgen.py --policy_file sample_cisco_lab.pol --output_directory ./
```
