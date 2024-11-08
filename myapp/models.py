from django.db import models
import os
from datetime import datetime
from django.utils.text import slugify
import uuid



# ----  MENÜ ----
class Menu (models.Model):
    title = models.CharField(max_length=255)
    selected = models.BooleanField(default=False)

class MenuItem(models.Model):
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True, blank=True, null=True)
    url = models.CharField(max_length=255,blank=True,null=True)
    order = models.PositiveIntegerField()
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True,null=True)
    menu = models.ForeignKey(Menu, on_delete=models.CASCADE)
    durum = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            # Benzersizliği sağlamak için slug'ı kontrol edin
            unique_slug = self.slug
            num = 1
            while MenuItem.objects.filter(slug=unique_slug).exists():
                unique_slug = f'{self.slug}-{num}'
                num += 1
            self.slug = unique_slug
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title



#### SLİDER
def slider_path(instance, filename):
    # Dosya uzantısını al (örn: .jpg, .png)
    ext = filename.split('.')[-1]
    # Benzersiz bir dosya ismi oluştur
    filename = f"{uuid.uuid4()}.{ext}"
    # 'media/personel/' altında bu dosyayı sakla
    return f'slider/{filename}'


class Sliders(models.Model):
    DEVICE_CHOICES = [
        ('mobil', 'Mobil'),
        ('masaüstü', 'Masaüstü'),
    ]
    name = models.CharField(max_length=200)
    img = models.ImageField(upload_to=slider_path, blank=True, null=True)
    url = models.URLField(max_length=500)
    order = models.IntegerField()
    device = models.CharField(max_length=15, choices=DEVICE_CHOICES, default='masaüstü')
    durum = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.name



### ÜRÜN KATEGORİ


from django.utils.text import slugify

def kapakfoto_path_urunkategori(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'urunkategori/kapakfoto/{filename}'

class UrunKategori(models.Model):
    baslik = models.CharField(max_length=200)
    kapak_fotografi = models.ImageField(upload_to=kapakfoto_path_urunkategori, blank=True, null=True)
    durum = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)  # slug alanını ekledik

    def __str__(self):
        return self.baslik

    def save(self, *args, **kwargs):
        # Eğer slug boşsa ve bu yeni bir nesne ise
        if not self.id and not self.slug:
            # Önce nesneyi veritabanına kaydet (bu, bir id atar)
            super(UrunKategori, self).save(*args, **kwargs)
            # Slug alanını oluştur
            self.slug = slugify(f"{self.baslik}-{self.id}")
            # save() metodunu tekrar çağırarak slug'ı kaydet
            kwargs.pop('force_insert', None)  # force_insert argümanını kaldır
            super(UrunKategori, self).save(*args, **kwargs)
        else:
            super(UrunKategori, self).save(*args, **kwargs)


## ürün VİTRİN ###

class UrunVitrin(models.Model):
    baslik = models.CharField(max_length=200)
    order = models.IntegerField()
    durum = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)
    slug = models.SlugField(max_length=200, unique=True, blank=True)

    def __str__(self):
        return self.baslik

    def save(self, *args, **kwargs):
        # Eğer slug boşsa ve bu yeni bir nesne ise
        if not self.slug:
            # Önce nesneyi veritabanına kaydet (bu, bir id atar)
            super(UrunVitrin, self).save(*args, **kwargs)
            # Slug alanını oluştur
            self.slug = slugify(f"{self.baslik}-{self.id}")
            # save() metodunu tekrar çağırarak slug'ı kaydet
            kwargs.pop('force_insert', None)  # force_insert argümanını kaldır
            super(UrunVitrin, self).save(*args, **kwargs)
        else:
            super(UrunVitrin, self).save(*args, **kwargs)




### ürünler  ###

from decimal import Decimal


