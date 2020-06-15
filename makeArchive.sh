#!/bin/sh

function makeArchive()
{
  solution=$1
  rm archive-${solution}.zip
  mkdir tmp

  cp ${solution}/cassandra.py tmp
  cp ${solution}/cassandra.py.display tmp
  cp ${solution}/cassandra.py.schema tmp
  cp ${solution}/c2d_deployment_configuration.json tmp
  cp ${solution}/test_config.yaml tmp

  cp ${solution}/common/common.py tmp
  cp ${solution}/common/default.py tmp
  cp ${solution}/common/software_status.py tmp
  cp ${solution}/common/software_status.py.schema tmp
  cp ${solution}/common/software_status.sh.tmpl tmp
  cp ${solution}/common/software_status_script.py tmp
  cp ${solution}/common/software_status_script.py.schema tmp

  cp -r ${solution}/resources tmp

  zip -r -X archive-${solution}.zip tmp -x "*.DS_Store"
  rm -rf tmp
}

makeArchive cassandra-gcp-mp
