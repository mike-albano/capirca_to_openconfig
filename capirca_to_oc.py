"""Sample utility for going from Capirca Policy file to OpenConfig ACL.

Some assumptions and hardcoding made just to show an example.
"""
import re
import json
import pyangbind.lib.pybindJSON as pybindJSON
from acl_bindings import openconfig_acl
from pyangbind.lib.serialise import pybindJSONDecoder


CONFIGS = openconfig_acl()

def _get_terms(file):
  """Parse Capirca policy for terms.

  Args:
    file: (list) Capirca language policy file.
  Returns:
    acl_terms: (dict) Policy file terms.
  """
  acl_terms = {}
  term_regex = r'(?:term((?:.*?\r?\n?)*)})+'
  matches = re.findall(term_regex, file, re.MULTILINE)  # Build dict of terms
  for term in matches:
    acl_terms[term.split()[0]] = term.split('\n')[1:]  # Key'd by term-name.

  return acl_terms


def fixup_terms(acl_terms):
  """Fixup Caprica formatted terms to OpenConfig terminology.

  Args:
    acl_terms: (dict) Policy file terms.
  Returns:
    oc_formatted: (dict) OC ACL-friendly formatted terms.
  """
  oc_formatted = {}  # Dict of OC-friendly formatted terminology.
  line_regex = r'(\s+)(.*\b)(::\s)(.*\b)'
  for name, term_list in acl_terms.items():
    for item in term_list:  # Expand the list of term items for each term.
      matches = re.search(line_regex, item, re.IGNORECASE)  # Pull out terms.
      if matches:
        if matches.group(2) == 'comment':  # Pull out comment.
          oc_formatted[name] = {'description': matches.group(4).strip('"')}
        elif matches.group(2) == 'destination-port':  # Pull out dest-port.
          if matches.group(4) == 'DNS':  # Change to oc ip-protocol-type.
            oc_formatted[name].update({'destination-port': 53})
          elif matches.group(4) == 'DHCP':  # Change to oc ip-protocol-type.
            oc_formatted[name].update({'destination-port': 67})
        elif matches.group(2) == 'protocol':  # Pull out protocol.
          if matches.group(4) == 'udp':  # Change to oc ip-protocol-type.
            oc_formatted[name].update({'protocol': 'IP_UDP'})
          elif matches.group(4) == 'tcp':  # Change to oc ip-protocol-type.
            oc_formatted[name].update({'protocol': 'IP_TCP'})
          # TODO: Add more protocols here.
        elif matches.group(2) == 'destination-address':  # Pull out dest-port.
          # TODO: Reference the Capirca def/NETWORK.net file.
          # TEMP workaround to replace nets with addresses.
          if matches.group(4) == 'GOOGLE_DNS':
            oc_formatted[name].update({'destination-address': '8.8.8.8/32'})
          elif matches.group(4) == 'INTERNAL':
            oc_formatted[name].update({'destination-address': '192.168.0.0/24'})
        elif matches.group(2) == 'option':  # Pull out option.
          # TODO: Build mapping from Capirca options to OC identites (TCP_FLAGS)
          if matches.group(4) == 'tcp-established':
            oc_formatted[name].update({'tcp-flags': 'TCP_ACK'})
        elif matches.group(2) == 'action':  # Pull out action.
          if matches.group(4) == 'deny':
            oc_formatted[name].update({'forwarding-action': 'DROP'})
          elif matches.group(4) == 'accept':
            oc_formatted[name].update({'forwarding-action': 'ACCEPT'})

  return oc_formatted


def _create_configs(oc_formatted):
  """Populate Pyangbind objects.

  Args:
    oc_formatted: (dict) OC ACL-friendly formatted terms.
  Returns:
    acl_configs: (class) Populated objects.
  """
  acl_conf = CONFIGS.acl.acl_sets.acl_set.add(name='Capirca Conversion Example',
                                              type='ACL_IPV4')
  acl_conf.config.name = 'Capirca Conversion Example'
  acl_conf.config.type = 'ACL_IPV4'
  acl_conf.config.description = ('Converted from Capirca pol file. TODO: Copy '
                                'Capirca header.')
  seq_number = 0
  for name, rules in oc_formatted.items():
    sequence = acl_conf.acl_entries.acl_entry.add(sequence_id=seq_number)
    sequence.config.sequence_id = seq_number
    seq_number = seq_number + 1
    sequence.config.description = rules['description']
    # TODO: Would need to deal with one seq. per destination-address.
    if 'destination-address' in rules:
      sequence.ipv4.config.destination_address = rules['destination-address']
    if 'protocol' in rules:
      sequence.ipv4.config.protocol = rules['protocol']
    if 'destination-port' in rules:
      sequence.transport.config.destination_port = rules['destination-port']
    if 'tcp-flags' in rules:
      sequence.transport.config.tcp_flags = rules['tcp-flags']
    sequence.actions.config.forwarding_action = rules['forwarding-action']

  print(pybindJSON.dumps(acl_conf, mode='ietf'))  # Print SetRequest() payload.


if __name__ == '__main__':
  pol_file = open('sample_cisco_lab.pol').read()
  acl_terms = _get_terms(pol_file)
  oc_formatted = fixup_terms(acl_terms)
  oc_config = _create_configs(oc_formatted)
