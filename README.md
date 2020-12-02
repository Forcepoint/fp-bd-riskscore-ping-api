# Technical Overview

This service exposes an API to retrieve User Risk level from CASB risk score and FBA risk level.

Note this was build to mimic an existing FBA risk level API (https://github.cicd.cloud.fpdev.io/UEBA/ueba-risk-exporter)

- https://127.0.0.1:5000/riskexporter
- https://127.0.0.1:5000/riskexporter/dummy/event
- https://127.0.0.1:5000/casb/healthcheck
- https://127.0.0.1:5000/casb/risk/level/(entity)
- https://127.0.0.1:5000/fba/healthcheck
- https://127.0.0.1:5000/fba/risk/level/(entity)


## Implementation

In this process logs are configured to rotated by size of 10mb into max of 2 rotated files.

Prerequisites are: python3.6

```bash
python3 -m pip install pipx
python3 -m pipx ensurepath
pipx install pipenv
```

To build run:

```bash
pipenv install
```

Make sure shell scripts are executable.

Configure cfg.yml file

Deploy systemd scripts located in deploy folder.

Code tests can be run by

```bash
pipenv run pytest
```

## User Configurations cfg.yml

```yml
api_port: 5000
ssl_certfile: 
ssl_keyfile: 
ssl_password:

# CASB Risk Score Configurations:
casb_risk_score_fetch_enable: True
casb_fetch_data_period_in_min: 10 minutes
casb_saas_url: 
casb_login_name: 
casb_login_password: 
risk_level_1: 0-10
risk_level_2: 20-49
risk_level_3: 50-79
risk_level_4: 80-99
risk_level_5: 100+

# FBA Risk Score Configurations:
fba_risk_score_fetch_enable: False
kafka_server_name: 
kafka_server_ip: 
ssl_cafile:  
```

## Docker

Package deployment first, then run image build.

```bash
./build/create-deployment.sh && \
docker build -t fp-riskexporter-api .
```

Edit cfg.env file first and then create container, you also need to map the certs.


```bash
docker run -itd \
   --name fp-riskexporter-api \
   -p 5000:5000 \
   --env-file $PWD/cfg.env \
   -v $PWD/certs:/app/fp-riskexporter-api/certs \
   -v RiskScoreDBVolume:/app/fp-riskexporter-api/db \
   fp-riskexporter-api
```

Another way to run a container without cfg.env, create cfg.yml and run below:

```bash
docker run -itd \
   --name fp-riskexporter-api \
   -p 5000:5000 \
   -v $PWD/cfg.yml:/app/fp-riskexporter-api/cfg.yml \
   -v $PWD/certs:/app/fp-riskexporter-api/certs \
   -v RiskScoreDBVolume:/app/fp-riskexporter-api/db \
   fp-riskexporter-api
```
