# KIPA with Docker

This project contains Dockefile that can be used to create own test enviroment of KIPA.
Docker makes it easy to create light weight and disposable enviroments.

## How to setup KIPA Docker test env

While in folder KIPA project root dir build :

```
docker build -t kipa/dev .
```

And after that run container image:

```
docker run -d -p 8000:8000 kipa/dev
```

This does command start container to background and makes port forwarding to containers 8000 port to hosts 8000 port.

After that you can open browser and go to http://host_ip:8000/kipa

## Build KIPA image from Github

Docker enbables also building from remote `Dockerfile`. So there is no need to clone KIPA repo to your local machine to run KIPAs Docker container.

To build container from remote `Dockerfile` and run container for testing KIPA:

```
docker build -t kipa/dev https://raw.githubusercontent.com/siimeon/Kipa/master/Dockerfile
docker run -d -p 8000:8000 kipa/dev
```

