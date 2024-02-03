# Monorepo for the firefly - kresus application.

The main goal of this application is to notify the user when a transaction is missing in the firefly application and to give him the possibility to synchronize the transaction.

This application is way much overeengineered but it was for training purproses (even if I use everyday). It use microservices architecture (driven by events) and is written in Python.

It use Kafka broker to communicate between microservices and have 4 microservices.

When missing transaction is detected :
- ![missing_transaction](/services/discord/images/missing_transaction.png)

When user ask to add the transaction:
- ![transaction_added](/services/discord/images/transaction_added.png)


## Micro-services

- [checkers](./services/checker/README.md)
- [notify](./services/notify/README.md) # TODO
- [synchronizer](./services/synchronizer/README.md)
- [discord](./services/discord/README.md)

## Deploy the solution

2 options are available to deploy the solution.
Kubernetes or docker-compose.

### Kubernetes

First, you need to have a kubernetes cluster running. You can use minikube or k3d for local development or testing.

Dont forget to change `kubernetes/02-secrets.yaml.template` to `kubernetes/02-secrets.yaml` and fill yours values.

Then, you need to apply the kubernetes resources.

```bash
kubectl apply -f kubernetes/
```

This is not magic, check the files to understand what is happening.


### Docker-compose

You can also deploy the solution using docker-compose.

First, you need to change the `.env.template` file to `.env` and fill yours values.

Then, you can run the following command to start the solution.
```bash
docker-compose up
```

## Development

in root directory, you can run the following command to start developing in locally.

### [checkers](./services/checkers/README.md)
```bash
docker build --pull --rm -t fireflysynchro-checker:latest . -f common/checker.Dockerfile
docker run -v ${PWD}/services/checker/src/:/app fireflysynchro-checker:latest
```

### [discord](./services/discord/README.md)
```bash
docker build --pull --rm -t fireflysynchro-discord:latest . -f common/discord.Dockerfile
docker run -v ${PWD}/services/discord/src/:/app fireflysynchro-discord:latest
```

### [synchronizer](./services/synchronizer/README.md)
```bash
docker build --pull --rm -t fireflysynchro-synchronizer:latest . -f common/synchronizer.Dockerfile
docker run -v ${PWD}/services/synchronizer/src/:/app fireflysynchro-synchronizer:latest
```



### Build and push all images to docker hub
Bash commands to build and push all images to docker hub by hand. (CI/CD do it automatically)
```bash
docker build -t alanjumeaucourt/firefly-synchro-discord -f common/discord.Dockerfile .
docker push alanjumeaucourt/firefly-synchro-discord

docker build -t alanjumeaucourt/firefly-synchro-checker -f common/checker.Dockerfile .
docker push alanjumeaucourt/firefly-synchro-checker

docker build -t alanjumeaucourt/firefly-synchro-synchronizer -f common/synchronizer.Dockerfile .
docker push alanjumeaucourt/firefly-synchro-synchronizer
```