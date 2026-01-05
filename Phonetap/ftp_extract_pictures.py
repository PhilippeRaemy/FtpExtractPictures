import re
from datetime import datetime
from ftplib import FTP
from os import listdir, path, remove

from Phonetap.profiles import explode_profile


def explore(profile: str, directory: str, username, password, host, port, local,
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


def extract(profile, username, password, host, port, local,
            directories, extensions,
            add_directories, remove_directories,
            add_extensions, remove_extensions):
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
    explore()
    # _extract(profile="philippe")
    # explore("philippe", '/')
    # extract("severine")
    # explore("severine", '/Pictures/Screenshots')