def kapakfoto_path_urunler(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'urunler/kapakfoto/{filename}'


class Urunler(models.Model):
    baslik = models.CharField(max_length=255,blank=True,null=True)
    slug = models.SlugField(max_length=200, unique=True,null=True, blank=True)
    fiyat = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    kapak_fotografi = models.ImageField(upload_to=kapakfoto_path_urunler, blank=True, null=True)
    urun_kategori=models.ForeignKey(UrunKategori,on_delete=models.CASCADE,null=True, blank=True)
    vitrin_kategori = models.ForeignKey(UrunVitrin, on_delete=models.SET_NULL, null=True, blank=True)
    durum = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)



    def __str__(self):
        return self.baslik


    def save(self, *args, **kwargs):
        # Eğer slug boşsa ve bu yeni bir nesne ise
        if not self.slug:
            # Önce nesneyi veritabanına kaydet (bu, bir id atar)
            super(Urunler, self).save(*args, **kwargs)
            # Slug alanını oluştur
            self.slug = slugify(f"{self.baslik}-{self.id}")
            # save() metodunu tekrar çağırarak slug'ı kaydet
            kwargs.pop('force_insert', None)  # force_insert argümanını kaldır
            super(Urunler, self).save(*args, **kwargs)
        else:
            super(Urunler, self).save(*args, **kwargs)




# beden tablosu


class Beden(models.Model):
    numara = models.IntegerField()
    urun = models.ForeignKey(Urunler, related_name='bedenler', on_delete=models.CASCADE, null=True, blank=True)
    durum = models.BooleanField(default=False)

    def __str__(self):
        return str(self.numara)



def album_path_fotogaleri(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'urun/album/{filename}'

class Image(models.Model):
    urun = models.ForeignKey(Urunler, related_name='images', on_delete=models.CASCADE,null=True, blank=True)
    image = models.ImageField(upload_to=album_path_fotogaleri, blank=True, null=True)
    durum = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)
    def __str__(self):
        return f"{self.urun.baslik} - Image {self.id}"







class SMedya(models.Model):
    twitter = models.URLField(max_length=100, blank=True, null=True)
    instagram = models.URLField(max_length=100, blank=True, null=True)
    facebook = models.URLField(max_length=100, blank=True, null=True)
    youtube = models.URLField(max_length=100, blank=True, null=True)
    tiktok = models.URLField(max_length=100, blank=True, null=True)
    linkedin = models.URLField(max_length=100, blank=True, null=True)





def kapakfoto_path_referances(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'references/kapakfoto/{filename}'


class References(models.Model):
    name = models.CharField(max_length=200)
    img = models.ImageField(upload_to=kapakfoto_path_referances, blank=True, null=True)
    url = models.URLField(max_length=500 , blank=True, null=True)
    durum = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)



class HizliLinkler(models.Model):
    name = models.CharField(max_length=200)
    url = models.URLField(max_length=500, blank=True, null=True)
    durum = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)



#### iletişim

class Contact(models.Model):
    address = models.CharField(max_length=255, blank=True, null=True)
    phone1 = models.CharField(max_length=20, blank=True, null=True)
    phone2 = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"Contact {self.id}"


# hakkımızda

class Hakkimizda(models.Model):
    content = models.TextField(blank=True, null=True)

    def __str__(self):
        return "Hakkımızda"



# başlık görsel


def kapakfoto_path_baslikgorsel(instance, filename):
    ext = filename.split('.')[-1]
    filename = f"{uuid.uuid4()}.{ext}"
    return f'baslikgorsel/kapakfoto/{filename}'


class BaslikGorsel(models.Model):
    name = models.CharField(max_length=200, blank=True, null=True)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    img = models.ImageField(upload_to=kapakfoto_path_baslikgorsel, blank=True, null=True)
    durum = models.BooleanField(default=True)
    is_removed = models.BooleanField(default=False)

    def __str__(self):
        return self.name


    def save(self, *args, **kwargs):
        # Eğer slug boşsa ve bu yeni bir nesne ise
        if not self.slug:
            # Önce nesneyi veritabanına kaydet (bu, bir id atar)
            super(BaslikGorsel, self).save(*args, **kwargs)
            # Slug alanını oluştur
            self.slug = slugify(f"{self.name}-{self.id}")
            # save() metodunu tekrar çağırarak slug'ı kaydet
            kwargs.pop('force_insert', None)  # force_insert argümanını kaldır
            super(BaslikGorsel, self).save(*args, **kwargs)
        else:
            super(BaslikGorsel, self).save(*args, **kwargs)


