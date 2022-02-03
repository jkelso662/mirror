#!/bin/bash
# https://www.howtogeek.com/405468/how-to-perform-a-task-when-a-new-file-is-added-to-a-directory-in-linux/
# https://www.maketecheasier.com/run-bash-commands-background-linux/

TARGET=output/
BUCKET_FOLDER=secondcrawl/

inotifywait -m -e create -e moved_to --format "%f" $TARGET \
        | while read FILENAME
                do
                        echo "Detected $FILENAME, moving to s3 (s3://github-analytics-bucket/$BUCKET_FOLDER$FILENAME)"
                        aws s3 cp $TARGET$FILENAME s3://github-analytics-bucket/$FILENAME
                done