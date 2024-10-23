#!/bin/bash

# This is the path where Isaac Sim is installed which contains the python.sh script
ISAAC_SIM_PATH="/home/wychien/.local/share/ov/pkg/isaac-sim-4.2.0"

## Go to location of the SDG script
cd ../palletjack_sdg
SCRIPT_PATH="${PWD}/standalone_palletjack_sdg.py"
OUTPUT_WAREHOUSE="${PWD}/palletjack_data02/distractors_warehouse"
OUTPUT_ADDITIONAL="${PWD}/palletjack_data02/distractors_additional"
OUTPUT_NO_DISTRACTORS="${PWD}/palletjack_data02/no_distractors"


## Go to Isaac Sim location for running with ./python.sh
cd $ISAAC_SIM_PATH

echo "Starting Data Generation"  

./python.sh $SCRIPT_PATH --height 1080 --width 1920 --headless True --num_frames 200 --distractors warehouse --data_dir $OUTPUT_WAREHOUSE

# ./python.sh $SCRIPT_PATH --height 544 --width 960 --num_frames 2000 --distractors additional --data_dir $OUTPUT_ADDITIONAL

# ./python.sh $SCRIPT_PATH --height 544 --width 960 --num_frames 1000 --distractors None --data_dir $OUTPUT_NO_DISTRACTORS


