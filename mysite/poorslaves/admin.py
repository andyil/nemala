from django.contrib import admin

# Register your models here.
from django.contrib import admin

from .models import Document, Answer

admin.site.register(Document)
admin.site.register(Answer)