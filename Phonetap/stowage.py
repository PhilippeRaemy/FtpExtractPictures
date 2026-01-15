import os
import shutil
from datetime import datetime, timedelta
import re


def stow(command: str, source: str, target: str, dry_run: bool, force: bool, verbose: bool, offset_hours: int,
         suffix: str, filter: str, file_types: str, min_date: str, max_date: str):
    extensions = ['.' + e for e in file_types.split(',')]
    if filter:
        filter_re = re.compile(filter.replace('.', '\\.').replace('?', '.').replace('*', '.*'), re.IGNORECASE)
    re_timestamp = re.compile(
        r'^(?P<head>.*)(?P<yyyy>\d\d\d\d)-(?P<MM>\d\d)-(?P<dd>\d\d)_(?P<hh>\d\d)-(?P<mm>\d\d)(-(?P<ss>\d\d))?(?P<tail>.*)\.(?P<ext>.*)$')
    min_date = datetime.fromisoformat(min_date)
    max_date = datetime.fromisoformat(max_date)
    target_folders = {}

    def find_target(creation_day: datetime):
        creation_day = creation_day.date()
        if creation_day in target_folders:
            return target_folders[creation_day]

        target_root = os.path.join(target,
                                   creation_day.strftime("%Y"),
                                   creation_day.strftime("%Y%m"))
        leaf = creation_day.strftime("%Y%m%d")
        found_leaf = next(
            (d
             for _, dirs, _ in os.walk(target_root)
             for d in dirs
             if d == leaf or d.startswith(leaf + ' ')
             ), leaf
        )
        target_folder = os.path.join(target_root, found_leaf)
        target_folders[creation_day] = target_folder
        if not os.path.exists(target_folder):
            os.makedirs(target_folder, exist_ok=True)
            return target_folder

        for folder, _, files in os.walk(source):
            for file in files:
                if not any((file.endswith(e) for e in extensions)):
                    continue
                if filter and not filter_re.match(file):
                    continue
                path_to_file = os.path.join(folder, file)
                ma = re_timestamp.match(file)
                if ma:  # no need to rename
                    ma_di = ma.groupdict()
                    creation_time = datetime(
                        int(ma_di['yyyy']), int(ma_di['MM']), int(ma_di['dd']),
                        int(ma_di['hh']), int(ma_di['mm']), int(ma_di['ss']) if ma_di['ss'] else 0)
                    head = ma_di['head'].strip()
                    tail = ma_di['tail'].strip()
                else:
                    creation_time = os.path.getctime(path_to_file)
                    head = ''
                    chunks = file.strip().split('.')
                    tail = '.'.join(chunks[:-1])
                    ext = chunks[-1]
                if offset_hours:
                    creation_time += timedelta(hours=offset_hours)
                if not min_date <= creation_time <= max_date:
                    continue
                target_folder = find_target(creation_time)
                new_file = os.path.join(target_folder,
                                        f"{creation_time.strftime("%Y-%m-%d_%H_%m_%S")} {head}{tail}{suffix}.{ext}")
                if os.path.exists(new_file):
                    if force:
                        os.remove(new_file)
                    else:
                        continue
                if command == 'copy':
                    shutil.copy(path_to_file, new_file)
                else:
                    shutil.move(path_to_file, new_file)
