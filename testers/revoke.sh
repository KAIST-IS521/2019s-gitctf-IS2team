@ECHO OFF
#!/usr/bin/env bash

echo "Initial revoke-list"
curl -k https://localhost:8000/revoke-list

curl -k https://localhost:8000/revoke
echo "After revoke without authentication"
curl -k https://localhost:8000/revoke-list

echo "Authenticate as kung"
curl -k https://localhost:8000/auth -d "id=kung&pw=Shoo8pie" --cookie-jar ./cookie_revoke
curl -k https://localhost:8000/revoke -b ./cookie_revoke

echo "New revoke record for kung"
curl -k https://localhost:8000/revoke-list
