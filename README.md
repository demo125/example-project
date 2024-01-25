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
export JENKINS_URL=jenkins.mlplatform:11443
openssl s_client -showcerts -connect $JENKINS_URL </dev/null | sed -n -e '/-.BEGIN/,/-.END/ p' > /usr/local/share/ca-certificates/my-selfsigned-cert-jenkins.crt
update-ca-certificates
curl https://$JENKINS_URL
```
Test:
```
curl https://minio-backend.mlplatform:11443/ --insecure
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
```
dagster asset materialize -m project_name --select dvc_dataset -d project_name/ 
```

# Docker
```
docker run -it --rm  --network=host \
-e MLFLOW_TRACKING_URI="https://mlflow.mlplatform:11443"  \
-e MLFLOW_S3_ENDPOINT_URL="https://mlflow-minio-backend.mlplatform:11443"  \
-e MLFLOW_S3_AWS_ACCESS_KEY_ID="lniKPUP6Vb4niLeXwRJj"  \
-e MLFLOW_S3_AWS_SECRET_ACCESS_KEY="MziqG98YT3ThMHEuYOuDfQQQ1b3iv81tK87tETKB"  \
-e MLFLOW_TRACKING_INSECURE_TLS=True  \
-e MLFLOW_S3_IGNORE_TLS=True \
-e SEED=42 \
docker-registry.mlplatform:11443/example-project:32 \
dagster job execute -m project_name --job train_model -d project_name/ 
```
