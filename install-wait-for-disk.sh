#!/bin/bash

mkdir -p /opt/c2d
cat > /opt/c2d/wait-for-disk.sh << 'EOF'

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

set -o nounset
set -o errexit

# Required:
readonly DISK_NAME=${1}

# Optional:
readonly MOUNT_DIR=${2:-}

readonly DISK_PATH=/dev/disk/by-id/google-${DISK_NAME}

# Expected (but not required)
# DISK_ATTACH_WAIT_SEC - maximum total seconds to wait
# DISK_WAIT_INTERVAL - sleep interval

readonly WAIT_SEC=${DISK_ATTACH_WAIT_SEC:-300}
readonly INTERVAL_SEC=${DISK_WAIT_INTERVAL:-5}

# Wait for the disk to be created and attached
for ((i = 0; i < ${WAIT_SEC}; i += ${INTERVAL_SEC})); do
  if [[ -e ${DISK_PATH} ]]; then
    break
  fi

  echo "Disk ${DISK_PATH} not found - sleeping ${INTERVAL_SEC} seconds..."
  sleep ${INTERVAL_SEC}
done

if [[ ! -e ${DISK_PATH} ]]; then
  echo "Disk ${DISK_PATH} not found after ${WAIT_SEC} seconds..."
  exit 1
fi

# Mount the dir if requested
if [[ -z ${MOUNT_DIR} ]]; then
  exit 0
fi

mkdir -p ${MOUNT_DIR}
chmod 777 ${MOUNT_DIR}
/usr/share/google/safe_format_and_mount \
  -m "mkfs.ext4 -F" ${DISK_PATH} ${MOUNT_DIR}

# Add an entry to /etc/fstab to mount the disk on restart
echo "${DISK_PATH} ${MOUNT_DIR} ext4 defaults 0 0" >> /etc/fstab

EOF

chmod +x /opt/c2d/wait-for-disk.sh
