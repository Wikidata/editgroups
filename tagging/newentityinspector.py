
import requests
import json

from .diffdigest import DiffDigest

class NewEntityInspector(object):

    def __init__(self, endpoint='https://www.wikidata.org/w/api.php'):
        """
        Initializes an inspector for the given MediaWiki API endpoint.
        """
        self.endpoint = endpoint

    def extract(self, revids):
        """
        Given a list of revision ids, extract one merged digest
        of all their contents.

        The maximum number of revids supplied is 50.
        :param revids: a list of revision ids, corresponding to creations of new items
        :returns: a DiffDigest merging all the creations together.
        """
        rev_to_content = self._retrieve_revisions(revids)
        digest = DiffDigest()
        for entity_json in rev_to_content.values():
            other_digest = self.extract_from_entity(entity_json)
            digest += other_digest
        return digest

    def extract_from_entity(self, entity_json):
        """
        Given a parsed JSON representation of the state of an item,
        extract a digest as if this was a new entity (so, empty initial
        content).
        """
        return DiffDigest(
            statements = (entity_json.get('claims') or {}).keys(),
            qualifiers = self._extract_qualifiers(entity_json),
            labels = (entity_json.get('labels') or {}).keys(),
            descriptions = (entity_json.get('descriptions') or {}).keys(),
            aliases = (entity_json.get('aliases') or {}).keys(),
        )

    def _extract_qualifiers(self, entity_json):
        """
        Extract the qualifier pids from an entity.
        """
        for statement_group in (entity_json.get('claims') or {}).values():
            for statement in statement_group:
                for qualifier_pid in (statement.get('qualifiers') or {}).keys():
                    yield qualifier_pid

    def _retrieve_revisions(self, revids):
        """
        Retrieves revisions of an item in JSON format.
        Useful to analyze the "diff" of new item creations.
        Maximum 50 revision ids.

        :param revid: a list of revision ids, corresponding to
            creations of new items
        :returns: map from revision ids to json representations of the revisions
        """
        assert len(revids) <= 50
        req = requests.get(self.endpoint,
            {
                'action': 'query',
                'prop': 'revisions',
                'revids': '|'.join(str(revid) for revid in revids),
                'rvslots': '*',
                'rvprop': 'content|ids',
                'format': 'json',
            })
        req.raise_for_status()
        rev_to_content = {}
        for page in (req.json().get('query', {}).get('pages') or {}).values():
            for rev in page.get('revisions') or []:
                text = rev.get('slots', {}).get('main', {}).get('*')
                revid = rev.get('revid')
                if revid and text:
                    rev_to_content[revid] = json.loads(text)
        return rev_to_content


