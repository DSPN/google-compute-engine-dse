"""Wrapper for datastax."""
import re


def NameConvert(value):
  """Converts zone name key into a zone value."""
  parts = re.findall(r'([A-Z]{1}[a-z]+)([A-Z]{1}[a-z]+)(\d)(\w)', value)
  return '%s-%s%s-%s' % (parts[0][0].lower(), parts[0][1].lower(),
                         parts[0][2].lower(), parts[0][3].lower())


def ConvertZoneBooleansToList(prop_dict):
  """Gets all properties that beging with zone and add them to list if true."""
  prop_keys = prop_dict.keys()
  return [NameConvert(k)
          for k in prop_keys if k.startswith('zone') and prop_dict[k]]


def GenerateConfig(context):
  """Generates YAML resource configuration."""
  res = []
  prop = context.properties
  zones = ConvertZoneBooleansToList(prop)
  datastax_instance_props = {
      'zones': zones,
      'machineType': prop['machineType'],
      'nodesPerZone': prop['nodesPerZone'],
      'nodeType': prop['nodeType'],
      'diskSize': prop['diskSize'],
      'opsCenterZone': prop['opsCenterZone'],
      'instanceBaseName': prop['instanceBaseName']
  }

  res.append({
      'name': 'datastax',
      'type': 'datastax.py',
      'properties': datastax_instance_props
  })

  resources = {'resources': res}

  return resources
