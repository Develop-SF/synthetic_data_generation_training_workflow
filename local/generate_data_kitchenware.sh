#!/bin/bash

# This is the path where Isaac Sim is installed which contains the python.sh script
ISAAC_SIM_PATH="/home/wychien/.local/share/ov/pkg/isaac-sim-4.2.0"

## Go to location of the SDG script
cd ../kitchenware_sdg
WS_DIR="${PWD}"
SCRIPT_PATH="${PWD}/standalone_kitchenware_sdg.py"

BASE_PROJECT_NAME="kitchenware_data"
PROJECT_NAME=$BASE_PROJECT_NAME
COUNTER=1

while [[ -d "$PWD/$PROJECT_NAME" ]]; do
    COUNTER=$((COUNTER + 1))
    PROJECT_NAME="${BASE_PROJECT_NAME}$(printf "%02d" $COUNTER)"
done

echo "Using project name: ${PROJECT_NAME}"

OUTPUT_KITCHEN="${PWD}/${PROJECT_NAME}/distractors_kitchen"
OUTPUT_ADDITIONAL="${PWD}/${PROJECT_NAME}/distractors_additional"
OUTPUT_NO_DISTRACTORS="${PWD}/${PROJECT_NAME}/no_distractors"


## Go to Isaac Sim location for running with ./python.sh
cd $ISAAC_SIM_PATH

echo "Starting Data Generation"  

./python.sh $SCRIPT_PATH --height 1080 --width 1920 --headless True --num_frames 400 --rt_subframes 30 --distractors warehouse --data_dir $OUTPUT_KITCHEN  --ws_dir $WS_DIR

./python.sh $SCRIPT_PATH --height 1080 --width 1920 --headless True --num_frames 800 --rt_subframes 30 --distractors additional --data_dir $OUTPUT_ADDITIONAL  --ws_dir $WS_DIR

./python.sh $SCRIPT_PATH --height 1080 --width 1920 --headless True --num_frames 400 --rt_subframes 30 --distractors None --data_dir $OUTPUT_NO_DISTRACTORS  --ws_dir $WS_DIR



