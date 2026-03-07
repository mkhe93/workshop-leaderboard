# Masterclass | DecompileD 2026

#### Vibes ship demos. Specs ship products.
Vibe coding helps you move fast—but not far, as brownfield success starts with clarity.

Spec-Driven Development is how teams keep velocity after the prototype: by writing specs that make context explicit, align stakeholders, and capture human intent—so everyone builds the same thing for the same reasons, especially when you’re working on top of what already exists.

### TOC

<!-- TOC -->
* [Requirements](#requirements)
* [0. Prerequisites](#0-prerequisites)
  * [0.1 Setup the Devcontainer](#01-setup-the-devcontainer)
  * [0.2 Enter the Devcontainer](#02-enter-the-devcontainer)
  * [0.3 Obtain your API Key](#03-obtain-your-api-key)
<!-- TOC -->

### Requirements
- Docker
- VSCode (for Windows it is recommended not to use WSL)

## 0. Prerequisites

### 0.1 Setup the Devcontainer

Download secrets and env variables from
- [https://secrets.devboost.com/en/p/jfmey_phud118jc/r](https://secrets.devboost.com/en/p/jfmey_phud118jc/r) 

and paste them in the `.devcontainer/devcontainer.env` file.

### 0.2 Enter the Devcontainer

<u>Option 1:</u> VScode will automatically detect the `.devcontainer` folder and prompt you to reopen the project in the container.

<img src="./assets/devcontainer_reopen_prompt.png" alt="Leaderboard" width="300"/>

<u>Option 2:</u> You can manually reopen the project by typing `> Dev Containers: Reopen in Container` in the top search bar of VScode:

<img src="./assets/devcontainer_reopen_command.png" alt="Leaderboard" width="300"/>

### 0.3 Obtain your API Key

Once you've entered the devcontainer, open a new terminal and run the following command to obtain your API key for Claude Code:

```bash
./get_api_key.sh YourFirstName YourLastName
```

Follow the instructions prompted by the script and you're ready for the masterclass! 🎉

See you on Thursday!
