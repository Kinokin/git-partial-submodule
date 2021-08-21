#!/usr/bin/python3
#coding: utf-8

import argparse, codecs, configparser, os, re, subprocess, sys

# Parse arguments

parser = argparse.ArgumentParser(description="Add or clone partial git submodules.")
parser.add_argument('-n', dest='dryRun', default=False, action='store_true', help='Dry run (display git commands without executing them)')
parser.add_argument('-v', dest='verbose', default=False, action='store_true', help='Verbose (display git commands being run)')
subparsers = parser.add_subparsers(dest='command', metavar='command')

addCmdParser = subparsers.add_parser(
    'add',
    allow_abbrev = False,
    help = "Add a new partial submodule.",
    epilog = "All other options are passed through to the underlying git command.")
addCmdParser.add_argument('-b', dest='branch', help='Branch in the submodule repository to check out')
addCmdParser.add_argument('--name', dest='name', help='Logical name for the submodule')
addCmdParser.add_argument('repository', help='URL to the git repository to be added as a submodule')
addCmdParser.add_argument('path', help='Directory where the submodule will be checked out')

cloneCmdParser = subparsers.add_parser(
    'clone',
    allow_abbrev = False,
    help = "Clone partial submodules from .gitmodules.",
    epilog = "All other options are passed through to the underlying git command.")
cloneCmdParser.add_argument('path', nargs='*', default=[], help='Submodule directory to clone (if unspecified, all submodules)')

args, extraArgs = parser.parse_known_args()
#print("Args:\n", args, "\nextraArgs:\n", extraArgs)

if args.command is None:
    parser.print_help()
    sys.exit()

# Helper functions

def Git(*gitArgs, **kwargs):
    if args.verbose:
        print('git ' + ' '.join(gitArgs))
    if args.dryRun:
        return
    cp = subprocess.run(('git',) + gitArgs, **kwargs)
    if cp.returncode != 0:
        sys.exit("Git command failed: git %s" % ' '.join(gitArgs))
    return cp

def CheckGitVersion(minVersion):
    cp = subprocess.run(('git', '--version'), capture_output=True)
    if cp.returncode != 0: sys.exit(1)
    if m := re.match(br'git version (\d+)\.(\d+)\.(\d+)', cp.stdout):
        gitVersion = tuple(int(m.group(i)) for i in range(1, 4))
    if gitVersion < minVersion:
        sys.exit("Git version is too old. You need at least %d.%d.%d, and you have %d.%d.%d." % (minVersion + gitVersion))

def GetWorktreeRoot():
    cp = subprocess.run(('git', 'rev-parse', '--show-toplevel'), capture_output=True)
    if cp.returncode != 0: sys.exit(1)
    return os.path.abspath(codecs.decode(cp.stdout, sys.stdout.encoding).strip())

def GetRepositoryRoot():
    cp = subprocess.run(('git', 'rev-parse', '--git-dir'), capture_output=True)
    if cp.returncode != 0: sys.exit(1)
    return os.path.abspath(codecs.decode(cp.stdout, sys.stdout.encoding).strip())

# Version 2.27.0 is needed for --filter and --sparse options on git clone
CheckGitVersion((2, 27, 0))

# Locate directories
worktreeRoot = GetWorktreeRoot()
repoRoot = GetRepositoryRoot()
if args.verbose:
    print("worktree root: %s\nrepo root: %s" % (worktreeRoot, repoRoot))

# Process commands

if args.dryRun:
    args.verbose = True
    print("DRY RUN:")

if args.command == 'add':
    # TODO: do underlying git submodule add without cloning?
    # TODO: clone as partial, setup worktree
    sys.exit("Not yet implemented")

elif args.command == 'clone':
    # Read .gitmodules
    gitmodules = configparser.ConfigParser(
        allow_no_value = True,
        default_section = None,
        inline_comment_prefixes = ('#', ';'),
        interpolation = None)
    if not gitmodules.read(os.path.join(worktreeRoot, '.gitmodules')):
        sys.exit("Couldn't parse .gitmodules!")
    if args.verbose:
        print("parsed %d submodules from .gitmodules" % len(gitmodules.sections()))

    # TODO: build mapping tables from gitmodules

    # Init the submodules - this ensures git config "submodule.foo" options are set up
    Git('submodule', 'init', *args.path)

    # TODO: loop over paths and clone as partial if not already cloned,
    # setup worktree as sparse if not already
    sys.exit("Not yet implemented")
