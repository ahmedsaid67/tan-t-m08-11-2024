from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Sliders,UrunKategori,UrunVitrin,Urunler,Image,\
    References,HizliLinkler,Contact,Hakkimizda,SMedya,Beden,Message


admin.site.register(Sliders)
admin.site.register(UrunKategori)
admin.site.register(UrunVitrin)
admin.site.register(Urunler)
admin.site.register(Image)
admin.site.register(References)
admin.site.register(HizliLinkler)
admin.site.register(Contact)
admin.site.register(Hakkimizda)
admin.site.register(SMedya)
admin.site.register(Beden)
admin.site.register(Message)
