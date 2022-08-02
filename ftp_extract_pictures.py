import json
import re
from copy import deepcopy
from datetime import datetime
from ftplib import FTP
from os import listdir, path, remove

import click

PROFILES_JSON = 'profiles.json'

with open(PROFILES_JSON) as j:
    profiles = json.loads(j.read())


def explode_profile(profile_name):
    profile = profiles[profile_name]
    return profile['username'], \
           profile['password'], \
           profile['local_directory'], \
           profile['remote_host'], \
           profile['port'], \
           profile['remote_directories'], \
           profile['extensions']


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
def _explore(profile: str, directory: str):
    username, password, _, remote_host, port, _, _ = explode_profile(profile)

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
    return date_threshold, lambda _: remove(file_full_name)


@profile.command('list')
def list_profiles():
    print(f'Available profiles are :{profiles.keys()}')


@profile.command('show')
@click.option('--profile', default='')
def show_profile(profile = None):
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
        dic['directories'] = dic['directories'] + add_directories.split(';')
    if add_extensions:
        dic['extensions'] = dic['extentions'] + add_extensions.split(';')
    if remove_directories:
        rm = remove_directories.split(';')
        dic['directories'] = [d for d in dic['directories'] if d not in rm]
    if remove_extensions:
        rm = remove_extensions.split(';')
        dic['extensions'] = [e for e in dic['extentions'] if e not in rm]
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
    with open(PROFILES_JSON, 'w') as j:
        dumps = json.dumps(profiles, indent=2)
        j.write(dumps)


@ftp.command('extract')
@click.option('--profile', prompt='profile name')
def _extract(profile):
    username, password, local_directory, remote_host, port, remote_directories, extensions = explode_profile(profile)

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

            def deep_list(directory: str, min_date, recurse):
                for name, attributes in ftp.mlsd(directory):
                    sub_directory = f'{directory}/{name}'
                    if attributes['type'] == 'dir' and sub_directory not in exclusions and recurse:
                        for (d, n, a) in deep_list(sub_directory, min_date, recurse):
                            yield d, n, a
                    else:
                        modify = attributes['modify'] = datetime_from_utc_to_local(
                            datetime.strptime(attributes['modify'],
                                              '%Y%m%d%H%M%S.%f')) if 'modify' in attributes else None
                        if modify > min_date and ext_re.match(name):
                            yield directory, name, attributes

            for remote_directory in remote_directories:
                for (d, n, a) in deep_list(remote_directory, date_threshold, recurse=True):
                    file = path.join(local_directory, n)
                    msg = f'Getting {file} from {d}/{n} ({int(a["size"]) / 1024 / 1024:,.3f} Mb)...'
                    if path.isfile(file) and path.getsize(file) == int(a["size"]):
                        print(f'{msg} already exists')
                    else:
                        print(msg)
                        ftp.retrbinary('RETR ' + d + '/' + n, open(file, 'wb').write)
                        print(f'{msg} Done.')

        date_threshold = datetime.now()

    except Exception as e:
        print(e)

    if date_threshold:
        threshold_file = path.join(local_directory, f"lastTimestamp_{date_threshold.strftime('%Y-%m-%d_%H-%M')}.txt")
        with open(threshold_file, 'w') as ts:
            ts.write(date_threshold.strftime('%Y-%m-%d %H:%M'))
            remover(None)
        print(f'Created threshold file {threshold_file}.')


if __name__ == '__main__':
    _explore()
    # extract(profile="philippe")
    # explore("philippe", '/')
    # extract("severine")
    # explore("severine", '/Pictures/Screenshots')
