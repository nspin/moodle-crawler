#!/bin/sh

# ensure that blobs are actually content-addressed

blob_dir=blobs

for blob in $(ls "$blob_dir"); do
    if [ "$blob" != "$(sha256sum "$blob_dir/$blob" | cut -d ' ' -f 1)" ]; then
        echo BAD "$blob"
    fi
done
