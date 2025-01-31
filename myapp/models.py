from django.db import models
import os
from datetime import datetime
from django.utils.text import slugify
import uuid





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
    slug = models.SlugField(max_length=255, unique=True, null=True, blank=True)

    def __str__(self):
        return self.baslik

    def __init__(self, *args, **kwargs):
        super(UrunKategori, self).__init__(*args, **kwargs)
        self.__original_baslik = self.baslik  # Başlığın orijinal değerini sakla

    def save(self, *args, **kwargs):
        # Yeni bir kayıt ise
        if not self.id:
            super(UrunKategori, self).save(*args, **kwargs)  # Önce kaydet (ID oluşturulur)
            if not self.slug:  # Slug yoksa oluştur
                self.slug = slugify(f"{self.baslik}-{self.id}")
                super(UrunKategori, self).save(update_fields=['slug'])  # Slug'ı güncelle
        else:
            # Başlık değişmişse
            if self.baslik != self.__original_baslik:
                self.slug = slugify(f"{self.baslik}-{self.id}")
                super(UrunKategori, self).save(*args, **kwargs)  # Tüm modeli kaydet
            else:
                super(UrunKategori, self).save(*args, **kwargs)  # Normal kaydetme işlemi

        # Orijinal başlık değerini güncelle
        self.__original_baslik = self.baslik

    def baslik_has_changed(self):
        """
        Başlık değiştiyse True döner, aksi halde False.
        """
        if not self.pk:  # Yeni nesne
            return False
        eski_baslik = UrunKategori.objects.filter(pk=self.pk).values_list('baslik', flat=True).first()
        return eski_baslik != self.baslik

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
    aciklama = models.TextField(blank=True, null=True)
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



# özellik tablosu

class Ozellik(models.Model):
    name = models.CharField(max_length=255)
    urun = models.ForeignKey(Urunler, related_name='ozellikler', on_delete=models.CASCADE, null=True, blank=True)
    durum = models.BooleanField(default=False)

    def __str__(self):
        return str(self.name)



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


