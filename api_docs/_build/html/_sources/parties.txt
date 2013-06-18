.. _ref-parties:

==================
Parties and Events
==================


Events
------

Vinely Events are public parties hosted by Vinely and users can come to the site and RSVP to attend.
Generally no invitations are sent out for Events.

Fetch event list

.. http:GET:: /api/v1/event/

This returns the list of all upcoming Vinely events.

.. NOTE:: Past events are not returned

Fetch information about a specific event

.. http:GET:: /api/v1/event/{id}/

Party
-----

Vinely Parties are private parties where someone has to be invited in order to attend. 
Invitations are sent out via mail which contains an RSVP link.

Fetch a list of upcoming parties that a user has been invited to

.. http:GET:: /api/v1/party/

.. NOTE:: Past parties are not returned

Fetch information about a specific party

.. http:GET:: /api/v1/party/{id}/


Party Invitations and RSVP
--------------------------
Every Vinely Party/Event has party invites that associate users with a party.

Fetch a list of all party invitations

.. http:GET:: /api/v1/partyinvite/

Fetch information about a specific party invite.

.. http:GET:: /api/v1/partyinvite/{id}/

Creating a party invitation.

Hosts and Pro's can invite people to a party at any time. 
Other tasters an only invite people to a party if the Host allows it.

.. http:POST:: /api/v1/partyinvite/

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

.. NOTE:: You rsvp to an event by setting the `response` field of the party invite object to any of the integer values in `RESPONSE_CHOICES` above.

