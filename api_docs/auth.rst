.. _ref-auth:

================================
Authentication and Authorization
================================


Signup
------

Vinely only allows you to sign up as a Host, Pro or as a Vinely Club Member.

.. http:POST:: /api/v1/auth/signup/

.. note:: The current implementation allows you to signup but without an unassinged role.
	Clarity is still required as to what role signups are allowed.


Login
-----

Allows you to log into the system. All API calls expect the user to be logged in.

.. http:POST:: /api/v1/auth/login/

A successful login returns an ``api_key`` for that session. This ``api_key`` must be sent along with
all subsequent requests

.. note:: All API calls will only allow you to view the information pertaining to the logged in user.

To use the API Key, you can specify an pass the ``username/api_key`` combination either via an 
``Authorization`` http header or as ``GET/POST`` parameters:

Examples::

	# As Authorization header
	Authorization: ApiKey attendee1@example.com:6f6f5ac1a65a6c9ae78ed8a9c7bc59d0430cb89e

	# As GET Parameters
	http://dev.vinely.com/api/v1/user/?username=attendee1@example.com&api_key=6f6f5ac1a65a6c9ae78ed8a9c7bc59d0430cb89e

.. warning::
	
	Use of the Authorization header is preferred for security reasons.

Logout
------

.. http:POST:: /api/v1/auth/logout/
