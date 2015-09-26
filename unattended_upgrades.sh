#!/bin/bash
#
# 1. Update a server to the latest software
# 2. Install and configure unattended upgrades.
#
# Operating system supported by this script:
#   Debian 7+
#   Ubuntu 14.04+
#
# For Debian, we'll configure defaults from:
#   https://wiki.debian.org/UnattendedUpgrades
#
# For Ubuntu, we'll use the distro defaults, as the package comes pre-installed
#
# TODO (cpomeroy) add support for CentOS6/7 (b/22925597)
#

set -o errexit
set -o nounset

function install-for-ubuntu() {
  apt-get update -qq
  apt-get dist-upgrade -yqq
}

function install-for-debian() {
  apt-get update -qq
  apt-get dist-upgrade -yqq
  apt-get install unattended-upgrades -yqq

  cat > /etc/apt/apt.conf.d/02periodic << 'EOF'
  // Added by Google
  // Configure unattended-upgrades package to check for and install security
  // upgrades daily.

  // Control parameters for cron jobs by /etc/cron.daily/apt //

  // Do "apt-get update" automatically every n-days (0=disable)
  APT::Periodic::Update-Package-Lists "1";

  // Do "apt-get upgrade --download-only" every n-days (0=disable)
  APT::Periodic::Download-Upgradeable-Packages "1";

  // Run the "unattended-upgrade" security upgrade script
  // every n-days (0=disabled)
  // Requires the package "unattended-upgrades" and will write
  // a log in /var/log/unattended-upgrades
  APT::Periodic::Unattended-Upgrade "1";

  // Do "apt-get autoclean" every n-days (0=disable)
  APT::Periodic::AutocleanInterval "21";
EOF
}

function install-for-centos6() {
  echo "CentOS 6 Not supported. Exiting..."
  exit 1
}

function install-for-centos7() {
  echo "CentOS 7 Not supported. Exiting..."
  exit 1
}

#
# Main
#

# Ubuntu, Debian, and CentOS 7 use /etc/os-release, CentOS 6 uses /etc/redhat-release
if [[ -f /etc/os-release ]]; then
  # Assign the distribution name to $ID
  source /etc/os-release
elif [[ -f /etc/redhat-release ]]; then
  readonly ID=$(cat /etc/redhat-release)
else
  echo "OS distribution not supported, exiting."
  exit 1
fi

ID=$(echo ${ID} | tr '[:upper:]' '[:lower:]')
case "${ID}" in
  "ubuntu")
    install-for-ubuntu
    ;;
  "debian")
    install-for-debian
    ;;
  "centos" | "centos"*)
    if [[ ${VERSION_ID:-} == "7" ]]; then
      install-for-centos7
    else
      install-for-centos6
    fi
    ;;
  *)
    echo 'Match not found for the value of $ID: ' ${ID}
    exit 1
    ;;
esac
