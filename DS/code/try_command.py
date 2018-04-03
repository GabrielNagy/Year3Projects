#!/usr/bin/env python
import argparse
import os
import subprocess
import sys
import keypress
from argparse import RawTextHelpFormatter

configuration = {
    "repo_addr": "https://github.com/buildbot/hello-world.git",
    "repo_type": "git",
    "try_scheduler_address": "localhost:8031",
    "username": "change",
    "password": "changepw"
}


def compose_patch_cmd(who, repo_type, scheduler, login, password, project_repo, branch,
                      builders, comments, patch, filelist):
    change_cmd = "buildbot try "
    change_cmd += '--who="%s" ' % who
    change_cmd += "--connect=pb "
    change_cmd += "--vc=%s " % repo_type
    change_cmd += "--topdir=. "
    change_cmd += "--master=%s " % scheduler
    change_cmd += '--username="%s" ' % login
    change_cmd += '--passwd="%s" ' % password
    change_cmd += "--repository=%s " % project_repo
    change_cmd += "--branch=%s " % branch
    change_cmd += "--project=test_proj "
    if patch:
        assert(os.path.exists(patch))
        change_cmd += "--diff=%s " % patch
    if builders:
        for builder in builders:
            change_cmd += "--builder='%s' " % builder
    change_cmd += '--comment="%s" ' % comments
    change_cmd += '--property=author=%s ' % who
    change_cmd += '--property=comment="%s" ' % comments
    change_cmd += '--property=filelist="%s" ' % filelist

    return change_cmd


class TriggerBuildbotFailed(Exception):
    pass


def clean_workspace():
    subprocess.check_call("rm patch*", shell=True)


def trigger_buildbot(who, configuration, branch, comments="", patch=None, builders=[], filelist=None, dryrun=False, verbose=False):
    if patch:
        command = compose_patch_cmd(who,
                                    configuration["repo_type"],
                                    configuration["try_scheduler_address"],
                                    configuration["username"],
                                    configuration["password"],
                                    configuration["repo_addr"],
                                    branch,
                                    builders,
                                    comments,
                                    patch,
                                    filelist)

    if verbose:
        print('\n' + command)

    if not dryrun:
        subprocess.check_call(command, shell=True)


if __name__ == "__main__":

    default_patch = 'patch.txt'
    default_branch = subprocess.check_output(['git', 'rev-parse', '--abbrev-ref', 'HEAD'])
    diff_command = "git diff > patch.txt"

    parser = argparse.ArgumentParser(description='Script for triggering '
                                     'buildbot try build',
                                     formatter_class=RawTextHelpFormatter)

    parser.add_argument('-n', '--dry-run', dest='dryrun', action='store_true', required=False,
                        default=False, help="don't trigger anything; exit after printing command")
    parser.add_argument('-v', '--verbose', dest='verbose', action='store_true', required=False,
                        default=False, help="increase verbosity")
    parser.add_argument('-a', '--author', dest='author', type=str, required=False,
                        default=os.getenv('USER', 'ninja_trigger'), help="any author string")
    parser.add_argument('-c', '--comment', dest='comment', type=str, required=False,
                        default="try job for " + os.getenv('USER'), help="any comment string")
    parser.add_argument('-B', '--builder', dest='builder', type=str, required=False,
                        action='append',
                        default=None, help="builder name, can be specified multiple times, e.g.\n"
                        '  -B runtests0 -B slowruntests\n'
                        "If no builder is specified all builders are triggered.")
    parser.add_argument('-p', '--patch', dest='patchfile', type=str, required=False,
                        default=default_patch, help="generated patch file (if applicable), e.g.\n"
                        "  git diff > patchfile.txt\n"
                        "If no patch is specified, git diff will be run automatically.")
    parser.add_argument('-b', '--branch', dest='branch', type=str, required=False,
                        default=default_branch, help="branch name, e.g.\n"
                        "  master\n"
                        )
    args = parser.parse_args()

    subprocess.call(diff_command, shell=True)
    if os.stat(args.patchfile).st_size == 0:
        print("Generated patch file is empty. Did you modify anything?")
        clean_workspace()
        sys.exit(1)

    patch_files = subprocess.check_output(['git', 'diff', '--stat'])
    while True:
        print("\nBuildbot try script triggered. Patch file saved to patch.txt.")
        print("\nFiles to be modified:\n" + patch_files)
        print("Press (r)un to send patch, (d)iff to view patch contents or e(x)it to stop.")
        letter = keypress.read_single_keypress()
        if letter == 'x':
            clean_workspace()
            sys.exit(1)
        if letter == 'd':
            print("\n\n*** PATCH CONTENTS ***\n")
            subprocess.call(['git', 'diff'])
            print("\n\n**************************\n")
        if letter == 'r':
            print("   sending...")
            break

    try:
        trigger_buildbot(args.author,
                         configuration,
                         args.branch,
                         patch=args.patchfile,
                         builders=args.builder,
                         filelist=patch_files,
                         comments=args.comment,
                         dryrun=args.dryrun,
                         verbose=args.verbose,)
    except TriggerBuildbotFailed as e:
        print(e)

    print("""
Patch sent to buildbot. Your build has not started yet. Go here:
        %s
and check the top of the page for your build status.
    """ % "http://tm171lin212.wls.ro.alcatel-lucent.com:8020/#/inctdashboard")
    clean_workspace()
