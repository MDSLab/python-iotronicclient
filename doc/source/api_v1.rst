.. _api_v1:

=======================
iotronicclient Python API
=======================

The iotronicclient python API lets you access iotronic, the OpenStack
Bare Metal Provisioning Service.

For example, to manipulate nodes, you interact with an
`iotronicclient.v1.node`_ object.
You obtain access to nodes via attributes of the
`iotronicclient.v1.client.Client`_ object.

Usage
=====

Get a Client object
-------------------
First, create an `iotronicclient.v1.client.Client`_ instance by passing your
credentials to `iotronicclient.client.get_client()`_. By default, the
Bare Metal Provisioning system is configured so that only administrators
(users with 'admin' role) have access.

There are two different sets of credentials that can be used::

   * iotronic endpoint and auth token
   * Identity Service (keystone) credentials

Using iotronic endpoint and auth token
.....................................

An auth token and the iotronic endpoint can be used to authenticate::

      * os_auth_token: authentication token (from Identity Service)
      * iotronic_url: iotronic API endpoint, eg http://iotronic.example.org:6385/v1

To create the client, you can use the API like so::

   >>> from iotronicclient import client
   >>>
   >>> kwargs = {'os_auth_token': '3bcc3d3a03f44e3d8377f9247b0ad155'
   >>>           'iotronic_url': 'http://iotronic.example.org:6385/'}
   >>> iotronic = client.get_client(1, **kwargs)

Using Identity Service (keystone) credentials
.............................................

These Identity Service credentials can be used to authenticate::

   * os_username: name of user
   * os_password: user's password
   * os_auth_url: Identity Service endpoint for authorization
   * insecure: Boolean. If True, does not perform X.509 certificate
     validation when establishing SSL connection with identity
     service. default: False (optional)
   * os_tenant_{name|id}: name or ID of tenant

To create a client, you can use the API like so::

   >>> from iotronicclient import client
   >>>
   >>> kwargs = {'os_username': 'name',
   >>>           'os_password': 'password',
   >>>           'os_auth_url': 'http://keystone.example.org:5000/',
   >>>           'os_tenant_name': 'tenant'}
   >>> iotronic = client.get_client(1, **kwargs)

Perform iotronic operations
-------------------------

Once you have an iotronic `Client`_, you can perform various tasks::

   >>> iotronic.driver.list()  # list of drivers
   >>> iotronic.node.list()  # list of nodes
   >>> iotronic.node.get(node_uuid)  # information about a particular node

When the `Client`_ needs to propagate an exception, it will usually
raise an instance subclassed from
`iotronicclient.exc.BaseException`_ or `iotronicclient.exc.ClientException`_.

Refer to the modules themselves, for more details.

iotronicclient Modules
====================

.. toctree::
    :maxdepth: 1

    modules <api/autoindex>


.. _iotronicclient.v1.node: api/iotronicclient.v1.node.html#iotronicclient.v1.node.Node
.. _iotronicclient.v1.client.Client: api/iotronicclient.v1.client.html#iotronicclient.v1.client.Client
.. _Client: api/iotronicclient.v1.client.html#iotronicclient.v1.client.Client
.. _iotronicclient.client.get_client(): api/iotronicclient.client.html#iotronicclient.client.get_client
.. _iotronicclient.exc.BaseException: api/iotronicclient.exc.html#iotronicclient.exc.BaseException
.. _iotronicclient.exc.ClientException: api/iotronicclient.exc.html#iotronicclient.exc.ClientException
