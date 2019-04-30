#!/usr/bin/env bash

echo "verify eliz certificate"
curl -k https://localhost:8000/verify -F "verifykey=@elizcert.json"

echo "verify kung certificate"
curl -k https://localhost:8000/verify -F "verifykey=@kungcert.json"
