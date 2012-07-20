import argparse
import os
import sys

from clint.textui import puts, colored

from photostash import __version__
from photostash.runner import Runner
from photostash.exceptions import CommandError


def main(argv=sys.argv, runner_class=Runner):
    parser = argparse.ArgumentParser(prog='stash')
    parser.add_argument(
        '--version',
        action='version',
        version='%%(prog)s %s' % __version__,
    )

    commands = {}

    command_parsers = parser.add_subparsers(dest='command')

    commands['create'] = command_parsers.add_parser('create')
    commands['create'].add_argument('album_name')

    commands['list'] = command_parsers.add_parser('list')
    commands['list'].add_argument('album_name')

    commands['delete'] = command_parsers.add_parser('delete')
    commands['delete'].add_argument('album_name')
    commands['delete'].add_argument('photo_id')

    commands['add'] = command_parsers.add_parser('add')
    commands['add'].add_argument('album_name')
    commands['add'].add_argument('photo_path')

    commands['open'] = command_parsers.add_parser('open')
    commands['open'].add_argument('photo_id')

    commands['stats'] = command_parsers.add_parser('stats')

    commend = parser.parse_args(argv[1:]).command

    subargs = commands[commend].parse_args(argv[2:])

    runner = runner_class(base_url=os.environ.get('STASH_API_URL', None))

    try:
        getattr(runner, commend)(**dict(subargs._get_kwargs()))
    except CommandError as e:
        puts(colored.red('%s' % e.message), stream=sys.stderr.write)
        sys.exit(1)
