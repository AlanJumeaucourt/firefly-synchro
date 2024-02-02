# Monorepo for the firefly - kresus application.

This application is overeengineered for training purproses. It use microservices architecture and is written in Python.

## Services

- [checkers](./services/checker/README.md)
- [notify](./services/notify/README.md)
- [synchronizer](./services/synchronizer/README.md)



## Development

### [checkers](./services/checkers/README.md)
```bash
docker build --pull --rm -t fireflysynchro-checker:latest . -f common/checker.Dockerfile
docker run -v ${PWD}/services/checker/src/:/app fireflysynchro-checker:latest
```

### [notify](./services/notify/README.md)
```bash
docker build --pull --rm -t fireflysynchro-notify:latest . -f common/notify.Dockerfile
docker run -v ${PWD}/services/notify/src/:/app fireflysynchro-notify:latest
```
