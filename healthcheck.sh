#!/bin/bash
# Simple check to ensure the device is accessible
if [ -c /dev/ttyUSB0 ]; then
    exit 0  # Success
else
    exit 1  # Failure
fi
