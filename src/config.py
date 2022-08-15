from os.path import exists, expanduser, join
from configparser import ConfigParser

CONFIGFILE = join(expanduser("~"), "jget.cfg")


def create_config_manager() -> ConfigParser:
    config = ConfigParser()
    if exists(CONFIGFILE):
        config.read(CONFIGFILE)
    return config


def get_config_data() -> dict[str, str]:
    config = create_config_manager()

    auth = {}
    cfg = {}
    if "auth" in config.sections():
        auth = config["auth"]
    if "cfg" in config.sections():
        cfg = config["cfg"]

    data = {
        "username": auth.get("username", None),
        "token": auth.get("token", None),
        "outdir": cfg.get("outdir", "./packages/"),
        "endpoint": cfg.get("endpoint", "http://jget.trevor.fish/"),
    }
    return data


def save_config_data(section: str, **kwargs) -> None:
    config = create_config_manager()

    if section not in config.sections():
        config[section] = {}

    for each in kwargs:
        if kwargs[each]:
            config[section][each] = kwargs[each]

    with open(CONFIGFILE, "w+") as f:
        config.write(f)
