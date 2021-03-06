# -*- coding: utf-8 -*-
"""
Test for ssh_pre_flight roster option
"""
from __future__ import absolute_import, print_function, unicode_literals

import os

import salt.utils.files
from tests.support.case import SSHCase
from tests.support.helpers import slowTest
from tests.support.runtests import RUNTIME_VARS


class SSHPreFlightTest(SSHCase):
    """
    Test ssh_pre_flight roster option
    """

    def setUp(self):
        super(SSHPreFlightTest, self).setUp()
        self.roster = os.path.join(RUNTIME_VARS.TMP, "pre_flight_roster")
        self.data = {
            "ssh_pre_flight": os.path.join(RUNTIME_VARS.TMP, "ssh_pre_flight.sh")
        }
        self.test_script = os.path.join(
            RUNTIME_VARS.TMP, "test-pre-flight-script-worked.txt"
        )

    def _create_roster(self):
        self.custom_roster(self.roster, self.data)

        with salt.utils.files.fopen(self.data["ssh_pre_flight"], "w") as fp_:
            fp_.write("touch {0}".format(self.test_script))

    @slowTest
    def test_ssh_pre_flight(self):
        """
        test ssh when ssh_pre_flight is set
        ensure the script runs successfully
        """
        self._create_roster()
        ret = self.run_function("test.ping", roster_file=self.roster)

        assert os.path.exists(self.test_script)

    @slowTest
    def test_ssh_run_pre_flight(self):
        """
        test ssh when --pre-flight is passed to salt-ssh
        to ensure the script runs successfully
        """
        self._create_roster()
        # make sure we previously ran a command so the thin dir exists
        self.run_function("test.ping", wipe=False)
        assert not os.path.exists(self.test_script)

        ret = self.run_function(
            "test.ping", ssh_opts="--pre-flight", roster_file=self.roster, wipe=False
        )
        assert os.path.exists(self.test_script)

    def tearDown(self):
        """
        make sure to clean up any old ssh directories
        """
        files = [self.roster, self.data["ssh_pre_flight"], self.test_script]
        for fp_ in files:
            if os.path.exists(fp_):
                os.remove(fp_)
