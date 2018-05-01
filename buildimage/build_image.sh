#/bin/bash

python image_creator.py \
--project datastax-public \
--disk instance-ubuntu-1604-xenial-v20180424 \
--name datastax-enterprise-ubuntu-1604-xenial-v20180424 \
--description 'DataStax Enterprise Ubuntu 16.04 (2018/04/24) Image' \
--destination-project datastax-public \
--license datastax-public/datastax-enterprise
