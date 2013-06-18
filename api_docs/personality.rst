.. _ref-personality:

============================
Personality and Wine Ratings
============================

Every user that participates in a Vinely Tasting event or Joins the VIP club
can have their Personalities revealed by having their wine ratings for the 6 wines filled in.

Wine Personality
----------------

There are 6 different Wine Personalities and the mystery personality
(for those that have not had their personality revealed yet).

Fetch a list of the Wine Personalities defined by Vinely.

.. http:GET:: /api/v1/personality/

Get information about a specfic wine personality.

.. http:GET:: /api/v1/personality/{id}/


Wine Ratings
------------
Each wine has a number of different values that need to be rated.

The ratings choices are::

    LIKENESS_CHOICES = (
        (1, 'Hate'),
        (2, 'Dislike'),
        (3, 'Neutral'),
        (4, 'Like'),
        (5, 'Love'),
    )

    DNL_CHOICES = (
        (1, 'Too Little'),
        (2, 'Just Right'),
        (3, 'Too Much'),
    )

    SWEET_CHOICES = (
        (1, 'Tart'),
        (2, 'Semi Tart'),
        (3, 'Neutral'),
        (4, 'Semi Sweet'),
        (5, 'Sweet'),
    )

    WEIGHT_CHOICES = (
        (1, 'Light'),
        (2, 'Semi Light'),
        (3, 'Medium'),
        (4, 'Semi Heavy'),
        (5, 'Heavy'),
    )

    TEXTURE_CHOICES = (
        (1, 'Silky'),
        (2, 'Semi Silky'),
        (3, 'Neutral'),
        (4, 'Semi Furry'),
        (5, 'Furry'),
    )

    SIZZLE_CHOICES = (
        (1, 'None'),
        (2, 'Somewhat'),
        (3, 'Tingle'),
        (4, 'Semi Burn'),
        (5, 'Burn')
    )

Fetch a list of Wine rating data for the user currently logged in. 
It should return up to 6 objects for the 6 wines that were tasted

.. http:GET:: /api/v1/rating/

Get information about a particular wine rating

.. http:GET:: /api/v1/rating/{id}/

Update wine rating information

.. http:PUT:: /api/v1/rating/{id}/

Create a new wine rating

.. http:POST:: /api/v1/rating/
