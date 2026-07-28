#!/bin/bash
# delete_person.sh — Portal person removal (Terminal portion only)
# Usage: ./delete_person.sh 292792337192
#
# REQUIRES: You must already have deleted the person (and parents) in
# Ancestry tree 210677585, exported it as GEDCOM, and saved it as
# /Users/admin/Desktop/portal/parker.ged BEFORE running this script.

set -e

if [ -z "$1" ]; then
    echo "ERROR: No ID given."
    echo "Usage: ./delete_person.sh 292792337192"
    exit 1
fi

ID="$1"
cd /Users/admin/Desktop/portal || { echo "ERROR: portal folder not found."; exit 1; }

echo "Rebuilding data.js from parker.ged..."
python3 new_build_data_js.py

echo "Removing html/media files for ID $ID..."
rm -f "html/${ID}.html"
rm -f media/${ID}*

echo "Removing $ID from id.csv and IDmediaLinks.csv..."
sed -i '' "/^${ID},/d" id.csv
sed -i '' "/^${ID},/d" IDmediaLinks.csv

echo ""
echo "Verifying removal..."
COUNTS=$(grep -c "$ID" data.js id.csv IDmediaLinks.csv || true)
echo "$COUNTS"
echo ""

if echo "$COUNTS" | grep -qv ":0$"; then
    echo "RESULT: FAIL — one or more files still contain ID $ID."
    echo "Do not assume deletion is complete. Check the counts above."
    exit 1
else
    echo "RESULT: PASS — ID $ID removed from all three files."
fi
