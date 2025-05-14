[![Open in Dev Containers](https://img.shields.io/static/v1?label=Dev%20Containers&message=Open&color=blue&logo=visualstudiocode)](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/snapenv/snap-backend-template) [![Open in GitHub Codespaces](https://img.shields.io/static/v1?label=GitHub%20Codespaces&message=Open&color=blue&logo=github)](https://codespaces.new/snapenv/snap-backend-template)

# Contributing to snap-backend-template

This is an open-source project and we welcome contributions.

## 👩‍💻 How to contribute

Please follow the [fork and pull request](https://docs.github.com/en/get-started/quickstart/contributing-to-projects) workflow:

- Fork the repository.
- Create a new branch for your feature.
- Add your feature or improvement.
- Send a pull request.
- We appreciate your support & input!

-----------------------
Contribution guidelines
-----------------------

Please:

1. Keep your commits modular
2. Add descriptive commit messages
3. Use conventional commits
4. Attach a PR to an issue if applicable
5. Ensure all new features have tests
6. Add documentation for new features

## Project setup

1. Clone the repository.
2. Create a virtual environment:
```sh
poetry install
```
   - This setup will:
     - Create a `.venv` virtual environment in the current directory.
     - Install the required packages.
     - Install the `snap-backend-template` package in editable mode.
3. Activate the virtual environment:
```sh
poetry shell
```
4. Test that the Python development environment is working:
```sh
ENVIRONMENT=dev poe test
```
- This setup will:
    - Use `dev.env` file as source of settings for the API server.
    - Starts a FastAPI server at `http://0.0.0.0:8000`.
    - Install the `snap-backend-template` package in editable mode.
- And open [localhost:8000/docs](http://localhost:8000/docs) in your browser.

## Developing using Docker

To serve this app, run:

```sh
docker compose --profile app up -d
```

and open [localhost:8000/docs](http://localhost:8000/docs) in your browser.

Within the Dev Container this is equivalent to:

```sh
ENVIRONMENT=dev poe api --dev
```

To stop, run:

```sh
docker compose --profile app down
```

| :boom: About env configuration |
|:-------------------------------|
| You can choose wich env file to use when running the app using the **ENVIRONMENT** env variable. If you set **ENVIRONMENT=dev** the app will read the `dev.env` file. If **ENVIRONMENT** is not set, the app will use the `.env` file. Off course, you can set all needed variables manually in the envionroment of your shell. |

## Formatting and validation

Ensure your code meets our quality standards by running the appropriate formatting and validation script before submitting a pull request:
   - `poe lint`
   - `ENVIRONMENT=dev poe test`
These scripts will perform code formatting with `ruff`, static type checks with `mypy`, and run unit tests with `pytest`.


## Contributing

<details>
<summary>Prerequisites</summary>

<details>
<summary>1. Set up Git to use SSH</summary>

1. [Generate an SSH key](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/generating-a-new-ssh-key-and-adding-it-to-the-ssh-agent#generating-a-new-ssh-key) and [add the SSH key to your GitHub account](https://docs.github.com/en/authentication/connecting-to-github-with-ssh/adding-a-new-ssh-key-to-your-github-account).
1. Configure SSH to automatically load your SSH keys:
    ```sh
    cat << EOF >> ~/.ssh/config
    
    Host *
      AddKeysToAgent yes
      IgnoreUnknown UseKeychain
      UseKeychain yes
      ForwardAgent yes
    EOF
    ```

</details>

<details>
<summary>2. Install Docker</summary>

1. [Install Docker](https://www.docker.com/get-started).
    - _Linux only_:
        - Export your user's user id and group id so that [files created in the Dev Container are owned by your user](https://github.com/moby/moby/issues/3206):
            ```sh
            cat << EOF >> ~/.bashrc
            
            export UID=$(id --user)
            export GID=$(id --group)
            EOF
            ```

</details>

<details>
<summary>3. Install VS Code or PyCharm</summary>

1. [Install VS Code](https://code.visualstudio.com/) and [VS Code's Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers). Alternatively, install [PyCharm](https://www.jetbrains.com/pycharm/download/).
2. _Optional:_ install a [Nerd Font](https://www.nerdfonts.com/font-downloads) such as [FiraCode Nerd Font](https://github.com/ryanoasis/nerd-fonts/tree/master/patched-fonts/FiraCode) and [configure VS Code](https://github.com/tonsky/FiraCode/wiki/VS-Code-Instructions) or [configure PyCharm](https://github.com/tonsky/FiraCode/wiki/Intellij-products-instructions) to use it.

</details>

</details>

<details open>
<summary>Development environments</summary>

The following development environments are supported:

1. ⭐️ _GitHub Codespaces_: click on _Code_ and select _Create codespace_ to start a Dev Container with [GitHub Codespaces](https://github.com/features/codespaces).
1. ⭐️ _Dev Container (with container volume)_: click on [Open in Dev Containers](https://vscode.dev/redirect?url=vscode://ms-vscode-remote.remote-containers/cloneInVolume?url=https://github.com/snapenv/snap-backend-template) to clone this repository in a container volume and create a Dev Container with VS Code.
1. _Dev Container_: clone this repository, open it with VS Code, and run <kbd>Ctrl/⌘</kbd> + <kbd>⇧</kbd> + <kbd>P</kbd> → _Dev Containers: Reopen in Container_.
1. _PyCharm_: clone this repository, open it with PyCharm, and [configure Docker Compose as a remote interpreter](https://www.jetbrains.com/help/pycharm/using-docker-compose-as-a-remote-interpreter.html#docker-compose-remote) with the `dev` service.
1. _Terminal_: clone this repository, open it with your terminal, and run `docker compose up --detach dev` to start a Dev Container in the background, and then run `docker compose exec dev zsh` to open a shell prompt in the Dev Container.

</details>

<details>
<summary>Developing</summary>

- This project follows the [Conventional Commits](https://www.conventionalcommits.org/) standard to automate [Semantic Versioning](https://semver.org/) and [Keep A Changelog](https://keepachangelog.com/) with [Commitizen](https://github.com/commitizen-tools/commitizen).
- Run `poe` from within the development environment to print a list of [Poe the Poet](https://github.com/nat-n/poethepoet) tasks available to run on this project.
- Run `poetry add {package}` from within the development environment to install a run time dependency and add it to `pyproject.toml` and `poetry.lock`. Add `--group test` or `--group dev` to install a CI or development dependency, respectively.
- Run `poetry update` from within the development environment to upgrade all dependencies to the latest versions allowed by `pyproject.toml`.
- Run `poe docs`, `poe lint` and `ENVIRONMENT=dev poe test` before any commit, or your git push can fail. `poe docs` generate any new documentation for changes/additions in the python modules.
- Run `cz --name cz_gitmoji commit` so commit files using conventional commits with emojis.
- Run `cz bump` to bump the app's version, update the `CHANGELOG.md`, and create a git tag.
- Run `git push --tags` to push the new tag to github.

</details>
