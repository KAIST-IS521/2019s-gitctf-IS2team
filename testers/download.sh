#!/usr/bin/env bash
curl -k https://localhost:8000/auth -d "id=eliz&pw=uNaiph9e" --cookie-jar ./cookie

echo "Download certificate of eliz"
curl -k https://localhost:8000/download -b ./cookie -o elizcert.json

echo "Download certificate of kung with eliz"
curl -k https://localhost:8000/download -b ./cookie -d "targetuid=kung" -o kungcert.json
