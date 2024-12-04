#!/bin/bash

# Parse command line arguments
MERGE=false
PROJECT_NAME_SPECIFIED=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --merge)
            MERGE=true
            shift
            ;;
        --project)
            if [ -n "$2" ]; then
                PROJECT_NAME_SPECIFIED=$2
                shift 2
            else
                echo "Error: --project requires a name argument"
                exit 1
            fi
            ;;
        *)
            shift
            ;;
    esac
done

# This is the path where Isaac Sim is installed which contains the python.sh script
ISAAC_SIM_PATH="/home/shinfang-ovx/.local/share/ov/pkg/isaac-sim-4.2.0"

## Go to location of the SDG script
cd ../kitchenware_sdg
WS_DIR="${PWD}"
SCRIPT_PATH="${PWD}/standalone_kitchenware_sdg.py"

BASE_PROJECT_NAME="kitchenware_data"
if [ -n "$PROJECT_NAME_SPECIFIED" ]; then
    PROJECT_NAME=$PROJECT_NAME_SPECIFIED
    # Check if specified directory exists
    if [[ -d "$PWD/$PROJECT_NAME" ]]; then
        echo -e "\033[33mWarning: Directory '$PROJECT_NAME' already exists. Do you want to continue? [y/N]\033[0m"
        read response
        case $response in
            [yY]) 
                echo "Continuing with existing directory..."
                ;;
            *)
                echo "Aborting. Please choose a different project name."
                exit 1
                ;;
        esac
    fi
else
    # Auto-increment logic for project name
    PROJECT_NAME=$BASE_PROJECT_NAME
    COUNTER=1
    while [[ -d "$PWD/$PROJECT_NAME" ]]; do
        COUNTER=$((COUNTER + 1))
        PROJECT_NAME="${BASE_PROJECT_NAME}$(printf "%02d" $COUNTER)"
    done
fi

echo "Using project name: ${PROJECT_NAME}"

OUTPUT_KITCHEN="${PWD}/${PROJECT_NAME}/distractors_kitchen"
OUTPUT_ADDITIONAL="${PWD}/${PROJECT_NAME}/distractors_additional"
OUTPUT_NO_DISTRACTORS="${PWD}/${PROJECT_NAME}/no_distractors"


## Go to Isaac Sim location for running with ./python.sh
cd $ISAAC_SIM_PATH

echo "Starting Data Generation"  

./python.sh $SCRIPT_PATH --height 1080 --width 1920 --headless True --num_frames 10000 --rt_subframes 30 --distractors warehouse --data_dir $OUTPUT_KITCHEN  --ws_dir $WS_DIR

./python.sh $SCRIPT_PATH --height 1080 --width 1920 --headless True --num_frames 20000 --rt_subframes 30 --distractors additional --data_dir $OUTPUT_ADDITIONAL  --ws_dir $WS_DIR

./python.sh $SCRIPT_PATH --height 1080 --width 1920 --headless True --num_frames 10000 --rt_subframes 30 --distractors None --data_dir $OUTPUT_NO_DISTRACTORS  --ws_dir $WS_DIR

# wait

# move back to the original directory
cd $WS_DIR

echo "Data Generation Complete"


cd ../local
# Run merge script only if --merge flag is provided
if [ "$MERGE" = true ]; then
    echo "Merging datasets..."
    ./merge_sdg.sh ${PROJECT_NAME}
else
    echo "Skipping merge step. Use --merge flag to merge datasets."
fi
