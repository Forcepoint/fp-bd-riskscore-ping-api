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

Create the SSL certificate, **Note** the command below is not provided for production as it's your own responsibility to provide and manage the SSL certificate, the command below is only made available for a quick temporary demo, the command below will create the public certificate and it's private key for the API in the ./certs directory, replacing: **SUBJECT** value.

```bash
HOSTNAME=$(hostname); \
SUBJECT="/C=IE/ST=Cork/L=Cork/O=Forcepoint/CN=$HOSTNAME"; \
LOCAL_DIR="./certs"; \
mkdir -p ${LOCAL_DIR}; \
docker run --rm --entrypoint /bin/ash frapsoft/openssl \
-c "openssl req \
  -newkey rsa:4096 \
  -days 3650 \
  -nodes \
  -x509 \
  -subj $SUBJECT \
  -keyout server.key \
  -out server.crt; \
  cat server.crt server.key" > ${LOCAL_DIR}/certs; \
cat ${LOCAL_DIR}/certs | sed '/END CERTIFICATE/q' > ${LOCAL_DIR}/${HOSTNAME}.crt; \
cat ${LOCAL_DIR}/certs | sed -n '/BEGIN PRIVATE KEY/, /END PRIVATE KEY/p' > ${LOCAL_DIR}/${HOSTNAME}.key; \
rm -rf ${LOCAL_DIR}/certs; \
openssl x509 -noout -certopt no_sigdump,no_pubkey -text -in ${LOCAL_DIR}/${HOSTNAME}.crt; \
unset HOSTNAME SUBJECT LOCAL_DIR;
```

or run the below with SUBJECTALT:

```bash
HOSTNAME=$(hostname); \
IPADDRESS=""; \
SUBJECT="/C=IE/ST=Cork/L=Cork/O=Forcepoint/CN=$HOSTNAME"; \
SUBJECTALT="DNS:$HOSTNAME, DNS:localhost, IP:$IPADDRESS, IP:127.0.0.1"; \
LOCAL_DIR="./certs"; \
mkdir -p ${LOCAL_DIR}; \
docker run --rm --entrypoint /bin/ash frapsoft/openssl \
-c "cat /etc/ssl/openssl.cnf > temp.conf && \
printf \"[SAN]\nsubjectAltName='$SUBJECTALT'\" >> temp.conf && \ 
openssl req \
  -newkey rsa:4096 \
  -days 3650 \
  -nodes \
  -x509 \
  -subj $SUBJECT \
  -extensions SAN \
  -keyout server.key \
  -out server.crt \
  -config temp.conf; \
  cat server.crt server.key" > ${LOCAL_DIR}/certs; \
cat ${LOCAL_DIR}/certs | sed '/END CERTIFICATE/q' > ${LOCAL_DIR}/${HOSTNAME}.crt; \
cat ${LOCAL_DIR}/certs | sed -n '/BEGIN PRIVATE KEY/, /END PRIVATE KEY/p' > ${LOCAL_DIR}/${HOSTNAME}.key; \
rm -rf certs; \
rm -rf ${LOCAL_DIR}/certs; \
openssl x509 -noout -certopt no_sigdump,no_pubkey -text -in ${LOCAL_DIR}/${HOSTNAME}.crt; \
unset HOSTNAME IPADDRESS SUBJECT SUBJECTALT LOCAL_DIR;
```

Get Kafka CA cert for FBA:

