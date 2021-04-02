from django.contrib import admin
from .models import User,Project,Page,Element,Keyword,TestCase,Environment,Browser,Result,SplitResult,Task

admin.site.register([Project]),
admin.site.register([Page]),
admin.site.register([Element]),
admin.site.register([Keyword]),
admin.site.register([TestCase]),
admin.site.register([Environment]),

admin.site.register([Browser]),
admin.site.register([Result]),
admin.site.register([SplitResult]),
admin.site.register([Task]),
# admin.site.register([Params])
# admin.site.register([Check])
# admin.site.register([LoginConfig])
# admin.site.register([EnvironmentLogin])
admin.site.register([User]),
