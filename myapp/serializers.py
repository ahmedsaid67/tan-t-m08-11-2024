from rest_framework import serializers

# ---- USER -----


from django.contrib.auth.models import User

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'first_name', 'last_name', 'email')







from .models import Sliders

class SlidersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Sliders
        fields = '__all__'


# ÜRÜN Kategori

from .models import UrunKategori


class UrunKategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrunKategori
        fields = '__all__'


# ürün vitrin



from .models import UrunVitrin


class UrunVitrinSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrunVitrin
        fields = '__all__'

from .models import Beden


class BedenSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beden
        fields = '__all__'


# ürünler

from .models import Urunler


class UrunlerSerializer(serializers.ModelSerializer):
    urun_kategori = UrunKategoriSerializer(read_only=True)
    urun_kategori_id = serializers.IntegerField(write_only=True)

    vitrin_kategori = UrunVitrinSerializer(read_only=True)
    vitrin_kategori_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)


    class Meta:
        model = Urunler
        fields = ['id', 'baslik','slug', 'fiyat', 'kapak_fotografi', 'urun_kategori', 'vitrin_kategori', 'urun_kategori_id',
                  'vitrin_kategori_id', 'durum','aciklama', 'is_removed']

    def create(self, validated_data):
        urun_kategori_id = validated_data.pop('urun_kategori_id')
        urun_kategori = UrunKategori.objects.get(id=urun_kategori_id)

        vitrin_kategori_id = validated_data.pop('vitrin_kategori_id', None)
        vitrin_kategori = UrunVitrin.objects.get(id=vitrin_kategori_id) if vitrin_kategori_id else None

        urun = Urunler.objects.create(urun_kategori=urun_kategori, vitrin_kategori=vitrin_kategori, **validated_data)

        return urun

    def update(self, instance, validated_data):
        urun_kategori_id = validated_data.get('urun_kategori_id', instance.urun_kategori_id)
        urun_kategori = UrunKategori.objects.get(id=urun_kategori_id)

        vitrin_kategori_id = validated_data.get('vitrin_kategori_id', instance.vitrin_kategori_id)
        vitrin_kategori = UrunVitrin.objects.get(id=vitrin_kategori_id) if vitrin_kategori_id else None

        instance.baslik = validated_data.get('baslik', instance.baslik)
        instance.fiyat = validated_data.get('fiyat', instance.fiyat)
        instance.urun_kategori = urun_kategori
        instance.vitrin_kategori = vitrin_kategori
        instance.kapak_fotografi = validated_data.get('kapak_fotografi', instance.kapak_fotografi)
        instance.durum = validated_data.get('durum', instance.durum)
        instance.is_removed = validated_data.get('is_removed', instance.is_removed)

        instance.save()
        return instance

### DECİMALFİLD ile çalışıyorsan boş değer gondereceksen bu "" olmalıdır. null none kabul etmıyor. yada formda hıc koyma oyle işlem yap.

# IMAGE

from .models import Image

class ImageSerializer(serializers.ModelSerializer):
    urun_id = serializers.IntegerField(write_only=True)
    class Meta:
        model = Image
        fields = ['id','urun', 'urun_id', 'image', 'is_removed']

    def create(self, validated_data):
        urun_id = validated_data.pop('urun_id')
        urun = Urunler.objects.get(id=urun_id)
        return Image.objects.create(urun=urun, **validated_data)





# MEDYA


from .models import SMedya
class MedyaSerializer(serializers.ModelSerializer):

    class Meta:
        model = SMedya
        fields = '__all__'


# REFERANSLAR


from .models import References
class ReferencesSerializer(serializers.ModelSerializer):

    class Meta:
        model = References
        fields = '__all__'



# HIZLI LİNKLER


from .models import HizliLinkler
class HizliLinklerSerializer(serializers.ModelSerializer):

    class Meta:
        model = HizliLinkler
        fields = '__all__'


# iletişim

from .models import Contact

class ContactSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contact
        fields = '__all__'



# hakkimizda

from .models import Hakkimizda

class HakkimizdaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hakkimizda
        fields = '__all__'