```bash
#!/usr/bin/env bash

HOSTNAME=$(hostname)
KAFKA_USER=""
KAFKA_SERVER=""
TRUSTSTORE_DIR="/etc/kafka/conf"
TRUSTSTORE_NAME="kafka-lab-truststore.p12"
TRUSTSTORE_PASS="changeme"
CA_FILE="kafka-ca.crt"
LOCAL_DIR="./certs"

# Download Kafka truststore for exporting CA chain
echo "Downloading Kafka truststore..."
scp ${KAFKA_USER}@${KAFKA_SERVER}:${TRUSTSTORE_DIR}/${TRUSTSTORE_NAME} ${TRUSTSTORE_NAME}

# Upload self-signed certificate
scp ${LOCAL_DIR}/${HOSTNAME}.crt ${KAFKA_USER}@${KAFKA_SERVER}:~/.

# Delete any existing certificates with local hostname alias and import to truststore
echo "Importing self-signed certificate to Kafka truststore and restarting Kafka..."
ssh -t ${KAFKA_USER}@${KAFKA_SERVER} "sudo keytool -keystore ${TRUSTSTORE_DIR}/${TRUSTSTORE_NAME} -alias ${HOSTNAME} -storepass ${TRUSTSTORE_PASS} -delete &>/dev/null; sudo keytool -keystore ${TRUSTSTORE_DIR}/${TRUSTSTORE_NAME} -alias ${HOSTNAME} -import -file ${HOSTNAME}.crt -storepass ${TRUSTSTORE_PASS} -noprompt ; rm -f ${HOSTNAME}.crt ; sudo service kafka restart"

# it can be found in ...
# Parse through truststore and get alias list for CA chain
IFS=$'\n'
arr=($(keytool -list -keystore ${TRUSTSTORE_NAME} -storepass ${TRUSTSTORE_PASS} | grep "ueba" | cut -d ',' -f1))
unset IFS

# Export CA certs
echo "Exporting Kafka CA certificates..."
for (( i=0; i<${#arr[@]}; i++ ))
do
	keytool -exportcert -keystore ${TRUSTSTORE_NAME} -storetype PKCS12 -alias "${arr[$i]}" -storepass ${TRUSTSTORE_PASS} -rfc >> ca.crt
done

# Workaround for Keytool CRLF bug
sed -e "s/\r//g" ca.crt > ${LOCAL_DIR}/${CA_FILE}

# Cleanup
rm -f ca.crt ${TRUSTSTORE_NAME}

# Docuble check cert exists
ssh -t ${KAFKA_USER}@${KAFKA_SERVER} "openssl pkcs12 -nokeys -info -in ${TRUSTSTORE_DIR}/${TRUSTSTORE_NAME} -passin pass:${TRUSTSTORE_PASS}"

echo "Done."
```


Edit cfg.env file first and then create container, you also need to map the certs.


```bash
docker run --interactive --tty --detach \
   --env-file $PWD/cfg.env \
   --name fp-riskexporter-api \
   --publish 5000:5000 \
   --restart unless-stopped \
   --volume $PWD/certs/server.crt:/app/fp-riskexporter-api/certs/server.crt \
   --volume $PWD/certs/server.key:/app/fp-riskexporter-api/certs/server.key \
   --volume $PWD/certs/kafka-ca.crt:/app/fp-riskexporter-api/certs/kafka-ca.crt \
   --volume RiskScoreDBVolume:/app/fp-riskexporter-api/db \
   --volume RiskScoreApiLogs:/app/fp-riskexporter-api/logs \
   docker.frcpnt.com/fp-riskexporter-api
```

Another way to run a container without cfg.env, create cfg.yml and run below:

```bash
docker run --interactive --tty --detach \
   --name fp-riskexporter-api \
   --publish 5000:5000 \
   --restart unless-stopped \
   --volume $PWD/cfg.yml:/app/fp-riskexporter-api/cfg.yml \
   --volume $PWD/certs/server.crt:/app/fp-riskexporter-api/certs/server.crt \
   --volume $PWD/certs/server.key:/app/fp-riskexporter-api/certs/server.key \
   --volume $PWD/certs/kafka-ca.crt:/app/fp-riskexporter-api/certs/kafka-ca.crt \
   --volume RiskScoreDBVolume:/app/fp-riskexporter-api/db \
   --volume RiskScoreApiLogs:/app/fp-riskexporter-api/logs \
   docker.frcpnt.com/fp-riskexporter-api
```
