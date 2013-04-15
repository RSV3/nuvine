from django_pylibmc.memcached import PyLibMCCache as DjangoPyLibMCCache


class PyLibMCCache(DjangoPyLibMCCache):
    """
    PyLibMCCache version that interprets 0 to mean, roughly, 30 days.
    This is because `pylibmc interprets 0 to mean literally zero seconds
    <http://sendapatch.se/projects/pylibmc/misc.html#differences-from-python-memcached>`_
    rather than "infinity" as memcached itself does.  The maximum timeout
    memcached allows before treating the timeout as a timestamp is just
    under 30 days.
    """
    def _get_memcache_timeout(self, timeout=None):
        # pylibmc doesn't like our definition of 0
        if timeout == 0:
            return 2591999
        return super(PyLibMCCache, self)._get_memcache_timeout(timeout)
