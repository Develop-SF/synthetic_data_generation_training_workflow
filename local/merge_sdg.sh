#!/bin/bash

# Progress bar function
progress_bar() {
    local current=$1
    local total=$2
    local width=50  # Width of the progress bar
    local percentage=$((current * 100 / total))
    local completed=$((width * current / total))
    local remaining=$((width - completed))
    
    printf "\rProgress: ["
    printf "%${completed}s" | tr ' ' '='
    printf "%${remaining}s" | tr ' ' ' '
    printf "] %d%%" $percentage
    
    if [ $current -eq $total ]; then
        printf "\n"
    fi
}

# Check if project name is provided as argument
if [ "$#" -ne 1 ]; then
    echo -e "\033[1mUsage:\033[0m $0 <project_name>"
    echo -e "\033[1mExample:\033[0m"
    echo "  $0 kitchenware_data01"
    echo -e "\n\033[1mDescription:\033[0m"
    echo "  Merges multiple dataset directories (distractors_kitchen, distractors_additional,"
    echo "  and no_distractors) into a single merged directory within the project folder."
    exit 1
fi

PROJECT_NAME=$1
WS_DIR="${PWD}"

# Define source and merged directories
OUTPUT_KITCHEN="${WS_DIR}/${PROJECT_NAME}/distractors_kitchen"
OUTPUT_ADDITIONAL="${WS_DIR}/${PROJECT_NAME}/distractors_additional"
OUTPUT_NO_DISTRACTORS="${WS_DIR}/${PROJECT_NAME}/no_distractors"

# Create merged directory
MERGED_DIR="${WS_DIR}/${PROJECT_NAME}/merged"
mkdir -p "${MERGED_DIR}/Camera"

echo "Merging datasets... ${MERGED_DIR}"

# Define source directories
SOURCES=("${OUTPUT_KITCHEN}" "${OUTPUT_ADDITIONAL}" "${OUTPUT_NO_DISTRACTORS}")

# Get subdirectories from first dataset to know what to merge
CAMERA_SUBDIRS=$(ls "${OUTPUT_KITCHEN}/Camera")

# Merge each source directory
for source_index in "${!SOURCES[@]}"; do
    source="${SOURCES[$source_index]}"
    source_num=$((source_index + 1))
    echo -e "\nMerging from source $source_num: $source"
    
    # Process each subdirectory
    for subdir in $CAMERA_SUBDIRS; do
        # Calculate starting number for this source
        start_number=0
        if [ $source_index -gt 0 ]; then
            for ((i=0; i<source_index; i++)); do
                prev_source="${SOURCES[$i]}"
                prev_files=(${prev_source}/Camera/${subdir}/*)
                start_number=$((start_number + ${#prev_files[@]}))
            done
        fi
        
        # Get list of files in current source directory
        files=(${source}/Camera/${subdir}/*)
        total_files=${#files[@]}
        
        echo -e "\033[36mMerging ${subdir} (${total_files} files) starting from index ${start_number}\033[0m"
        mkdir -p "${MERGED_DIR}/Camera/${subdir}"
        
        # Copy and rename each file
        current_file_number=0
        for file in "${files[@]}"; do
            # Extract file extension
            extension="${file##*.}"
            # Copy with sequential number
            cp "${file}" "${MERGED_DIR}/Camera/${subdir}/$((start_number + current_file_number)).${extension}"
            ((current_file_number++))
            progress_bar $current_file_number $total_files
        done
    done
done

# Merge metadata files
cat "${OUTPUT_KITCHEN}/metadata.txt" "${OUTPUT_ADDITIONAL}/metadata.txt" "${OUTPUT_NO_DISTRACTORS}/metadata.txt" > "${MERGED_DIR}/metadata.txt"

echo "Merge Complete"
