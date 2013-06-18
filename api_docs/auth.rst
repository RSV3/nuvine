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

A successful login returns an api_key for that session. This api_key must be sent along with
all subsequent requests

.. note:: All API calls will only allow you to view the information pertaining to the logged in user.


Logout
------

.. http:POST:: /api/v1/auth/logout/
