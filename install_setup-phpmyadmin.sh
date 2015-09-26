#!/bin/bash

mkdir -p /opt/c2d
cat > /opt/c2d/setup-phpmyadmin.sh << 'EOF'

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
# install-phpmyadmin.sh
#
# This script installs and configures phpmyadmin
#

set -o nounset
set -o errexit

readonly INSTALL_PHPMYADMIN="$(/usr/share/google/get_metadata_value attributes/INSTALL_PHPMYADMIN | awk -F':' '{print $2}' | tr '[:upper:]' '[:lower:]')"
readonly MYSQL_ROOT_PASSWORD="$(/usr/share/google/get_metadata_value attributes/MYSQL_ROOT_PASSWORD)"

if [[ "${INSTALL_PHPMYADMIN:-}" == "true" ]]; then

  # Install phpmyadmin Note: on Debian, the config files are placed in /etc/phpmyadmin
  echo phpmyadmin phpmyadmin/dbconfig-install boolean true | debconf-set-selections
  echo phpmyadmin phpmyadmin/mysql/admin-pass password ${MYSQL_ROOT_PASSWORD} | debconf-set-selections
  echo phpmyadmin phpmyadmin/reconfigure-webserver multiselect apache2 | debconf-set-selections
  export DEBIAN_FRONTEND='noninteractive'
  apt-get install phpmyadmin -yqq

  if [[ -d "/usr/share/nginx" ]]; then
    ln -s /usr/share/phpmyadmin /usr/share/nginx/html
    service nginx restart
  fi
else
  echo "phpMyAdmin install not requested... skipping."
fi
EOF
chmod +x /opt/c2d/setup-phpmyadmin.sh
echo "setup-phpmyadmin.sh" >> /opt/c2d/manifest
