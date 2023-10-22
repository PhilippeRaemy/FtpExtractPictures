import json
import re
from copy import deepcopy
from datetime import datetime
from ftplib import FTP
from os import listdir, path, remove
from typing import List

import click

PROFILES_JSON = 'profiles.json'
profiles_json = path.sep.join(path.realpath(__file__).split(path.sep)[:-1] + [PROFILES_JSON])

with open(profiles_json) as j:
    profiles = json.loads(j.read())


def explode_profile(profile_name, username, password, host, port, local, directories, extensions, add_directories,
                    remove_directories, add_extensions, remove_extensions):
    profile = profiles[profile_name]
    print('explode profile')
    print(json.dumps({'profile_name':profile_name,
                    'username':username,
                    'password':password,
                    'host':host,
                    'port':port,
                    'local':local,
                    'directories':directories,
                    'extensions':extensions,
                    'add_directories':add_directories,
                    'remove_directories':remove_directories,
                    'add_extensions':add_extensions,
                    'remove_extensions':remove_extensions
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


@click.group()
@click.version_option()
def cli():
    """Handle pictures from phone via FTP"""


@cli.group()
def ftp():
    """FTP operations"""


@cli.group()
def profile():
    """profile operations"""


@ftp.command("explore")
@click.option('--profile', prompt='profile name')
@click.option('--directory', prompt='root directory')
@click.option('--username', required=False, default=None, type=str)
@click.option('--password', required=False, default=None, type=str)
@click.option('--host', required=False, default=None, type=str)
@click.option('--port', required=False, default=None, type=int)
@click.option('--local', required=False, default=None, type=str)
@click.option('--extensions', required=False, default=[], type=List[str])
@click.option('--add_extensions', required=False, default=[], type=List[str])
@click.option('--remove_extensions', required=False, default=[], type=List[str])
def _explore(profile: str, directory: str, username, password, host, port, local,
             extensions,
             add_extensions, remove_extensions):
    username, password, _, remote_host, port, _, _ = explode_profile(profile, username, password, host, port, local,
                                                                     [], extensions,
                                                                     [], [],
                                                                     add_extensions, remove_extensions)

    with FTP() as ftp:
        print(f'Connecting to {remote_host}:{port}')
        ftp.connect(host=remote_host, port=port)
        ftp.login(user=username, passwd=password)
        print(ftp.getwelcome())
        for name, attributes in ftp.mlsd(directory):
            print(name, attributes)


def remove_timestamp_file(local_directory):
    re_file = re.compile('lastTimestamp.*.txt', re.IGNORECASE)
    date_threshold = datetime(1900, 1, 1)

    file_full_name = None
    for lastTimestamp in sorted(fi for fi in listdir(local_directory) if re_file.match(fi)):
        file_full_name = path.join(local_directory, lastTimestamp)
        with open(file_full_name, 'r', encoding='utf-8') as ts:
            for li in ts.readlines():
                try:
                    date = datetime.strptime(li.strip(), '%Y-%m-%d %H:%M')
                    if date_threshold < date:
                        date_threshold = date
                except:
                    pass
    return date_threshold, (lambda _: remove(file_full_name)) if file_full_name else None


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


@profile.command()
@click.option('--n', default=3)
def dots(n):
    click.echo('.' * n)


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


@ftp.command('extract')
@click.option('--profile', prompt='profile name')
@click.option('--username', required=False, default=None, type=str)
@click.option('--password', required=False, default=None, type=str)
@click.option('--host', required=False, default=None, type=str)
@click.option('--port', required=False, default=None, type=int)
@click.option('--local', required=False, default=None, type=str)
# @click.option('--directories', required=False, default=[], type=List[str])
# @click.option('--extensions', required=False, default=[], type=List[str])
# @click.option('--add_directories', required=False, default=[], type=List[str])
# @click.option('--remove_directories', required=False, default=[], type=List[str])
# @click.option('--add_extensions', required=False, default=[], type=List[str])
# @click.option('--remove_extensions', required=False, default=[], type=List[str])
def _extract(profile, username, password, host, port, local): #, directories, extensions, add_directories,             remove_directories, add_extensions, remove_extensions):
    directories=[]
    extensions=[]
    add_directories=[]
    remove_directories=[]
    add_extensions=[]
    remove_extensions=[]

    username, password, local_directory, remote_host, port, remote_directories, extensions \
        = explode_profile(profile, username, password, host, port, local,
                          directories, extensions,
                          add_directories, remove_directories,
                          add_extensions, remove_extensions)

    ext_re = re.compile('^.*\\' + ('$|^.*\\'.join(extensions)) + '$', re.IGNORECASE)

    exclusions = ['Android/media/ga.asti.android']

    date_threshold = None
    try:
        with FTP() as ftp:
            print(f'Connecting to {remote_host}:{port}')
            ftp.connect(host=remote_host, port=port)
            ftp.login(user=username, passwd=password)
            print(ftp.getwelcome())

            date_threshold, remover = remove_timestamp_file(
                local_directory)  # do this only when FTP connection was successful

            def datetime_from_utc_to_local(utc_datetime):
                ts = utc_datetime.timestamp()
                return utc_datetime + (datetime.fromtimestamp(ts) - datetime.utcfromtimestamp(ts))

            def deep_list(directory: str, recurse):
                for name, attributes in ftp.mlsd(directory):
                    sub_directory = f'{directory}/{name}'
                    if attributes['type'] == 'dir' and sub_directory not in exclusions and recurse:
                        for (d, n, a, m) in deep_list(sub_directory, recurse):
                            yield d, n, a, m
                    else:
                        modify = attributes['modify'] = datetime_from_utc_to_local(
                            datetime.strptime(attributes['modify'],
                                              '%Y%m%d%H%M%S.%f')) if 'modify' in attributes else None
                        if ext_re.match(name):
                            yield directory, name, attributes, modify

            for remote_directory in remote_directories:
                print(remote_directory)
                for (d, n, a, m) in deep_list(remote_directory, recurse=True):
                    file = path.join(local_directory, n)
                    msg = f'Getting {file} from {d}/{n} ({int(a["size"]) / 1024 / 1024:,.3f} Mb)...'
                    if m < date_threshold:
                        pass
                        # print(f'{msg} is before date threshold')
                    elif path.isfile(file) and path.getsize(file) == int(a["size"]):
                        print(f'{msg} already exists')
                    else:
                        print(msg, end='')
                        ftp.retrbinary('RETR ' + d + '/' + n, open(file, 'wb').write)
                        print(' Done.')

        date_threshold = datetime.now()

    except Exception as e:
        print(e)

    if date_threshold:
        threshold_file = path.join(local_directory, f"lastTimestamp_{date_threshold.strftime('%Y-%m-%d_%H-%M')}.txt")
        with open(threshold_file, 'w') as ts:
            ts.write(date_threshold.strftime('%Y-%m-%d %H:%M'))
            if remover:
                remover(None)
        print(f'Created threshold file {threshold_file}.')


if __name__ == '__main__':
    _explore()
    # extract(profile="philippe")
    # explore("philippe", '/')
    # extract("severine")
    # explore("severine", '/Pictures/Screenshots')
