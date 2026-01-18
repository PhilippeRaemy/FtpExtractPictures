from functools import reduce
from importlib.metadata import requires

import click

from Phonetap import ftp_extract_pictures, profiles, pictures, stowage


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


@cli.group()
def stow():
    """stow operations"""


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
@click.option('--folder', '-f', required=True, help='The root folder')
@click.option('--file-types', '-y', required=False, type=str, default='jpg,jpeg,cr2,webp',
              help='File extensions of interest, comma-delimited, no wildcards')
@click.option('--algorithm', '-a', required=False, default='dhash', type=click.Choice(['average', 'dhash']),
              help='The hash algorithm used')
@click.option('--hash-size', '-z', required=False, type=int, default=64,
              help='the hash size. The number of comparison points is the square of the hash size')
@click.option('--similarity', '-s', required=False, default=95, help='Similarity percentage')
@click.option('--dry-run', '-n', required=False, is_flag=True, help='Only show similarities')
@click.option('--verbose', '-v', required=False, is_flag=True, help='verbose progress display')
@click.option('--show', '-w', required=False, is_flag=True, help='Open the pictures in system pictures viewer')
def pictures_deduplicate(**kwargs):
    pictures.deduplicate(**kwargs)


def stow_options(f):
    options = [
        click.option('--source', '-s', required=False, default=".", help='The source folder'),
        click.option('--target', '-t', required=False, default=".", help='The root target folder'),
        click.option('--dry-run', '-n', required=False, is_flag=True, help='Only show work at hand'),
        click.option('--force', '-f', required=False, is_flag=True, help='Force copy or move onto existing file'),
        click.option('--verbose', '-v', required=False, is_flag=True, help='verbose progress display'),
        click.option('--offset-hours', '-o', required=False, type=int, default=0, help='Set time offset in hours'),
        click.option('--suffix', '-x', required=False, type=str, default='', help='Set optional picture name suffix'),
        click.option('--filter', '-l', required=False, type=str, default='', help='Filter files with os-wildcards'),
        click.option('--file-types', '-y', required=False, type=str, default='jpg,jpeg,mov,mp3,mp4,cr2,webp,avi,wav',
                     help='File extensions of interest, comma-delimited, no wildcards'),
        click.option('--min-date', '-max', required=False, type=str, default='1900-01-01', help='Minimum file date'),
        click.option('--max-date', '-min', required=False, type=str, default='2500-01-01', help='Maximum file date'),

    ]
    return reduce(lambda lf, opt: opt(lf), options, f)


@stow.command('copy')
@stow_options
def stow_pictures(**kwargs):
    """
This function imports pictures and other acceptable files from the
current working folder (usually a memory card), or a designated source folder,
and imports them in a local folder.\n
On the way, the filenames are timestamped, i.e. the date and time of
creation of the file are used to prefix the file name, in an ISO format.
Additionally, the files are arranged under the chosen target folder
in a directory tree similar to\n
    ../yyyy/yyyymm/yyyymmdd\n
If such a directory does not exist, it is created.
If such a directory does exist, or a similar directory with a name or
a description suffix after the day date, this directory is used.
    """
    stowage.stow('copy', **kwargs)


@stow.command('move')
@stow_options
def stow_pictures(**kwargs):
    """
This function imports pictures and other acceptable files from the
current working folder (usually a memory card), or a designated source folder,
and imports them in a local folder.\n
With this command the imported files are deleted from the source location.\n
On the way, the filenames are timestamped, i.e. the date and time of
creation of the file are used to prefix the file name, in an ISO format.
Additionally, the files are arranged under the chosen target folder
in a directory tree similar to\n
    ../yyyy/yyyymm/yyyymmdd\n
If such a directory does not exist, it is created.
If such a directory does exist, or a similar directory with a name or
a description suffix after the day date, this directory is used.
    """
    stowage.stow('move', **kwargs)


if __name__ == '__main__':
    print('in main')
    cli()
