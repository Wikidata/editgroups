

class DiffDigest(object):
    """
    An object holding statistics about a diff:
    which properties appeared as statements, qualifiers
    which language codes appeared as labels, descriptions and aliases.
    """

    def __init__(self,
            statements=None,
            qualifiers=None,
            labels=None,
            descriptions=None,
            aliases=None,
            sitelinks=None):
        """
        Create a diff digest.
        """
        self.statements = set(statements or [])
        self.qualifiers = set(qualifiers or [])
        self.labels = set(labels or [])
        self.descriptions = set(descriptions or [])
        self.aliases = set(aliases or [])
        self.sitelinks = set(sitelinks or [])

    def json(self):
        """
        Serializes the digest to a dictionary.
        """
        return {
            'statements': self.statements,
            'qualifiers': self.qualifiers,
            'labels': self.labels,
            'descriptions': self.descriptions,
            'aliases': self.aliases,
            'sitelinks': self.sitelinks,
        }

    def __add__(self, other):
        return DiffDigest(
            statements = self.statements | other.statements,
            qualifiers = self.qualifiers | other.qualifiers,
            labels = self.labels | other.labels,
            descriptions = self.descriptions | other.descriptions,
            aliases = self.aliases | other.aliases,
            sitelinks = self.sitelinks | other.sitelinks,
        )

    def __str__(self):
        return ', '.join('{}: {}'.format(key, val) for key, val in self.json().items() if val) or 'empty'

    def __repr__(self):
        return '<DiffDigest: {}>'.format(str(self))

    def __eq__(self, other):
        return other.json() == self.json()


