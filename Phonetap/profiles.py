import json
from copy import deepcopy
from os import path

import click

import Phonetap.phonetap_cli
from Phonetap.phonetap_cli import cli

PROFILES_JSON = 'profiles.json'
profiles_json = path.sep.join(path.realpath(__file__).split(path.sep)[:-1] + [PROFILES_JSON])

with open(profiles_json) as j:
    pass


def explode_profile(profile_name, username, password, host, port, local, directories, extensions, add_directories,
                    remove_directories, add_extensions, remove_extensions):
    profile = profiles[profile_name]
    print('explode profile')
    print(json.dumps({'profile_name'      : profile_name,
                      'username'          : username,
                      'password'          : password,
                      'host'              : host,
                      'port'              : port,
                      'local'             : local,
                      'directories'       : directories,
                      'extensions'        : extensions,
                      'add_directories'   : add_directories,
                      'remove_directories': remove_directories,
                      'add_extensions'    : add_extensions,
                      'remove_extensions' : remove_extensions
                      }, indent=4))
    return username if username else profile['username'], \
        password if password else profile['password'], \
        local if local else profile['local_directory'], \
        host if host else profile['remote_host'], \
        port if port else profile['port'], \
        directories if directories else \
            set(profile['remote_directories']) \
                .union(add_directories if add_directories else []) \
                .difference(remove_directories if remove_directories else []), \
        extensions if extensions else \
            set(profile['extensions']) \
                .union(add_extensions if add_extensions else add_extensions) \
                .difference(remove_extensions if remove_extensions else remove_extensions)


def edit(profile, username, password, host, port, local,
         directories, extensions,
         add_directories, remove_directories,
         add_extensions, remove_extensions, model):
    dic = deepcopy(profiles.get(profile, profiles.get(model, {})))
    if local:
        dic['local_directory'] = local
    if directories:
        dic['directories'] = directories.split(';')
    if extensions:
        dic['extensions'] = extensions.split(';')
    if add_directories:
        dic['remote_directories'] = dic['remote_directories'] + add_directories.split(';')
    if add_extensions:
        dic['extensions'] = dic['extensions'] + add_extensions.split(';')
    if remove_directories:
        rm = remove_directories.split(';')
        dic['directories'] = [d for d in dic['directories'] if d not in rm]
    if remove_extensions:
        rm = remove_extensions.split(';')
        dic['extensions'] = [e for e in dic['extensions'] if e not in rm]
    if username:
        dic['username'] = username
    if password:
        dic['password'] = username
    if host:
        dic['remote_host'] = host
    if port:
        dic['port'] = port
    profiles[profile] = dic
    print(json.dumps(dic, indent=2))
    with open(profiles_json, 'w') as j:
        dumps = json.dumps(profiles, indent=2)
        j.write(dumps)


profiles = json.loads(j.read())


@profile.command('list')
def list():
    print(f'Available profiles are :{profiles.keys()}')


@profile.command('show')
@click.option('--profile', default='')
def show(profile=None):
    if profile:
        print(json.dumps(profiles[profile], indent=2))
    else:
        # list_profiles()
        print(f'Available profiles are :{profiles.keys()}')
