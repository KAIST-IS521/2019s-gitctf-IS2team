#!/usr/bin/env bash
curl -k https://localhost:8000/auth -d "id=eliz&pw=uNaiph9e" --cookie-jar ./cookie
curl -k https://localhost:8000/ -b ./cookie
