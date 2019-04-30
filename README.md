# CA Development - IS2TEAM

We developed CA with python3 and django.  
We tested it on ubuntu 16.04.  
you can access server at https://127.0.0.1/  

## Install
```
git clone.
cd 2019s-is2team
docker build -t ca_server:1 .
docker run -d -p 443:8000 ca_server:1
```

## Test

For usage, we provides test scripts under the tester directory.

