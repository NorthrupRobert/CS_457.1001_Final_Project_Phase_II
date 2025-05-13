#!/bin/bash

EXCEL_FILE="sample ClassSched-CS-S25.xlsx"
ETL_SCRIPT="ETL.py"

echo "Watching $EXCEL_FILE for changes..."

inotifywait -m -e close_write --format '%w%f' "$EXCEL_FILE" | while read FILE
do
    echo "Detected update to $FILE. Running ETL..."
    python3 "$ETL_SCRIPT"
done
