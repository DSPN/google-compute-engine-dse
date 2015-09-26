#!/bin/bash

#
# Script to install startup-script.sh to the Click to Deploy setup
# directory.
#

mkdir -p /opt/c2d
cat > /opt/c2d/startup-script.sh << 'EOF'
#!/bin/bash
# Copyright 2014 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS-IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# startup-script.sh
#
# Provides the boot-strapping and orchestrating startup-script for
# Click to Deploy software setup.
#
# This startup script:
#
# Sets up environment variables by:
#   Listing all instance metadata that starts with "ENV_"
#   Exporting VAR=VAL for each (stripping "ENV_" from each)
# For example, a metadata key of ENV_FOO with a value of BAR
# would become "export FOO=BAR"
#
# The package directory /opt/c2d must contain a file called /manifest.
# The contents of the /manifest are executed one line at a time.
#
# All output is recorded to /tmp/startup-script.out
# Deployment status is reported to the serial port (/dev/console)
#

set -o errexit
set -o nounset

readonly INSTALL_TEMP=/tmp
readonly PACKAGE_DIR=/opt/c2d
readonly PACKAGE_LOG=${PACKAGE_DIR}/setup.log
readonly COMPLETION_FILE=${PACKAGE_DIR}/setup.complete

readonly MSGTAG_STATUS_UPDATE="c2d-StatusUpdate"
readonly MSGTAG_STATUS_DETAIL="c2d-StatusDetail"

# Turn on bash xtrace and redirect all stderr and stdout to a log file
set -x
exec 1> ${INSTALL_TEMP}/startup-script.out 2>&1

# writeToSerialPort
#
# Utility routine to write a tagged and timestamped message to the serial port
function writeToSerialPort() {
  local tag=$1
  local timestamp=$2
  local message=$3

  echo "${tag}:TIME=${timestamp};${message}" > /dev/console
}
readonly -f writeToSerialPort

# report
#
# Reports a status of execution message to the log file and serial port
function report() {
  local tag="${1}"
  local message="${2}"
  local timestamp="$(date +%s)000"

  echo "${timestamp} - ${message}"

  writeToSerialPort "${tag}" "${timestamp}" "${message}"
}
readonly -f report

# report_status_update
#
# Reports a status of execution message to the log file and serial port
function report_status_update() {
  report "${MSGTAG_STATUS_UPDATE}" "STATUS=${1}"
}
readonly -f report_status_update

# report_detail
#
# Reports a detail message to the log file and serial port
function report_detail() {
  report "${MSGTAG_STATUS_DETAIL}" "DETAIL=${1}"
}
readonly -f report_detail

# set_script_environment
#
# Read all instance metadata values that start with "ENV_", get their values,
# and set them in the environment
function set_script_environment() {
  local vars=$(/usr/share/google/get_metadata_value attributes/ | grep ^ENV_)
  for var in ${vars}; do
    local val=$(/usr/share/google/get_metadata_value attributes/${var})

    # Trim the "ENV_" portion
    var=${var:4}
    eval export ${var}=\"${val}\"
  done
}
readonly -f set_script_environment

# execute_command
#
# Executes the specified command and turns on xtrace so that we capture
# everything to the log file.
function execute_command() {
  local line=${1}

  bash -x ${line} < /dev/null
}
readonly -f execute_command

#
# Main
#

set_script_environment

report_status_update "STARTUP_SCRIPT_STARTED"

if [ -f ${COMPLETION_FILE} ]; then
  report_status_update "SUCCESS: Setup already completed"
  exit 0
fi

# The package directory is expected to have a manifest, which is a simple list
# of commands to execute

cd ${PACKAGE_DIR}
export PATH=.:${PATH}

# Read line by line from the file and execute
declare FINISHED_STATUS="DEPLOYED"

if [ -f manifest ]; then
  while read line || [[ -n "${line}" ]]; do
    # Skip blank lines
    if [[ -z  ${line} ]]; then
      continue
    fi

    # Make the file executable
    report_status_update "EXECUTING: ${line}"
    chmod 700 ${line}

    # Run it
    if execute_command ${line} &>> ${PACKAGE_LOG}; then
      report_status_update "SUCCESS: ${line}"
    else
      report_status_update "FAILED: ${line}"

      while read logline; do
        report_detail "${logline}"
      done < <(cat ${PACKAGE_LOG})

      FINISHED_STATUS="DEPLOYMENT_FAILED"
      break
    fi
  done < ${PACKAGE_DIR}/manifest

else
  report_status_update "SUCCESS: No manifest for setup found"
fi

# Until the finished status is set correctly into metadata, keep emitting
# to the serial port
declare STORED_STATUS=
while [[ ${STORED_STATUS} != ${FINISHED_STATUS} ]]; do
  report_status_update ${FINISHED_STATUS}
  sleep 2m
  if STORED_STATUS=$(/usr/share/google/get_metadata_value attributes/C2D_STATUS); then
    echo "C2D_STATUS: ${STORED_STATUS}"
  else
    echo "C2D_STATUS not set.  Sleep 1m"
  fi
done

touch ${COMPLETION_FILE}

echo "Startup script complete"

EOF
chmod +x /opt/c2d/startup-script.sh
