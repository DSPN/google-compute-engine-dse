"""Utils that help with components testing."""
import os

from google3.pyglib import flags

FLAGS = flags.FLAGS


def GetCommonDir():
  """Return the path to the common diretory with reusable modules."""
  return os.path.join(flags.FLAGS.test_srcdir, 'google3', 'cloud',
                      'click_to_deploy', 'packages', 'common') + '/'


def GetFileContent(filename, path=None):
  """Reads a file from the common directory."""
  path = path or GetCommonDir()
  return open(path + filename, 'r').read()


def CreateImportsDict(*args):
  """Generic function to be used by several tests that use the expansion lib."""
  imports = {}
  path = GetCommonDir()
  for arg in args:
    imports[arg] = GetFileContent(arg, path)
  return imports


def CreateImportsDictFromYaml(yaml_dict, sol_path=None):
  """Derive the imports from the yaml file itself."""
  if not yaml_dict or 'imports' not in yaml_dict:
    raise ValueError('Yaml config %s is not a dictionary with an '
                     '"imports" key.')
  imports = {}
  if sol_path and sol_path[-1] != '/':
    sol_path += '/'
  for paths in yaml_dict['imports']:
    filename = paths['path']
    name = paths['name'] if 'name' in paths else filename
    imports[name] = GetFileContent(filename, sol_path)
  return imports
