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
```

Create new code location
```
dagster project scaffold-code-location --name <project_name>
```

# Run dagster job via cli

```
dagster job execute -m project_name --job train_model -d project_name/
```