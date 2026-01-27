import json
import os

profile_fields = (
    'username',
    'password',
    'local',
    'host',
    'port',
    'directories',
    'extensions')


def _explode_profile(**kwargs):
    print('explode profile')
    profile_file = kwargs['profile_file']
    profile_name = kwargs['profile']

    if os.path.exists(profile_file):
        with open(profile_file) as j:
            profiles = json.loads(j.read())
    else:
        profiles = {}

    saved_profile = profiles.get(profile_name, {})
    profile = {fi: kwargs.get(fi) or saved_profile.get(fi) for fi in profile_fields}
    # TODO: on creation, check that all the fields are present
    profile['profile'] = profile_name
    profile['profile_file'] = profile_file
    add_directories = kwargs['add_directories']
    remove_directories = kwargs['remove_directories']
    if not kwargs['directories']:
        profile['directories'] = list(
            set(profile['directories'])
            .union(add_directories if add_directories else [])
            .difference(remove_directories if remove_directories else []))
    add_extensions = kwargs['add_extensions']
    remove_extensions = kwargs['remove_extensions']
    if not kwargs['extensions']:
        profile['extensions'] = list(
            set(profile['extensions'])
            .union(add_extensions if add_extensions else [])
            .difference(remove_extensions if remove_extensions else []))
    print(json.dumps(profile, indent=4))
    return profile


def explode_profile(**kwargs):
    profile = _explode_profile(**kwargs)
    return (profile[fi] for fi in profile_fields)


def edit(**kwargs):
    profile = _explode_profile(**kwargs)
    profile_file = profile['profile_file']
    with open(profile_file, 'r') as j:
        profiles = json.loads(j.read())
    profiles[profile['profile']] = profile
    with open(profile_file, 'w') as j:
        dumps = json.dumps(profiles, indent=2)
        j.write(dumps)


def list_profiles(profile_file):
    with open(profile_file, 'r') as j:
        profiles = json.loads(j.read())
    print(f'Available profiles are :{profiles.keys()}')


def show(profile_file, profile=None):
    with open(profile_file, 'r') as j:
        profiles = json.loads(j.read())
    if profile:
        print(json.dumps(profiles[profile], indent=2))
    else:
        # list_profiles()
        print(f'Available profiles are :{profiles.keys()}')
