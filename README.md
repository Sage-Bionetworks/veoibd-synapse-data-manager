[![Documentation Status](https://readthedocs.org/projects/veoibd-synapse-data-manager/badge/?version=latest)](http://veoibd-synapse-data-manager.readthedocs.io/?badge=latest)


# Project Description
Admin related logistics regarding uploading and annotating data to Synapse for members of the VEOIBD consortium.

# Before we begin

There are a few things that we take for granted at this point.

1. You are a registered Synapse user.
2. You have either [Conda or Miniconda installed.](http://conda.pydata.org/docs/download.html#should-i-download-anaconda-or-miniconda)
3. You have the ability to execute Makefiles.
    - Linux/Unix/OS X **should** work fine out of the box.
    - Windows will need [Cygwin](https://en.wikipedia.org/wiki/Cygwin) installed or take advantage of the ability to run bash in Windows 10.

## Registering with [Synapse](https://www.synapse.org/)

1. Create an account at [Synapse](https://www.synapse.org/)
2. You will need to register and become a [certified user](http://docs.synapse.org/articles/getting_started.html#becoming-a-certified-user).

## Installing

### Download this project repository

Using git...

```shell
git clone https://github.com/ScottSnapperLab/veoibd-synapse-data-manager.git
```

Using your web browser...

1. Click [here](https://github.com/ScottSnapperLab/veoibd-synapse-data-manager/releases) to see a list of releases.
2. Download and unzip.
3. Navigate into the project folder.

### "Install" the package

At your terminal, in the directory we created above:

```shell
make install
```

Now activate the conda environment that we just created with this command:

```shell
source activate veoibd_synapse
```

And let's see the program's main help text:

```shell
$ veoibd_synapse --help
Usage: veoibd_synapse [OPTIONS] COMMAND [ARGS]...

  Command interface to the veoibd-synapse-manager.

  For command specific help text, call the specific command followed by the
  --help option.

Options:
  -c, --config DIRECTORY  Path to optional config directory. If `None`,
                          configs/ is searched for *.yaml files.
  --home                  Print the home directory of the install and exit.
  --help                  Show this message and exit.

Commands:
  configs  Manage configuration values and files.
  push     Consume a push-config file, execute described...
```



## Configuring

The `configs/factory_resets` folder contains examples of configuration files.  Modify the values to fit your site's information.

To generate fresh example configs in the `config` directory  we use the `veoibd_synapse configs` command.

```shell
Usage: veoibd_synapse configs [OPTIONS]

  Manage configuration values and files.

Options:
  -l, --list                      Print the configuration values that will be
                                  used and exit.
  -g, --generate-configs          Copy one or more of the 'factory default'
                                  config files to the top-level config
                                  directory. Back ups will be made of any
                                  existing config files.  [default: False]
  -k, --kind [all|site|users|projects|push|pull]
                                  Which type of config should we replace?
                                  [default: all]
  --help                          Show this message and exit.
```

Run this command to get fresh configs:

```shell
veoibd_synapse configs --generate-configs
```


## Uploading a batch of files

- You need to have a project created on Synapse for the files to be sent to.
- You will need to have created the appropriate configuration files:
    - See the config section

Lets take a look at the help text for the `push` command:

```shell
$ veoibd_synapse push  --help

Usage: veoibd_synapse push [OPTIONS]

  Consume a push-config file, execute described transactions, save record of
  transactions.

Options:
  -u, --user TEXT     Provide the ID for a user listed in the 'users' config
                      file.
  --push-config PATH  Path to the file where this specific 'push' is
                      configured.
  --help              Show this message and exit.
```

And a quick example command would be:

```shell
$ veoibd_synapse push -u GUSDUNN --push-config configs/GUSDUNN/new_WES_files.yaml
```
