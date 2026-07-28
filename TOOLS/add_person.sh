#!/bin/bash
# add_person.sh — Portal person creation (Terminal portion only)
# Usage: ./add_person.sh 292810274722 [photo_count]
#
# REQUIRES BEFORE RUNNING:
#   1. Person already linked/added in Ancestry tree 210677585 (parker).
#   2. Fresh GEDCOM exported and saved as
#      /Users/admin/Desktop/portal/parker.ged
#   3. If photos are ready, they are already copied into
#      /Users/admin/Desktop/portal/media/ named ID_1.webp, ID_2.webp, etc.
#      before you run this script with the matching photo_count.
#
# photo_count is optional — defaults to 0 if not given.

set -e

if [ -z "$1" ]; then
    echo "ERROR: No ID given."
    echo "Usage: ./add_person.sh 292810274722 [photo_count]"
    exit 1
fi

ID="$1"
PHOTOS="${2:-0}"

cd /Users/admin/Desktop/portal || { echo "ERROR: portal folder not found."; exit 1; }

echo "Backing up data.js..."
cp data.js data.js.bak

echo "Rebuilding data.js from parker.ged..."
python3 new_build_data_js.py

echo ""
echo "Checking that ID $ID is present in data.js..."
COUNT=$(grep -c "$ID" data.js || true)
if [ "$COUNT" -eq 0 ]; then
    echo "RESULT: FAIL — ID $ID not found in data.js."
    echo "The person did not make it into parker.ged. Check Step 1/2"
    echo "(Ancestry linking and export) before running this script again."
    exit 1
fi
echo "Found ID $ID in data.js ($COUNT occurrence(s))."

echo ""
if [ -f "html/${ID}.html" ]; then
    echo "Existing page found for $ID — removing so it can be regenerated..."
    rm -f "html/${ID}.html"
fi

echo "Creating page for $ID with $PHOTOS photo(s)..."
python3 build_new_html.py "$ID" --photos "$PHOTOS"

echo ""
if [ -f "html/${ID}.html" ]; then
    echo "RESULT: PASS — page created for ID $ID (html/${ID}.html), $PHOTOS photo(s) referenced."
else
    echo "RESULT: FAIL — build_new_html.py did not produce html/${ID}.html."
    echo "Check the output above for an error message from the script."
    exit 1
fi
