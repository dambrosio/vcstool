import argparse
from cgitb import reset
from distutils.util import execute
from gettext import find
from prettytable import PrettyTable
import sys
from unittest import result
from vcstool import clients
from vcstool.commands.branch import BranchCommand
from vcstool.crawler import find_repositories

from vcstool.executor import ansi, execute_jobs, generate_jobs, output_repositories
from vcstool.commands.import_ import get_repositories
from vcstool.streams import set_streams

from .command import add_common_arguments
from .command import Command


class CompareCommand(Command):

    command = 'compare'
    help = 'Compare working copy to the repository list file'

    def __init__(self, args):
        super(CompareCommand, self).__init__(args)


def get_parser():
    parser = argparse.ArgumentParser(
        description='Compare working copy to the repository list file',
        prog='vcs compare')
    group = parser.add_argument_group('"compare" command parameters')
    group.add_argument(
        '--input', type=argparse.FileType('r'), default='-')
    return parser


def main(args=None, stdout=None, stderr=None):
    set_streams(stdout=stdout, stderr=stderr)

    parser = get_parser()
    add_common_arguments(parser, skip_hide_empty=True,
                         skip_nested=True, skip_repos=True, path_nargs='?')
    args = parser.parse_args(args)

    # Get the repos from the repo file
    try:
        repos = get_repositories(args.input)
    except RuntimeError as e:
        print(ansi('redf') + str(e) + ansi('reset'), file=sys.stderr)
        return 1

    # Get clients from the client directory
    command = CompareCommand(args)
    clients = find_repositories(command.paths, nested=command.nested)
    jobs = generate_jobs(clients, command)
    result = execute_jobs(
        jobs, show_progress=True, number_of_workers=args.workers,
        debug_jobs=args.debug)

    table = PrettyTable()
    table.field_names = ['S', 'Repository', 'Client', 'Version']

    for key in repos:
        table.add_row(['x', key, repos[key]
                      ['type'], repos[key]['version']])

    for entry in result:
        # Strip the input path from the client path
        path = entry['cwd'].replace(f'{args.path}/', '')
        output = entry['output']
    table.sortby = 'Repository'
    print(table)

    return 0


if __name__ == '__main__':
    sys.exit(main())
