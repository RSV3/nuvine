.. _ref-accounts:

=====================================
Accounts: User and profile management
=====================================

Handle all user and profile management requests

User
----
Fetching user information. 

.. http:GET:: /api/v1/user/

Detailed profile information is included in the returned information but it can
also be fetched in a separate API call if required. *See below*.

.. NOTE:: This exists for the purposes of convention and can be used if you don't have the ``user_id``. 
  It returns a list with only one item i.e. the profile of the person currently logged in.

Get information by id.

.. http:GET:: /api/v1/profile/{id}/

This returns information about the user with the provided ``id``.

.. NOTE:: For security reasons, the ``id`` must be the ``user_id`` of the currently logged in person.

Update user information

.. http:PUT:: /api/v1/user/{id}/

.. NOTE:: For security reasons, the ``id`` must be the ``user_id`` of the currently logged in person.


Profile
-------

Returns user profile information

.. http:GET:: /api/v1/profile/

.. NOTE:: This exists for the purposes of convention. It returns a list with only one item i.e. 
  the profile of the person currently logged in.

Get information by id.

.. http:GET:: /api/v1/profile/{id}/

This returns information about the profile with the provided ``id``. 

.. NOTE:: For security reasons, the ``id`` must be the ``profile_id`` of the currently logged in person.

Update profile information

.. http:PUT:: /api/v1/profile/{id}/

.. NOTE:: For security reasons, the ``id`` must be the ``profile_id`` of the currently logged in person.

Updating the user profile image::

    # The image has to be sent as base64 encoded JSON string
    # it should include the file name

    # Example

    {
        'image':
            {
                'name': 'filename.png',
                'file': <base64-encoded-data>
            }
    }
