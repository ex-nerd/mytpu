# mytpu

Command line client for Tacoma Public Utilities usage data.

This is still very much a work in progress.

The final result is intended to provide usage data to be fed to [Home Assistant](https://www.home-assistant.io/integrations/utility_meter/)

Help wanted (and given): https://community.home-assistant.io/t/tacoma-public-utilities-smart-water-power-meter-integration/451418

## Development / Usage

Since this is still under development and doesn't have a published package,
you'll need to set things up by hand. The fastest way to do this is just to run
the following command from the source directory. This will give you access to
the `mytpu` command line client, pointed at the copy of the library in this
repository so you can develop against it.


```bash
pip install -e .
```

You can install this into your system python, but I recommend looking at the
`direnv` setup below for better isolation.

### Direnv

You can use system python, but I prefer to develop in a virtualenv. The easiest
way I've found to set this up is to use [direnv](https://direnv.net/) and let it
manage all of that for you. Follow the install instructions for `direnv` for
your shell, and then when you come back to this directory, run `direnv allow`
and it will install the python virtualenv for you automatically.
