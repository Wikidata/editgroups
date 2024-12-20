
import requests
import lxml.html
import json
from lxml import etree
import re
from collections import namedtuple
from .diffdigest import DiffDigest

property_re = re.compile('.*(Property:|Special:EntityPage/)(P\d+)')

class DiffInspector(object):
    """
    Object which retrieves and parses the diff of a Wikibase
    edit, and extracts the property ids of statements and qualifiers
    from it.
    """

    def __init__(self, endpoint='https://www.wikidata.org/w/api.php'):
        """
        Creates an inspector for the given MediaWiki endpoint.
        """
        self.endpoint = endpoint

    def inspect(self, oldrevid, newrevid):
        """
        Given two revision ids, assumed to be of the same page,
        extract a digest from it.
        This will not work for item creations (oldrevid = 0).

        :param oldrevid: the old revision id
        :param newrevid: the new revision id
        :returns: a DiffDigest
        """
        assert oldrevid != 0
        html_diff = self._retrieve_html_diff(oldrevid, newrevid)
        return self._extract_digest(html_diff)

    def _retrieve_html_diff(self, oldrevid, newrevid):
        """
        Given two revision ids, assumed to be of the same page,
        queries the Wikibase API and returns the HTML representation
        of the diff between the two.

        :param oldrevid: the old revision id
        :param newrevid: the new revision id
        """
        req = requests.get(self.endpoint,
            {
                'action': 'compare',
                'fromrev': oldrevid,
                'torev': newrevid,
                'uselang': 'en',
                'format': 'json',
            })
        req.raise_for_status()
        return req.json().get('compare', {}).get('*')

    def _extract_digest(self, html_diff):
        """
        Given the HTML representation of a diff, return
        the pids which appear as statements or qualifiers
        in the diff and the language codes appearing as terms,
        in a DiffDigest object.
        """
        digest = DiffDigest()
        if not html_diff:
            return digest

        encoded_html = ('<table>'+html_diff+'</table>').encode('utf-8')
        tree = lxml.html.fromstring(encoded_html)

        qualifier_change = False
        for td in tree.xpath('//td'):
            if td.get('class') == 'diff-lineno':
                difftype = etree.tostring(td, method='text', encoding='unicode')
                if not difftype:
                    continue
                difftype = difftype.lower()
                if difftype.startswith('property /'):
                    link = td.xpath('.//a')[0]
                    pid = self._a_to_pid(link)
                    if pid:
                        digest.statements.add(pid)
                        if difftype.endswith('qualifier'):
                            qualifier_change = True
                elif difftype.startswith('label / '):
                    digest.labels.add(difftype[len('label / '):].split(' ')[0])
                elif difftype.startswith('description /'):
                    digest.descriptions.add(difftype[len('description / '):].split(' ')[0])
                elif difftype.startswith('aliases /'):
                    digest.aliases.add(difftype[len('aliases / '):].split(' ')[0])
                elif difftype.startswith('links /'):
                    digest.sitelinks.add(difftype[len('links / '):].split(' ')[0])
            elif td.get('class') in ['diff-addedline','diff-deletedline'] and qualifier_change:
                link = td.xpath('.//a')[0]
                pid = self._a_to_pid(link)
                if pid:
                    digest.qualifiers.add(pid)
                qualifier_change = False

        return digest

    def _a_to_pid(self, link):
        """
        Given an <a> element, return the PID.
        """
        title = link.get('title')
        match = property_re.match(title)
        if match:
            return match.group(2)

