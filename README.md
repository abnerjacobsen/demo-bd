[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/abnerjacobsen/demo-bd) [![Open in GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=blue&logo=github)](https://codespaces.new/abnerjacobsen/demo-bd)

# demo-bd

Awesome demo_bd created by abnerjacobsen

# Install the dependencies and create virtualenv

```sh
poetry shell
poetry install
```

## Using

To serve this app in dev mode, run:

```sh
ENVIRONMENT=dev poe api --dev
```
and open [localhost:8000](http://localhost:8000) in your browser.


## Using  with Docker

To build the container for using with docker:

```sh
docker compose build app
```

To run the container with docker compose:

```sh
docker compose --profile app up -d
```

and open [localhost:8000](http://localhost:8000) in your browser.

To stop the running container's with docker compose:

```sh
docker compose --profile app down
```


