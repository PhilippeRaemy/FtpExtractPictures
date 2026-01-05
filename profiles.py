import json
from copy import deepcopy

import click

from ftp_extract_pictures import profile, profiles_json, j


def explode_profile(profile_name, username, password, host, port, local, directories, extensions, add_directories,
                    remove_directories, add_extensions, remove_extensions):
    profile = profiles[profile_name]
    print('explode profile')
    print(json.dumps({'profile_name': profile_name,
                      'username': username,
                      'password': password,
                      'host': host,
                      'port': port,
                      'local': local,
                      'directories': directories,
                      'extensions': extensions,
                      'add_directories': add_directories,
                      'remove_directories': remove_directories,
                      'add_extensions': add_extensions,
                      'remove_extensions': remove_extensions
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


@profile.command('edit')
@click.option('--profile', required=True)
@click.option('--username', required=False, default=None, type=str)
@click.option('--password', required=False, default=None, type=str)
@click.option('--host', required=False, default=None, type=str)
@click.option('--port', required=False, default=None, type=int)
@click.option('--local', required=False, default=None, type=str)
@click.option('--directories', required=False, default=None, type=str)
@click.option('--extensions', required=False, default=None, type=str)
@click.option('--add_directories', required=False, default=None, type=str)
@click.option('--remove_directories', required=False, default=None, type=str)
@click.option('--add_extensions', required=False, default=None, type=str)
@click.option('--remove_extensions', required=False, default=None, type=str)
@click.option('--model', required=False, default=None, type=str)
def edit_profile(profile, username=None, password=None, host=None, port=None, local=None,
                 directories=None, extensions=None,
                 add_directories=None, remove_directories=None,
                 add_extensions=None, remove_extensions=None, model='default'):
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
def list_profiles():
    print(f'Available profiles are :{profiles.keys()}')


@profile.command('show')
@click.option('--profile', default='')
def show_profile(profile=None):
    if profile:
        print(json.dumps(profiles[profile], indent=2))
    else:
        # list_profiles()
        print(f'Available profiles are :{profiles.keys()}')
