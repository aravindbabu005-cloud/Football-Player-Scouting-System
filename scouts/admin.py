from django.contrib import admin
from .models import Academy, Player, UserProfile, ShortlistedPlayer

admin.site.register(UserProfile)
admin.site.register(Academy)
admin.site.register(Player)
admin.site.register(ShortlistedPlayer)
