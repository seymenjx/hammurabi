from django.contrib import admin
from .models import PromptFeedback,Prompt,Convo,BlockNote,KnowledgeBase,Note,KnowledgeSource
# Register your models here.

admin.site.register(PromptFeedback)
admin.site.register(Convo)
admin.site.register(Prompt)

admin.site.register(Note)
admin.site.register(BlockNote)

admin.site.register(KnowledgeSource)
admin.site.register(KnowledgeBase)