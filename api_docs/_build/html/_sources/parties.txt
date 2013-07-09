.. _ref-parties:

Parties and Events
##################

Party
=====

Vinely Parties are private parties where someone has to be invited in order to attend. 
Invitations are sent out via mail which contains an RSVP link.

Vinely Events are public parties hosted by Vinely and users can come to the site and RSVP to attend.
Generally no invitations are sent out for Events.

Fetch a list of upcoming parties that a user has been invited to

.. http:GET:: /api/v1/party/

.. NOTE:: Past parties and events are not returned

Fetch information about a specific party

.. http:GET:: /api/v1/party/{id}/

.. NOTE:: The party details have a property called ``is_event`` to distinguish between Vinely events and private parties.

Filtering parties
-----------------

By default ``/api/v1/party`` returns a list of all upcoming parties

*Only My Parties*

.. http:GET:: /api/v1/party/?me=1

*Filtering parties by title*

.. http:GET:: /api/v1/party/?title=icontains=<party title>


Party Invitations and RSVP
==========================
Every Vinely Party/Event has party invites that associate users with a party.

Fetch a list of all party invitations

.. http:GET:: /api/v1/partyinvite/

Fetch information about a specific party invite.

.. http:GET:: /api/v1/partyinvite/{id}/

Creating a party invitation.

Hosts and Pro's can invite people to a party at any time. 
Other tasters an only invite people to a party if the Host allows it.

.. http:POST:: /api/v1/partyinvite/

.. warning ::

    Unlike the other calls where ``relation`` fields require the uri, you should provide the names 
    and email of the ``invitee`` when creating an invitation.

    If the user does not exist, a new account will be created for them.

Example::
    
    # Only the invitee and party fields are required, all others are optional.

    {
      "invitee": {
        "first_name": "First",
        "last_name": "Last",
        "email": "someuser@example.com"
      },
      "party": "/api/v1/party/123/"
    }

Updating a party invitation

.. http:PUT:: /api/v1/partyinvite/{id}/

A party invitation can be updated at any time up until the day of the event.

**RSVP'ing to an event**::

    RESPONSE_CHOICES = (
        (0, '--'),
        (1, 'No'),
        (2, 'Maybe'),
        (3, 'Yes'),
        (4, 'Under Age'),
    )

.. NOTE:: You rsvp to an event by setting the ``response`` field of the party invite object to any of the integer values in ``RESPONSE_CHOICES`` above.

