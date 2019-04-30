#!/usr/bin/env bash
curl -k https://localhost:8000/auth -d "id=test&pw=test" --cookie-jar ./cookie
curl -k https://localhost:8000/ -b ./cookie
echo "[*] Changing test uid information to [last, first, admin@test.com, 1234]"

curl -k https://localhost:8000/change -d "lastname=last&firstname=first&email=admin@test.com&passwd=1234" -b ./cookie

echo "[*] Auth with test/1234"
curl -k https://localhost:8000/auth -d "id=test&pw=1234" --cookie-jar ./cookie2
curl -k https://localhost:8000/ -b ./cookie2
