# Firefly - Kresus Monorepo

## Introduction

This monorepo contains a set of microservices designed to bridge the [Kresus](https://github.com/kresusapp/kresus) personal finance manager with the [Firefly III](https://github.com/firefly-iii/firefly-iii) financial management tool. Kresus, which leverages [woob](https://gitlab.com/woob/woob) to sync bank transactions, acts as the source of truth. The application notifies users of missing transactions in Firefly and offers synchronization capabilities.

Though arguably overengineered for an everyday tool, this project serves as an excellent sandbox for microservices architecture and event-driven design in Python.

## Features

- Detects missing transactions in Firefly that are present in Kresus.
- Offers an interface for syncing transactions between the two services.
- Uses an event-driven microservices architecture.

## Microservices

- [Checker](./services/checker/README.md): Monitors for missing transactions.
- [Notifier](./services/notify/README.md) (TODO): Handles user notifications.
- [Synchronizer](./services/synchronizer/README.md): Syncs transactions between services.
- [Discord Bot](./services/discord/README.md): Provides a user interface on Discord.

## Getting Started

### Requirements

- Docker and Docker Compose for local deployment.
- Access to a Kubernetes cluster for k8s deployment.

### Installation

#### Kubernetes

1. Set up a Kubernetes cluster (Minikube or k3d for local development).
1. Rename and configure `kubernetes/02-secrets.yaml.template` to `kubernetes/02-secrets.yaml`.
1. Apply the Kubernetes manifests:

   ```bash
   kubectl apply -f kubernetes/
    ```

This is not magic, check the files to understand what is happening.


#### Docker-compose

1. Rename .env.template to .env and populate it with your values
1. Start the application stack:

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