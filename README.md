# Mindustry Pal

> Your fellow pal helping you with [Mindustry Game](https://github.com/anuken/mindustry)

```console
$ mindustry --help          
usage: mindustry [-h] [-q] [-v] command ...

A CLI for managing Mindustry game versions and campaigns.

positional arguments:
  command
    store        Store (dump) current Mindustry campaign in a file.
    switch       Switch between Mindustry campaigns.
    ...
```

## What's this?

I am a simple working man who enjoys playing Mindustry and is lazy enough to get annoyed at manually downloading new versions of the game and managing different playthroughs all by the buttons in the game.

So, **Mindutry Pal** automates exactly this thing: it stores current saves, mods and settings the way game makes backups (in `.zip` files) and allows you to switch between them and create new ones.

I also said something about downloading versions but Mindustry Pal cannot do it *yet*. Maybe, some time...

## Installation

This command line utility is a standard Python package and it is published on PyPI, so you can install it via `pip` or other package managers.

```sh
pip install mindustry-pal

mindustry-pal --help
```

You can also use it with [`uv`](https://docs.astral.sh/uv/) as a tool or dependency:

```sh
# No separate installation step!
uvx mindustry-pal --help

# Can be installed into its own isolated environment!
uv tool install mindustry-pal

mindustry --help
```

## Basic Usage

You can run Mindustry Pal with either of two commands (they are just aliases):

* `mindustry-pal`
* `mindustry`

### Quick Workflow

Say, you've got a lot of mods on version 5.0 and noticed Anuken made a couple of releases. Now, you want to update to 8.0 and start from the scratch. That's what you do:

```sh
# Save current prograss into a campaign file
mindustry store my-old-modded-chaos

# Create a brand new empty campaign for new game version
mindustry create 8.0-playthrough

# Now, you're ready to play!

# Wanna get back to legacy experience? Return your saves? Just switch back:
mindustry switch my-old-modded-chaos
```

### List of commands

This utility features the following commands:

* `store [name]`: stores your current Mindustry campaign into a `.zip` file.
* `restore [name]`: overrides your game files with those stored in a `.zip` file.
* `create <name>`: creates a new empty campaign and switches to it (current is automatically saved).
* `switch <name>`: safely switches from one campaign to another.
* `status`: tells you information about your current campaign save file.
* `list`: prints a list of all campaigns currently stored on disk.

## Where the campaigns go?

> Whatcha doin with my files, man?

Mindustry-Pal uses your operating system's standard app data directory. It keeps its config file and zipped campaigns in a dedicated `Mindustry-Pal` folder (just next to where `Mindustry` folder is).

The path is as follows:

* **Windows**: `%APPDATA%\Mindustry-Pal`
* **Linux**: `~/.local/share/Mindustry-Pal` or `$XDG_DATA_HOME/Mindustry-Pal`
* **macOS**: `~/Library/Application Support/Mindustry-Pal`

<!-- TODO: Write about contribution, manual builds, maybe something else -->
