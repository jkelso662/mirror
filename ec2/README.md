# mirror - EC2 tools
To run the crawler for long periodes of time, we have built an EC2 instance that can run the program for as long as needed.
Included in this folder are some tools and scripts that will help.

## setup
this shell script can be used to build the instance during the configuration step in the AWS console, or as reference to the commands that need to be run to set it up.

## s3sync.sh
This script when run will watch the path provided at the top of the script for new files being created by the crawler. It will then proceed to push these files to the s3 bucket provided