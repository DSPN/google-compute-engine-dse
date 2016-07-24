# Copyright 2015 Google Inc. All rights reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# usage: on a linux bash terminal (with gcloud sdk installed)
# $ python license_image.py --disk <disk_name> --bucket <destination_buket> \
#   --licenses <license_ids>
#
# example:
# $ python license_image.py --disk disk.raw --bucket gs://dest_bucket \
#   --licenses 11000023 1100034
#
"""Script to License a base os image for partner solution."""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile


def SubprocessCall(args, env=None):
  """Method to call subprocess for running linux bash commands."""
  process = subprocess.Popen(args,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE,
                             env=env)
  output, error = process.communicate()
  if process.returncode:
    print '\n Error executing ' + ' '.join(args)
    print '\n'
    sys.exit(0)


def main(disk_raw, dest_bucket, license_ids):
  """Main execution block."""
  ## create a work dir and  a tmp dir
  work_dir = tempfile.mkdtemp()
  print '\n work dir: ' + work_dir
  temp_dir = tempfile.mkdtemp()
  print '\n temp dir: ' + temp_dir
  tar_path = temp_dir + '/root.tar.gz'

  ## copy the disk.raw to the new dir
  shutil.copyfile(disk_raw, work_dir + '/disk.raw')
  print '\n Successfully copied raw disk file to work dir.'

  ## Create the Manifest file inside work_dir
  manifest_text = json.dumps({'licenses': license_ids})

  with open(os.path.join(work_dir, 'manifest.json'), 'w') as f:
    f.write(manifest_text)

  print '\n Successfully written manifest.json file to work dir.'

  ## Packaging the new tar file (image + manifest)
  image_file_set = ['manifest.json', 'disk.raw']

  tar_command = ['tar', '--format=gnu', '-C', work_dir, '-Szcf', tar_path]
  for item in image_file_set:
    tar_command.append(os.path.basename(item))

  SubprocessCall(tar_command)
  print '\n Successfully created tar archive of work dir at temp dir.'

  ## Copying the new tar file to the desticantion bucket
  destination_path = dest_bucket + '/licensed-base-os-raw.tar.gz'

  SubprocessCall(['gsutil', 'cp', tar_path, destination_path])
  print '\n Successfully copied tar file to bucket ' + destination_path

  ## Cleanup
  shutil.rmtree(temp_dir)
  shutil.rmtree(work_dir)
  print '\n Successfully cleaned up temp and work dirs.'
  print '\n'


if __name__ == '__main__':

  parser = argparse.ArgumentParser()
  parser.add_argument('-d',
                      '--disk',
                      dest='disk',
                      help='path to the raw disk image',
                      required=True)
  parser.add_argument('-b',
                      '--bucket',
                      dest='bucket',
                      help='destination Google Cloud Service bucket.',
                      required=True)
  parser.add_argument('-l',
                      '--licenses',
                      dest='licenses',
                      nargs='+',
                      help='license id(s) for the solution.',
                      required=True)

  params = parser.parse_args()

  disk = params.disk
  bucket = params.bucket
  licenses = params.licenses

  main(disk, bucket, licenses)