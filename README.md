# Connect to k3d services
Dev container must be in the same network as k3d containers:
Add to devcontainer.json or with ``ocker network connect` command
```
"runArgs": [
    "--network=<network_name>",
],
```
Port forward
```
ssh -L localhost:443:localhost:<port exposed by k3d> <user>@<ip>
eg:
ssh -L localhost:443:localhost:11443 mde@10.201.50.246
```
Test:
```
curl https://minio-backend.localhost/ --insecure
```
Should get you acess denied - s3 backend does not accept http, which is ok

# DVC config
s3:
```
export AWS_ACCESS_KEY_ID=s4yZ4wDOIRTrW3zMkRmz
export AWS_SECRET_ACCESS_KEY=ZoPjYOLdHveRGhqenAKyV3cFLIEeD9obZYMXzUTq

# export MLFLOW_TRACKING_URI=http://192.168.2.150:5035/
# export MLFLOW_S3_ENDPOINT_URL=http://192.168.2.150:9000
# export AWS_ACCESS_KEY_ID=amr-user
# export AWS_SECRET_ACCESS_KEY=amr-user
# export BACKEND_STORE_URI="postgresql://mlflow_user:mlflow@localhost:5432/mlflow_db"
# export MINIO_ROOT_USER=minioadmin
# export MINIO_ROOT_PASSWORD=CsxpIFl4NT8O1RuLN20e
# export MLFLOW_TRACKING_USERNAME=mlflowadmin
# export MLFLOW_TRACKING_PASSWORD=5qheS9140fJxL0uCrTa8

```

Create new code location
```
dagster project scaffold-code-location --name <project_name>
```

