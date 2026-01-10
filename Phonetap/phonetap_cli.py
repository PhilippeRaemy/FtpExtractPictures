from functools import reduce
from importlib.metadata import requires

import click

from Phonetap import ftp_extract_pictures, profiles, pictures


@click.group()
@click.version_option()
def cli():
    """Handle pictures from phone via FTP"""


@cli.group()
def ftp():
    """FTP operations"""


@cli.group()
def profile():
    """profiles operations"""


@cli.group()
def picture():
    """pictures operations"""

# @cli.group()
# def stow():
#     """stow operations"""


def profile_option(f):
    options = [
        click.option('--profile', required=True),
        click.option('--username', required=False, default=None, type=str),
        click.option('--password', required=False, default=None, type=str),
        click.option('--host', required=False, default=None, type=str),
        click.option('--port', required=False, default=None, type=int),
        click.option('--local', required=False, default=None, type=str),
        click.option('--directories', required=False, default=[], type=str),
        click.option('--extensions', required=False, default=[], type=str),
        click.option('--add-directories', required=False, default=[], type=str),
        click.option('--remove-directories', required=False, default=[], type=str),
        click.option('--add-extensions', required=False, default=None, type=str),
        click.option('--remove-extensions', required=False, default=None, type=str)]

    return reduce(lambda lf, opt: opt(lf), options, f)

    # directories = []
    # extensions = []
    # add_directories = []
    # remove_directories = []
    # add_extensions = []
    # remove_extensions = []


@profile.command('edit')
@profile_option
@click.option('--model', required=False, default='default', type=str)
def edit_profile(profile, username, password, host, port, local,
                 directories, extensions,
                 add_directories, remove_directories,
                 add_extensions, remove_extensions, model):
    profiles.edit(profile, username, password, host, port, local,
                  directories, extensions,
                  add_directories, remove_directories,
                  add_extensions, remove_extensions, model)


@profile.command('list')
def list_profiles():
    profiles.list_profiles()


@profile.command('show')
@click.option('--profile', default='')
def show_profile(profile=None):
    profiles.show(profile)


@ftp.command("explore")
@profile_option
def explore(profile: str, directory: str, username, password, host, port, local,
            extensions,
            add_extensions, remove_extensions):
    ftp_extract_pictures.explore(profile, directory, username, password, host, port, local,
                                 extensions,
                                 add_extensions, remove_extensions)


@ftp.command('extract')
@profile_option
def extract(profile, username, password, host, port, local,
            directories, extensions,
            add_directories, remove_directories,
            add_extensions, remove_extensions):
    ftp_extract_pictures.extract(profile, username, password, host, port, local,
                                 directories, extensions,
                                 add_directories, remove_directories,
                                 add_extensions, remove_extensions)


@picture.command('compare')
@click.option('--first', required=True, help='The first picture to compare')
@click.option('--second', required=True, help='The second picture to compare')
@click.option('--show', required=False, is_flag=True, help='Open the pictures in system pictures viewer')
def pictures_compare(**kwargs):
    pictures.compare(**kwargs)


@picture.command('deduplicate')
@click.option('--folder', required=True, help='The root folder')
@click.option('--hash-size', required=False, type=int, default=64,
              help='the hash size. The number of comparison points is the square of the hash size')
@click.option('--dry-run', required=False, is_flag=True, help='Only show similarities')
@click.option('--verbose', required=False, is_flag=True, help='verbose progress display')
@click.option('--show', required=False, is_flag=True, help='Open the pictures in system pictures viewer')
def pictures_deduplicate(**kwargs):
    pictures.deduplicate(**kwargs)


@cli.command('stow')
@click.option('--folder', required=True, help='The root folder')
@click.option('--dry-run', required=False, is_flag=True, help='Only show work at hand')
@click.option('--verbose', required=False, is_flag=True, help='verbose progress display')
@click.option('--time-offset', required=False, type=int, default=0, help='Set time offset in hours')
@click.option('--suffix', required=False, type=str, default='', help='Set optional picture name suffix')
def stow_pictures(**kwargs):
    pass


if __name__ == '__main__':
    print('in main')
    cli()
