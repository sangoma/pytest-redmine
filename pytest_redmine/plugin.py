# -*- coding: utf-8 -*-
# vim:ts=4:sw=4:softtabstop=4:smarttab:expandtab
#
# Copyright (C) 2014  Sangoma Technologies Corp.
# All Rights Reserved.
# Author(s)
# Tyler Goodlet <tgoodlet@sangoma.com>
# Simon Gomizelj <sgomizelj@sangoma.com>

import py
import sys
import pytest
import redminelib
from _pytest.runner import Skipped
if sys.version_info >= (3, 0):
    from configparser import ConfigParser, NoOptionError, NoSectionError
else:
    from ConfigParser import ConfigParser, NoOptionError, NoSectionError


class PytestRedmineError(Exception):
    pass


class AssociatedIssue(Skipped):
    def __init__(self, issue):
        issue_title = str(issue).strip()
        if issue_title[-1] == '.':
           issue_title = issue_title[:-1]

        msg = '{} Redmine #{}: {}'.format(issue.status.name, issue.id,
                                          issue_title)

        Skipped.__init__(self, msg)
        self.issue = issue


def connect_to_redmine():
    '''Try to establish an authenticated connection to the redmine database.

    Searches for login credentials in the redmine.ini configuration
    file. First it tries using an API key and then falls back to
    username/password
    '''

    cfg = ConfigParser()
    cfg.read(py.path.local('redmine.ini').strpath)

    try:
        baseurl = cfg.get('redmine', 'baseurl')
        return redminelib.Redmine(baseurl, key=cfg.get('redmine', 'apikey'))
    except NoSectionError:
        raise PytestRedmineError("No [redmine] section found in redmine.ini")
    except NoOptionError:
        try:
            return redminelib.Redmine(baseurl,
                                      username=cfg.get('redmine', 'username'),
                                      password=cfg.get('redmine', 'password'))
        except NoOptionError:
            raise PytestRedmineError("Not configured with either an api key "
                                     "or login credentials")


def pytest_namespace():
    return {'redmine': None}


def pytest_configure(config):
    # register addtional markers
    config.addinivalue_line(
        "markers",
        "redmine(issueids, ...): mark to run test only if there is no pending "
        "redmine issues for id, otherwise skip"
    )


@pytest.hookimpl(tryfirst=True)
def pytest_runtest_setup(item):
    marker = item.get_marker('redmine')
    if not marker:
        return

    if not pytest.redmine:
        pytest.redmine = connect_to_redmine()

    for issueno in marker.args:
        issue = pytest.redmine.issue.get(issueno)
        if issue.status.name not in ('Resolved', 'Closed'):
            raise AssociatedIssue(issue)


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    rep = outcome.get_result()
    if call.excinfo and call.excinfo.errisinstance(AssociatedIssue):
        path, lineno, _ = item.reportinfo()
        rep.issue = call.excinfo.value.issue
        rep.longrepr = path, lineno, str(call.excinfo.value)


def pytest_report_teststatus(report):
    issue = getattr(report, 'issue', None)
    if issue:
        msg = '{} REDMINE'.format(issue.status.name.upper())
        return 'skipped', '🐛', (msg, {'yellow': True})
