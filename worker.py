#!/usr/bin/python

import boto3
import sys
import botocore
import json
import time
import os
from utils import crop, uploadfile, downloadfile, removefile


sqs = boto3.client('sqs', region_name='eu-central-1' )
queue_url = 'https://sqs.eu-central-1.amazonaws.com/129273668251/this-is-my-first-cli-created-queue'
while True:
  response = sqs.receive_message(QueueUrl=queue_url)
  if 'Messages' in response:
    for message in response['Messages']:
      receipt_handle = message['ReceiptHandle']
      data = json.loads(message['Body'])
      bucket_name = data['Bucket_name']
      src_file_path = data['File_Path']
      coordinates = tuple(map(int , tuple(data['Coordinates'].replace(",", "")[1:-1].split())))
      x0, y0, x1, y2 = coordinates
#      print "Download file... "
      src_folder, filename = src_file_path.split('/')
#      print "file will be saved in /tmp"
      dst_folder = 'tmp'
      crp_folder = 'crp'
      if not os.path.exists(crp_folder):
        os.mkdir(crp_folder)
      downloadfile(bucket_name, dst_folder, src_file_path)
      crop("{}/{}".format(dst_folder, filename), coordinates, os.path.join(crp_folder, filename))
#      print " Upload new file"
      uploadfile("{}/{}".format(crp_folder, filename), bucket_name, "CROP")
#      print " Remove downloded file"
      removefile("{}/{}".format(dst_folder, filename)) 
#      print " Remov croped file"
      removefile("{}/{}".format(crp_folder, filename))
#      print " Delete message"
      sqs.delete_message(QueueUrl=queue_url, ReceiptHandle=receipt_handle);
      sleep_time = 1
  else:
    sleep_time = 15
#    print 'Queue is empty...'
#    print 'Waiting 15 seconds...'
  time.sleep(sleep_time)
