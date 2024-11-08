from django.db.models.signals import post_migrate,post_save
from django.dispatch import receiver
from .models import Contact,Hakkimizda,BaslikGorsel,SMedya,Beden,Menu, MenuItem,Urunler

@receiver(post_migrate)
def create_initial_contact(sender, **kwargs):
    if sender.name == 'myapp':
        if not Contact.objects.exists():
            Contact.objects.create()


@receiver(post_migrate)
def create_initial_hakkimizda(sender, **kwargs):
    if sender.name == 'myapp':
        if not Hakkimizda.objects.exists():
            Hakkimizda.objects.create()



@receiver(post_migrate)
def create_initial_baslikgorsel(sender, **kwargs):
    if sender.name == 'myapp':  # 'myapp' yerine kendi uygulama adınızı koyun
        if not BaslikGorsel.objects.exists():
            initial_data = [
                {"name": "Referanslar", "slug": "referanslar"},
                {"name": "Hakkımızda", "slug": "hakkimizda"},
                {"name": "İletişim", "slug": "iletisim"},
            ]

            for data in initial_data:
                BaslikGorsel.objects.create(name=data['name'], slug=data['slug'])



@receiver(post_migrate)
def create_initial_medya(sender, **kwargs):
    if sender.name == 'myapp':
        if not SMedya.objects.exists():
            SMedya.objects.create()









@receiver(post_migrate, sender=None)
def create_initial_data(sender, **kwargs):
    if sender.name == 'myapp':
        # Menu modeli için veri oluşturma işlemleri
        if not Menu.objects.exists():
            # Menüyü Oluştur
            menu01 = Menu.objects.create(title='menu01', selected=True)

            # MenuItems Verileri
            menu_items_data = [
                {'title': 'Ana Sayfa', 'order': 1, 'url': '/', 'slug': 'anasayfa'},
                {'title': 'Ürünlerimiz', 'order': 2, 'url': '/urunlerimiz', 'slug': 'urunlerimiz'},
                {'title': 'Referanslar', 'order': 3, 'url': '/referanslar', 'slug': 'referanslar'},
                {'title': 'Hakkımızda', 'order': 4, 'url': '/hakkimizda', 'slug': 'hakkimizda'},
                {'title': 'İletişim', 'order': 5, 'url': '/iletisim', 'slug': 'iletisim'},
            ]

            # MenuItems Oluştur
            for item in menu_items_data:
                MenuItem.objects.create(
                    title=item['title'],
                    slug=item['slug'],
                    url=item['url'],
                    order=item['order'],
                    menu=menu01,
                    durum=True,
                    is_removed=False,
                    parent=None
                )