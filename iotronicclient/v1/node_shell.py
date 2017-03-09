# Copyright 2013 Red Hat, Inc.
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import argparse
import six

from iotronicclient.common.apiclient import exceptions
from iotronicclient.common import cliutils
from iotronicclient.common.i18n import _
from iotronicclient.common import utils
from iotronicclient import exc
from iotronicclient.v1 import resource_fields as res_fields
from iotronicclient.v1 import utils as v1_utils


def _print_node_show(node, fields=None, json=False):
    if fields is None:
        fields = res_fields.NODE_DETAILED_RESOURCE.fields

    data = dict(
        [(f, getattr(node, f, '')) for f in fields])
    cliutils.print_dict(data, wrap=72, json_flag=json)


@cliutils.arg(
    'node',
    metavar='<id>',
    help="Name or UUID of the node ")
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more node fields. Only these fields will be fetched from "
         "the server.")
def do_node_show(cc, args):
    """Show detailed information about a node."""
    fields = args.fields[0] if args.fields else None
    utils.check_empty_arg(args.node, '<id>')
    utils.check_for_invalid_fields(
        fields, res_fields.NODE_DETAILED_RESOURCE.fields)
    node = cc.node.get(args.node, fields=fields)
    _print_node_show(node, fields=fields, json=args.json)


@cliutils.arg(
    '--limit',
    metavar='<limit>',
    type=int,
    help='Maximum number of nodes to return per request, '
         '0 for no limit. Default is the maximum number used '
         'by the Iotronic API Service.')
@cliutils.arg(
    '--marker',
    metavar='<node>',
    help='Node UUID (for example, of the last node in the list from '
         'a previous request). Returns the list of nodes after this UUID.')
@cliutils.arg(
    '--sort-key',
    metavar='<field>',
    help='Node field that will be used for sorting.')
@cliutils.arg(
    '--sort-dir',
    metavar='<direction>',
    choices=['asc', 'desc'],
    help='Sort direction: "asc" (the default) or "desc".')
@cliutils.arg(
    '--project',
    metavar='<project>',
    help="Project of the list.")
@cliutils.arg(
    '--detail',
    dest='detail',
    action='store_true',
    default=False,
    help="Show detailed information about the nodes.")
@cliutils.arg(
    '--fields',
    nargs='+',
    dest='fields',
    metavar='<field>',
    action='append',
    default=[],
    help="One or more node fields. Only these fields will be fetched from "
         "the server. Can not be used when '--detail' is specified.")
def do_node_list(cc, args):
    """List the nodes which are registered with the Iotronic service."""
    params = {}

    if args.project is not None:
        params['project'] = args.project

    if args.detail:
        fields = res_fields.NODE_DETAILED_RESOURCE.fields
        field_labels = res_fields.NODE_DETAILED_RESOURCE.labels
    elif args.fields:
        utils.check_for_invalid_fields(
            args.fields[0], res_fields.NODE_DETAILED_RESOURCE.fields)
        resource = res_fields.Resource(args.fields[0])
        fields = resource.fields
        field_labels = resource.labels
    else:
        fields = res_fields.NODE_RESOURCE.fields
        field_labels = res_fields.NODE_RESOURCE.labels

    sort_fields = res_fields.NODE_DETAILED_RESOURCE.sort_fields
    sort_field_labels = res_fields.NODE_DETAILED_RESOURCE.sort_labels

    params.update(utils.common_params_for_list(args,
                                               sort_fields,
                                               sort_field_labels))
    nodes = cc.node.list(**params)
    cliutils.print_list(nodes, fields,
                        field_labels=field_labels,
                        sortby_index=None,
                        json_flag=args.json)

@cliutils.arg(
    'name',
    metavar='<name>',
    help="Name or UUID of the node ")
@cliutils.arg(
    'code',
    metavar='<code>',
    help="Codeof the node ")
@cliutils.arg(
    'type',
    metavar='<type>',
    help="Type of the node ")
@cliutils.arg(
    'latitude',
    metavar='<latitude>',
    help="Latitude of the node ")
@cliutils.arg(
    'longitude',
    metavar='<longitude>',
    help="Longitude of the node ")
@cliutils.arg(
    'altitude',
    metavar='<altitude>',
    help="Altitude of the node ")
@cliutils.arg(
    '-m','--mobile',
    dest='mobile',
    action='store_true',
    default=False,
    help="Set a mobile node")
@cliutils.arg(
    '-e', '--extra',
    metavar='<key=value>',
    action='append',
    help="Record arbitrary key/value metadata. "
         "Can be specified multiple times.")

def do_node_create(cc, args):
    """Register a new node with the Iotronic service."""
    field_list = ['name','code','type','mobile','extra']

    fields = dict((k, v) for (k, v) in vars(args).items()
                  if k in field_list and not (v is None))
    fields = utils.args_array_to_dict(fields, 'extra')

    fields['location']=[{'latitude':args.latitude,'longitude':args.longitude,'altitude':args.altitude}]

    node = cc.node.create(**fields)

    data = dict([(f, getattr(node, f, '')) for f in field_list])
    cliutils.print_dict(data, wrap=72, json_flag=args.json)


@cliutils.arg('node',
              metavar='<node>',
              nargs='+',
              help="Name or UUID of the node.")
def do_node_delete(cc, args):
    """Unregister node(s) from the Iotronic service.

    Returns errors for any nodes that could not be unregistered.
    """

    failures = []
    for n in args.node:
        try:
            cc.node.delete(n)
            print(_('Deleted node %s') % n)
        except exceptions.ClientException as e:
            failures.append(_("Failed to delete node %(node)s: %(error)s")
                            % {'node': n, 'error': e})
    if failures:
        raise exceptions.ClientException("\n".join(failures))


@cliutils.arg('node', metavar='<node>', help="Name or UUID of the node.")
@cliutils.arg(
    'op',
    metavar='<op>',
    choices=['add', 'replace', 'remove'],
    help="Operation: 'add', 'replace', or 'remove'.")
@cliutils.arg(
    'attributes',
    metavar='<path=value>',
    nargs='+',
    action='append',
    default=[],
    help="Attribute to add, replace, or remove. Can be specified "
         "multiple times. For 'remove', only <path> is necessary. "
         "For nested attributes, separate the components with slashes, eg "
         "'driver_info/deploy_kernel=uuid'.")
def do_node_update(cc, args):
    """Update information about a registered node."""
    patch = utils.args_array_to_patch(args.op, args.attributes[0])
    node = cc.node.update(args.node, patch)
    _print_node_show(node, json=args.json)

