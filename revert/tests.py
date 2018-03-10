from django.test import TestCase
from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import User

from store.models import Edit
from store.models import Batch
from .models import RevertTask

class RevertTaskTest(TestCase):
    @classmethod
    def setUpClass(cls):
        Edit.ingest_jsonlines('store/testdata/one_or_batch.json')
        cls.batch = Batch.objects.get()
        cls.client = Client()
        cls.admin = User(username='admin', password='admin123')
        cls.admin.save()
        cls.john = User(username='john', password='jamesbond007')
        cls.john.save()

    def setUp(self):
        self.client.force_login(self.admin)

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
        response = self.client.post(
            reverse('submit-revert', args=[self.batch.tool.shortid, self.batch.uid]),
            data={'comment':'testing reverts'})
        self.assertEquals(400, response.status_code)

    def test_revert_batch_already_being_reverted(self):
        task = RevertTask(batch=self.batch, user=self.admin, comment="Already reverting")
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

    def test_revert_batch_fine(self):
        response = self.client.post(
            reverse('submit-revert', args=[self.batch.tool.shortid, self.batch.uid]),
            data={'comment':'testing reverts'})
        self.assertEquals(302, response.status_code)

    def test_revert_batch_previous_canceled(self):
        task = RevertTask(batch=self.batch, user=self.admin, comment="Already reverting")
        task.cancel = True
        task.save()
        response = self.client.post(
            reverse('submit-revert', args=[self.batch.tool.shortid, self.batch.uid]),
            data={'comment':'testing reverts'})
        self.assertEquals(302, response.status_code)
        self.assertEquals(2, RevertTask.objects.count())

    def test_stop_not_logged_in(self):
        self.client.logout()
        task = RevertTask(batch=self.batch, user=self.admin, comment="Already reverting")
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
        task = RevertTask(batch=self.batch, user=self.admin, comment="Already reverting")
        task.complete = True
        task.save()
        response = self.client.post(
            reverse('stop-revert', args=[self.batch.tool.shortid, self.batch.uid]))
        self.assertEquals(404, response.status_code)

    def test_stop_fine(self):
        task = RevertTask(batch=self.batch, user=self.admin, comment="Already reverting")
        task.save()
        response = self.client.post(
            reverse('stop-revert', args=[self.batch.tool.shortid, self.batch.uid]))
        self.assertEquals(302, response.status_code)
        task = RevertTask.objects.get(id=task.id)
        self.assertTrue(task.cancel)

    @classmethod
    def tearDownClass(cls):
        pass

