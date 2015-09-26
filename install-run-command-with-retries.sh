#!/bin/bash

#
# Script to install run-command-with-retries.sh to the Click to Deploy setup
# directory.
#

mkdir -p /opt/c2d
cat > /opt/c2d/run-command-with-retries.sh << 'EOF'
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
# run-command-with-retries.sh
#
# This script provides functionality for Click to Deploy startup scripts.
#
MAX_RETRY_SEC=${MAX_RETRY_SEC:-120}
SLEEP_SEC=${SLEEP_SEC:-2}

# Expect
# COMMAND
readonly COMMAND=$1

# Exit if no command exists
if [ -z "${COMMAND}" ]; then
  exit 1
fi

echo "Running command: ${COMMAND}"

# Run the command
for ((i = 0; i < ${MAX_RETRY_SEC}; i += ${SLEEP_SEC})); do
  if eval ${COMMAND}; then
    exit 0
  fi

  echo "Command '${COMMAND}' failed -  retry after sleep ${SLEEP_SEC} seconds..."
  sleep ${SLEEP_SEC}
done

exit 1
EOF

chmod +x /opt/c2d/run-command-with-retries.sh
