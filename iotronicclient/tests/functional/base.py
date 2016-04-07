# Copyright (c) 2016 Mirantis, Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.

import os

import six.moves.configparser as config_parser
from tempest_lib.cli import base
from tempest_lib import exceptions

import iotronicclient.tests.functional.utils as utils

DEFAULT_CONFIG_FILE = os.path.join(os.path.dirname(__file__), 'test.conf')


class FunctionalTestBase(base.ClientTestBase):
    """Iotronic base class, calls to iotronicclient."""

    def setUp(self):
        super(FunctionalTestBase, self).setUp()
        self.client = self._get_clients()

    def _get_clients(self):
        # NOTE(aarefiev): {toxinidir} is a current working directory, so
        # the tox env path is {toxinidir}/.tox
        cli_dir = os.path.join(os.path.abspath('.'), '.tox/functional/bin')

        config = self._get_config()
        if config.get('os_auth_url'):
            client = base.CLIClient(cli_dir=cli_dir,
                                    username=config['os_username'],
                                    password=config['os_password'],
                                    tenant_name=config['os_tenant_name'],
                                    uri=config['os_auth_url'])
            for keystone_object in 'user', 'project':
                domain_attr = 'os_%s_domain_id' % keystone_object
                if config.get(domain_attr):
                    setattr(self, domain_attr, config[domain_attr])
        else:
            self.iotronic_url = config['iotronic_url']
            self.os_auth_token = config['os_auth_token']
            client = base.CLIClient(cli_dir=cli_dir,
                                    iotronic_url=self.iotronic_url,
                                    os_auth_token=self.os_auth_token)
        return client

    def _get_config(self):
        config_file = os.environ.get('IRONICCLIENT_TEST_CONFIG',
                                     DEFAULT_CONFIG_FILE)
        config = config_parser.SafeConfigParser()
        if not config.read(config_file):
            self.skipTest('Skipping, no test config found @ %s' % config_file)
        try:
            auth_strategy = config.get('functional', 'auth_strategy')
        except config_parser.NoOptionError:
            auth_strategy = 'keystone'
        if auth_strategy not in ['keystone', 'noauth']:
            raise self.fail(
                'Invalid auth type specified: %s in functional must be '
                'one of: [keystone, noauth]' % auth_strategy)

        conf_settings = []
        keystone_v3_conf_settings = []
        if auth_strategy == 'keystone':
            conf_settings += ['os_auth_url', 'os_username',
                              'os_password', 'os_tenant_name']
            keystone_v3_conf_settings += ['os_user_domain_id',
                                          'os_project_domain_id']
        else:
            conf_settings += ['os_auth_token', 'iotronic_url']

        cli_flags = {}
        missing = []
        for c in conf_settings + keystone_v3_conf_settings:
            try:
                cli_flags[c] = config.get('functional', c)
            except config_parser.NoOptionError:
                # NOTE(vdrok): Here we ignore the absence of KS v3 options as
                # v2 may be used. Keystone client will do the actual check of
                # the parameters' correctness.
                if c not in keystone_v3_conf_settings:
                    missing.append(c)
        if missing:
            self.fail('Missing required setting in test.conf (%(conf)s) for '
                      'auth_strategy=%(auth)s: %(missing)s' %
                      {'conf': config_file,
                       'auth': auth_strategy,
                       'missing': ','.join(missing)})
        return cli_flags

    def _cmd_no_auth(self, cmd, action, flags='', params=''):
        """Execute given command with noauth attributes.

        :param cmd: command to be executed
        :type cmd: string
        :param action: command on cli to run
        :type action: string
        :param flags: optional cli flags to use
        :type flags: string
        :param params: optional positional args to use
        :type params: string
        """
        flags = ('--os_auth_token %(token)s --iotronic_url %(url)s %(flags)s'
                 %
                 {'token': self.os_auth_token,
                  'url': self.iotronic_url,
                  'flags': flags})
        return base.execute(cmd, action, flags, params,
                            cli_dir=self.client.cli_dir)

    def _iotronic(self, action, flags='', params=''):
        """Execute iotronic command for the given action.

        :param action: the cli command to run using Iotronic
        :type action: string
        :param flags: any optional cli flags to use
        :type flags: string
        :param params: any optional positional args to use
        :type params: string
        """
        flags += ' --os-endpoint-type publicURL'
        try:
            if hasattr(self, 'os_auth_token'):
                return self._cmd_no_auth('iotronic', action, flags, params)
            else:
                for keystone_object in 'user', 'project':
                    domain_attr = 'os_%s_domain_id' % keystone_object
                    if hasattr(self, domain_attr):
                        flags += ' --os-%(ks_obj)s-domain-id %(value)s' % {
                            'ks_obj': keystone_object,
                            'value': getattr(self, domain_attr)
                        }
                return self.client.cmd_with_auth('iotronic',
                                                 action, flags, params)
        except exceptions.CommandFailed as e:
            self.fail(e)

    def iotronic(self, action, flags='', params=''):
        """Return parsed list of dicts with basic item info.

        :param action: the cli command to run using Iotronic
        :type action: string
        :param flags: any optional cli flags to use
        :type flags: string
        :param params: any optional positional args to use
        :type params: string
        """
        output = self._iotronic(action=action, flags=flags, params=params)
        return self.parser.listing(output)

    def get_table_headers(self, action, flags='', params=''):
        output = self._iotronic(action=action, flags=flags, params=params)
        table = self.parser.table(output)
        return table['headers']

    def assertTableHeaders(self, field_names, table_headers):
        """Assert that field_names and table_headers are equal.

        :param field_names: field names from the output table of the cmd
        :param table_heades: table headers output from cmd
        """
        self.assertEqual(sorted(field_names), sorted(table_headers))

    def assertNodeStates(self, node_show, node_show_states):
        """Assert that node_show_states output corresponds to node_show output.

        :param node_show: output from node-show cmd
        :param node_show_states: output from node-show-states cmd
        """
        for key in node_show_states.keys():
            self.assertEqual(node_show_states[key], node_show[key])

    def assertNodeValidate(self, node_validate):
        """Assert that node_validate is able to validate all interfaces present.

        :param node_validate: output from node-validate cmd
        """
        self.assertNotIn('False', [x['Result'] for x in node_validate])

    def delete_node(self, node_id):
        """Delete node method works only with fake driver.

        :param node_id: node uuid
        """
        node_list = self.list_nodes()

        if utils.get_object(node_list, node_id):
            node_show = self.show_node(node_id)
            if node_show['provision_state'] != 'available':
                self.iotronic('node-set-provision-state',
                            params='{0} deleted'.format(node_id))
            if node_show['power_state'] not in ('None', 'off'):
                self.iotronic('node-set-power-state',
                            params='{0} off'.format(node_id))
            self.iotronic('node-delete', params=node_id)

            node_list_uuid = self.get_nodes_uuids_from_node_list()
            if node_id in node_list_uuid:
                self.fail('Iotronic node {0} has not been deleted!'
                          .format(node_id))

    def create_node(self, driver='fake', params=''):
        node = self.iotronic('node-create',
                           params='--driver {0} {1}'.format(driver, params))

        if not node:
            self.fail('Iotronic node has not been created!')

        node = utils.get_dict_from_output(node)
        self.addCleanup(self.delete_node, node['uuid'])
        return node

    def show_node(self, node_id, params=''):
        node_show = self.iotronic('node-show',
                                params='{0} {1}'.format(node_id, params))
        return utils.get_dict_from_output(node_show)

    def list_nodes(self, params=''):
        return self.iotronic('node-list', params=params)

    def update_node(self, node_id, params):
        updated_node = self.iotronic('node-update',
                                   params='{0} {1}'.format(node_id, params))
        return utils.get_dict_from_output(updated_node)

    def get_nodes_uuids_from_node_list(self):
        node_list = self.list_nodes()
        return [x['UUID'] for x in node_list]

    def show_node_states(self, node_id):
        show_node_states = self.iotronic('node-show-states', params=node_id)
        return utils.get_dict_from_output(show_node_states)

    def set_node_maintenance(self, node_id, maintenance_mode, params=''):
        self.iotronic(
            'node-set-maintenance',
            params='{0} {1} {2}'.format(node_id, maintenance_mode, params))

    def set_node_power_state(self, node_id, power_state):
        self.iotronic('node-set-power-state',
                    params='{0} {1}'.format(node_id, power_state))

    def set_node_provision_state(self, node_id, provision_state, params=''):
        self.iotronic('node-set-provision-state',
                    params='{0} {1} {2}'
                    .format(node_id, provision_state, params))

    def validate_node(self, node_id):
        return self.iotronic('node-validate', params=node_id)

    def list_driver(self, params=''):
        return self.iotronic('driver-list', params=params)

    def show_driver(self, driver_name):
        driver_show = self.iotronic('driver-show', params=driver_name)
        return utils.get_dict_from_output(driver_show)

    def properties_driver(self, driver_name):
        return self.iotronic('driver-properties', params=driver_name)

    def get_drivers_names(self):
        driver_list = self.list_driver()
        return [x['Supported driver(s)'] for x in driver_list]

    def delete_chassis(self, chassis_id):
        chassis_list = self.list_chassis()

        if utils.get_object(chassis_list, chassis_id):
            self.iotronic('chassis-delete', params=chassis_id)

    def get_chassis_uuids_from_chassis_list(self):
        chassis_list = self.list_chassis()
        return [x['UUID'] for x in chassis_list]

    def create_chassis(self, params=''):
        chassis = self.iotronic('chassis-create', params=params)

        if not chassis:
            self.fail('Iotronic chassis has not been created!')

        chassis = utils.get_dict_from_output(chassis)
        self.addCleanup(self.delete_chassis, chassis['uuid'])
        return chassis

    def list_chassis(self, params=''):
        return self.iotronic('chassis-list', params=params)

    def show_chassis(self, chassis_id, params=''):
        chassis_show = self.iotronic('chassis-show',
                                   params='{0} {1}'.format(chassis_id, params))
        return utils.get_dict_from_output(chassis_show)

    def update_chassis(self, chassis_id, operation, params):
        updated_chassis = self.iotronic(
            'chassis-update',
            params='{0} {1} {2}'.format(chassis_id, operation, params))
        return utils.get_dict_from_output(updated_chassis)
