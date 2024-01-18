# Connect to k3d services
Dev container must be in the same network as k3d containers:
Add to devcontainer.json or with ``ocker network connect` command
```
"runArgs": [
    "--network=host",
],
```
# Add certificate to the dev container
Download the certificate
```
export JENKINS_URL=jenkins.localhost:11443
openssl s_client -showcerts -connect $JENKINS_URL </dev/null | sed -n -e '/-.BEGIN/,/-.END/ p' > /usr/local/share/ca-certificates/my-selfsigned-cert-jenkins.crt
update-ca-certificates
curl https://$JENKINS_URL
```


Test:
```
curl https://minio-backend.localhost:11443/ --insecure
```
Should get you acess denied - s3 backend does not accept http, which is ok

# DVC config
s3:
```
export AWS_ACCESS_KEY_ID=s4yZ4wDOIRTrW3zMkRmz
export AWS_SECRET_ACCESS_KEY=ZoPjYOLdHveRGhqenAKyV3cFLIEeD9obZYMXzUTq
```

Create new code location
```
dagster project scaffold-code-location --name <project_name>
```

# Run dagster job via cli

```
dagster job execute -m project_name --job train_model -d project_name/
```