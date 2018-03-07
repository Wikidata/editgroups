from django.contrib import admin

# Register your models here.
from store.models import Tool
from store.models import Batch
from store.models import Edit

admin.site.register(Tool)
admin.site.register(Batch)
admin.site.register(Edit)
