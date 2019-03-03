# -*- coding: utf-8 -*-

import json
import os
import sys
from pathlib import Path

from utils import mangle

CONFIG = "~/.config/meross/config.json"


def go(opts):
    exists(fail=True)
    cfg = load()
    if os.getuid() == 0:
        if opts.ssid:
            opts.ssid = mangle(opts.ssid)
        if opts.password:
            opts.password = mangle(opts.password)

        root_update(cfg, opts)
        save(cfg)
    else:
        # Normal user mode
        update(cfg, opts)
        save(cfg)
    if opts.show:
        print(json.dumps(cfg, indent=4))


def exists(user=CONFIG, fail=True):
    cfgfile = Path.expanduser(Path(CONFIG))
    if fail and not cfgfile.exists():
        sys.exit("No configuration file, run 'meross init' first")
    return cfgfile.exists()


def load(user=CONFIG):
    cfgfile = Path.expanduser(Path(user))
    if not cfgfile.exists():
        cfgfile.parent.mkdir(parents=True, exist_ok=True)
        save(dict())
    cfg = json.loads(cfgfile.read_text())
    return cfg


def update(cfg, opts, attrs=["server", "port", "ca_cert"]):
    for attr in attrs:
        if getattr(opts, attr):
            cfg[attr] = getattr(opts, attr)


def root_update(cfg, opts):
    update(cfg, opts, attrs=["user", "ssid", "password", "interface"])


def user_config_file(user):
    return "/home/" + user + "/.config/meross/config.json"


def load_user(user):
    return load(user_config_file(user))


def save(cfg, user=CONFIG):
    cfgfile = Path.expanduser(Path(user))
    cfgfile.write_text(json.dumps(cfg, indent=4))
    cfgfile.chmod(0o600)


def save_user(cfg, user):
    save(cfg, user_config_file(user))


def add_device(dev, opts, user):
    cfg = load_user(user)
    devices = cfg.get("devices")
    if list(dev.keys())[0] in devices:
        if not opts.force:
            sys.exit("Unable to overwrite device unless you use --force")
    cfg["devices"].update(dev)
    save_user(cfg, user)


def list_devices(cfg):
    return list(cfg["devices"].keys())
