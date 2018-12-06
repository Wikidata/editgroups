from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User
from django.conf import settings
from requests_oauthlib import OAuth1
from social_django.models import UserSocialAuth
import requests_mock
from editgroups.celery import app as celery_app
from unittest.mock import patch

from store.models import Edit
from store.models import Batch
from .models import RevertTask

def fake_revert(*args, **kwargs):
    pass

class RevertTaskTest(TestCase):
    @classmethod
    def setUpClass(cls):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        cls.batch = Batch.objects.get()
        cls.client = Client()
        cls.mary = User(username='admin', password='admin123')
        cls.mary.save()
        mary_auth = UserSocialAuth(
            user=cls.mary, provider='wikidata', uid='39834872',
            extra_data= {"access_token":
                {"oauth_token": "12345",
                 "oauth_token_secret": "67890"},
        "auth_time": 1520695332})
        mary_auth.save()
        cls.john = User(username='john', password='jamesbond007')
        cls.john.save()

    def setUp(self):
        self.client.force_login(self.mary)
        celery_app.task_always_eager = True

    def test_revert_not_logged_in(self):
        self.client.logout()
        response = self.client.post(
            reverse('submit-revert', args=[self.batch.tool.shortid, self.batch.uid]),
            data={'comment':'testing reverts'})
        self.assertEquals(401, response.status_code)

    def test_revert_invalid_batch(self):
        response = self.client.post(
            reverse('submit-revert', args=['NOTATOOL', 'uster']),
            data={'comment':'testing reverts'})
        self.assertEquals(404, response.status_code)

    def test_revert_batch_already_reverted(self):
        Edit.objects.all().update(reverted=True)
        b = Batch.objects.get()
        b.nb_reverted_edits = b.nb_edits
        b.save()
        response = self.client.post(
            reverse('submit-revert', args=[self.batch.tool.shortid, self.batch.uid]),
            data={'comment':'testing reverts'})
        self.assertEquals(400, response.status_code)

    def test_revert_batch_already_being_reverted(self):
        task = RevertTask(batch=self.batch, user=self.mary, comment="Already reverting")
        task.save()

        batch = Batch.objects.get(id=self.batch.id)
        self.assertEquals(task, batch.active_revert_task)

        response = self.client.post(
            reverse('submit-revert', args=[self.batch.tool.shortid, self.batch.uid]),
            data={'comment':'testing reverts'})
        self.assertEquals(400, response.status_code)

    def test_revert_batch_no_summary(self):
        response = self.client.post(
            reverse('submit-revert', args=[self.batch.tool.shortid, self.batch.uid]),
            data={})
        self.assertEquals(400, response.status_code)

    @patch.object(RevertTask, 'revert_edit', fake_revert)
    def test_revert_batch_fine(self):
        response = self.client.post(
            reverse('submit-revert', args=[self.batch.tool.shortid, self.batch.uid]),
            data={'comment':'testing reverts'})
        self.assertEquals(302, response.status_code)

    @patch.object(RevertTask, 'revert_edit', fake_revert)
    def test_revert_batch_previous_canceled(self):
        task = RevertTask(batch=self.batch, user=self.mary, comment="Already reverting")
        task.cancel = True
        task.save()
        response = self.client.post(
            reverse('submit-revert', args=[self.batch.tool.shortid, self.batch.uid]),
            data={'comment':'testing reverts'})
        self.assertEquals(302, response.status_code)
        self.assertEquals(2, RevertTask.objects.count())

    def test_stop_not_logged_in(self):
        self.client.logout()
        task = RevertTask(batch=self.batch, user=self.mary, comment="Already reverting")
        task.save()
        response = self.client.post(
            reverse('stop-revert', args=[self.batch.tool.shortid, self.batch.uid]))
        self.assertEquals(401, response.status_code)

    def test_stop_no_task(self):
        response = self.client.post(
            reverse('stop-revert', args=[self.batch.tool.shortid, self.batch.uid]))
        self.assertEquals(404, response.status_code)

    def test_stop_different_user(self):
        task = RevertTask(batch=self.batch, user=self.john, comment="Already reverting")
        task.save()
        response = self.client.post(
            reverse('stop-revert', args=[self.batch.tool.shortid, self.batch.uid]))
        self.assertEquals(403, response.status_code)

    def test_stop_task_already_complete(self):
        task = RevertTask(batch=self.batch, user=self.mary, comment="Already reverting")
        task.complete = True
        task.save()
        response = self.client.post(
            reverse('stop-revert', args=[self.batch.tool.shortid, self.batch.uid]))
        self.assertEquals(404, response.status_code)

    def test_stop_fine(self):
        task = RevertTask(batch=self.batch, user=self.mary, comment="Already reverting")
        task.save()
        response = self.client.post(
            reverse('stop-revert', args=[self.batch.tool.shortid, self.batch.uid]))
        self.assertEquals(302, response.status_code)
        task = RevertTask.objects.get(id=task.id)
        self.assertTrue(task.cancel)

    def test_oauth_tokens(self):
        task = RevertTask(batch=self.batch, user=self.mary, comment="Already reverting")
        self.assertEquals({'oauth_token':'12345','oauth_token_secret':'67890'},
            task.oauth_tokens)

    def test_oauth_tokens_canceled(self):
        task = RevertTask(batch=self.batch, user=self.mary, comment="Already reverting")
        task.cancel = True
        with self.assertRaises(ValueError):
            self.assertEquals({'oauth_token':'12345','oauth_token_secret':'67890'},
                task.oauth_tokens)

    def test_summary(self):
        task = RevertTask(batch=self.batch, user=self.mary, comment="Already reverting")
        edit = self.batch.edits.all()[0]
        self.assertTrue(len(task.uid) > 5)
        summary = task.undo_summary(edit)
        self.assertTrue(summary.startswith('/* undo'))
        self.assertTrue("Already reverting" in summary)
        self.assertTrue(task.uid in summary)

    def test_revert_edit(self):
        task = RevertTask(batch=self.batch, user=self.mary, comment="Already reverting")
        edit = self.batch.edits.order_by('-timestamp')[0]
        with requests_mock.mock() as m:
            auth = OAuth1(settings.SOCIAL_AUTH_MEDIAWIKI_KEY,
                        settings.SOCIAL_AUTH_MEDIAWIKI_SECRET,
                        '12345', '67890')
            m.get('https://www.wikidata.org/w/api.php?action=query&meta=tokens&format=json',
                text='{"batchcomplete":"","query":{"tokens":{"csrftoken":"abcd"}}}')
            m.post('https://www.wikidata.org/w/api.php',
                text='{"edit":{"result":"Success","pageid":4246474,"title":"Q4115189","contentmodel":"wikibase-item","oldrevid":647380593,"newrevid":647388912,"newtimestamp":"2018-03-10T20:19:49Z"}}')

            task.revert_edit(edit)

    @classmethod
    def tearDownClass(cls):
        pass




