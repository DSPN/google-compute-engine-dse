#/bin/bash

python image_creator.py \
--project datastax-public \
--disk instance-ubuntu-1604-xenial-v20180506 \
--name datastax-enterprise-ubuntu-1604-xenial-v20180506 \
--description 'DataStax Enterprise Ubuntu 16.04 (2018/05/06) Image' \
--destination-project datastax-public \
--license datastax-public/datastax-enterprise
