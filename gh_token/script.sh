#!/bin/bash

# Check if the required number of arguments are provided
if [ "$#" -ne 3 ]; then
    echo "Usage: source ./gh_token/script.sh <key_file> <arg1> <arg2>"
    return 1
fi

KEY_FILE="$1"
ARG1="$2"
ARG2="$3"

# Call the Python script with the provided arguments and capture the output
TOKEN=$(python ./gh_token/script.py "$KEY_FILE" "$ARG1" "$ARG2")

# Export the GITHUB_TOKEN environment variable
export GITHUB_TOKEN="$TOKEN"
