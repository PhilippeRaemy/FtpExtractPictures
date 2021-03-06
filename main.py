from datetime import datetime
from ftplib import FTP
import re
from os import listdir, path, remove
import click

profiles = {
    'philippe': {
        'username': "philippe",
        'password': "philippe",
        'local_directory': "d:/users/public/pictures/fromphones/philippe",
        'remote_host': "192.168.0.11",
        'port': 2121,
        'remote_directories': [
            "/Pictures",
            "/DCIM",
            "/Telegram",
            "/Threema",
            "/Movies/Threema",
            "/Android/media/com.whatsapp"
        ],
        'extensions': ['.jpg', '.jpeg', '.mov', '.mp4', '.vid', '.div']},
    'severine': {
        'username': "severine",
        'password': "severine",
        'local_directory': "d:/users/public/pictures/fromphones/FairSev",
        'remote_host': "192.168.0.12",
        'port': 2121,
        'remote_directories': [
            "/Pictures",
            "/DCIM",
            "/Telegram",
            "/Threema",
            "/Movies/Threema",
            #     "/Android/media/com.whatsapp"
        ],
        'extensions': ['.jpg', '.jpeg', '.mov', '.mp4', '.vid', '.div']}
}


def explode_profile(profile_name):
    profile = profiles[profile_name]
    return profile['username'], \
           profile['password'], \
           profile['local_directory'], \
           profile['remote_host'], \
           profile['port'], \
           profile['remote_directories'], \
           profile['extensions']


# @click.command('explore')
# @click.option('--profile', prompt='profile name')
# @click.option('--directory', prompt='root directory')
def explore(profile: str, directory: str):
    username, password, _, remote_host, port, _, _ = explode_profile(profile)

    with FTP() as ftp:
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
                    date = datetime.strptime(li, '%Y-%m-%d %H:%M')
                    if date_threshold < date:
                        date_threshold = date
                except:
                    pass
        remove(file_full_name)
    return date_threshold


# @click.command('extract')
# @click.option('--profile', prompt='profile name')
def extract(profile):
    username, password, local_directory, remote_host, port, remote_directories, extensions = explode_profile(profile)

    ext_re = re.compile('^.*\\' + ('$|^.*\\'.join(extensions)) + '$', re.IGNORECASE)

    exclusions = ['Android/media/ga.asti.android']

    date_threshold = None
    try:
        with FTP() as ftp:
            ftp.connect(host=remote_host, port=port)
            ftp.login(user=username, passwd=password)
            print(ftp.getwelcome())

            date_threshold = remove_timestamp_file(local_directory)  # do this only when FTP connection was successful

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
                    print(f'Getting {file} from {d}/{n}...', end='')
                    if path.isfile(file):
                        print(f'{file} already exists')
                    else:
                        ftp.retrbinary('RETR ' + d + '/' + n, open(file, 'wb').write)
                        print(' Done.')

        date_threshold = datetime.now()

    except Exception as e:
        print(e)

    if date_threshold:
        threshold_file = path.join(local_directory, f"lastTimestamp_{date_threshold.strftime('%Y-%m-%d_%H-%M')}.txt")
        with open(threshold_file, 'w') as ts:
            ts.write(date_threshold.strftime('%Y-%m-%d %H:%M'))
        print(f'Created threshold file {threshold_file}.')


if __name__ == '__main__':
    extract(profile="philippe")
    # explore("philippe", '/')
    # extract("severine")
    # explore("severine", '/Pictures/Screenshots')
