#!/usr/bin/env bash
curl -k https://localhost:8000/auth -d "id=eliz&pw=uNaiph9e" --cookie-jar ./cookie

echo "Upload eliz certificate in ascii format"
curl -k https://localhost:8000/upload -b ./cookie -F "signkey=@sangkilc.gpg"

echo "Upload eliz certificate in binary format"
curl -k https://localhost:8000/upload -b ./cookie -F "signkey=@sangkilc.gpg.dearmored"

echo "Upload eliz certificate in bad ascii format, deleting last 3 character"
curl -k https://localhost:8000/upload -b ./cookie -F "signkey=@sangkilc.gpg.bad"

echo "Upload eliz certificate in bad binary format, changing first byte to null"
curl -k https://localhost:8000/upload -b ./cookie -F "signkey=@sangkilc.gpg.dearmored.bad"