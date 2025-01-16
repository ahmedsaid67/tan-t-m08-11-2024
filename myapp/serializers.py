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


# özellik

from .models import Ozellik


class OzellikSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ozellik
        fields = '__all__'



# ürünler

from .models import Urunler


class UrunlerSerializer(serializers.ModelSerializer):
    urun_kategori = UrunKategoriSerializer(read_only=True)
    urun_kategori_id = serializers.IntegerField(write_only=True)

    vitrin_kategori = UrunVitrinSerializer(read_only=True)
    vitrin_kategori_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    #bedenler = BedenSerializer(read_only=True,many=True)


    class Meta:
        model = Urunler
        fields = ['id', 'baslik','slug', 'fiyat', 'kapak_fotografi', 'urun_kategori', 'vitrin_kategori', 'urun_kategori_id',
                  'vitrin_kategori_id', 'durum','aciklama','is_removed']

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
        instance.aciklama = validated_data.get('aciklama', instance.aciklama)
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

# tek bir ürünün özelliklerini sadece goruntuleme ıcın yazılmıs bır endpointtir. kullanıcı arayuzden urun detay sayfasında kullanıcaktır.


class BedenGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beden
        fields = ['id', 'numara']

class OzellikGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ozellik
        fields = ['id', 'name']


class UrunGetKategoriSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrunKategori
        fields = ['id', 'baslik','slug']


class UrunGetVitrinSerializer(serializers.ModelSerializer):
    class Meta:
        model = UrunKategori
        fields = ['id', 'baslik','slug']


class ImageGetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Image
        fields = ['id', 'image']

class UrunlerGetSerializer(serializers.ModelSerializer):
    urun_kategori = UrunGetKategoriSerializer(read_only=True)

    bedenler = serializers.SerializerMethodField()
    ozellikler = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()

    class Meta:
        model = Urunler
        fields = ['id', 'baslik', 'slug', 'fiyat', 'kapak_fotografi', 'urun_kategori', 'aciklama', 'bedenler', 'images', 'ozellikler']

    def get_bedenler(self, obj):
        # Sadece durumu True olan bedenler
        bedenler = obj.bedenler.filter(durum=True)
        return BedenGetSerializer(bedenler, many=True).data

    def get_ozellikler(self, obj):
        # Sadece durumu True olan özellikler
        ozellikler = obj.ozellikler.filter(durum=True)
        return OzellikGetSerializer(ozellikler, many=True).data

    def get_images(self, obj):
        # request'i context'ten alıyoruz
        request = self.context.get('request')

        # Resimleri alıyoruz, sadece is_removed=False
        images = obj.images.filter(is_removed=False)

        # Resimleri serileştiriyoruz
        image_serializer = ImageGetSerializer(images, many=True, context={'request': request})

        # Serileştirilmiş resim verisini döndürüyoruz
        return image_serializer.data



## paneldekı arama için yazılmış serializers get sadece




class BedenGetPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Beden
        fields = ['id', 'numara','durum']
        extra_kwargs = {'id': {'read_only': False}}

class OzellikGetPanelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ozellik
        fields = ['id', 'name','durum']
        extra_kwargs = {'id': {'read_only': False}} # ilişkili verilerden id ideğerini data da gonderıldıgınde algılayabılmesı ıcın sadece okunur degıl ekleme ıhtıyacı oldu. update de id yakalanamıyord.
class UrunlerDetailSerializer(serializers.ModelSerializer):
    urun_kategori = UrunGetKategoriSerializer()
    vitrin_kategori = UrunGetVitrinSerializer()

    bedenler = serializers.SerializerMethodField()
    ozellikler = serializers.SerializerMethodField()


    class Meta:
        model = Urunler
        fields = ['id', 'baslik', 'slug', 'fiyat', 'kapak_fotografi', 'urun_kategori','vitrin_kategori', 'aciklama', 'bedenler', 'ozellikler','durum']

    def get_bedenler(self, obj):
        # Sadece durumu True olan bedenler
        bedenler = obj.bedenler.all()
        return BedenGetPanelSerializer(bedenler, many=True).data

    def get_ozellikler(self, obj):
        # Sadece durumu True olan özellikler
        ozellikler = obj.ozellikler.all()
        return OzellikGetPanelSerializer(ozellikler, many=True).data

import  json
class UrunlerUpdateSerializer(serializers.ModelSerializer):
    urun_kategori = serializers.PrimaryKeyRelatedField(queryset=UrunKategori.objects.all(), required=False)
    vitrin_kategori = serializers.PrimaryKeyRelatedField(queryset=UrunVitrin.objects.all(), required=False)
    # Bedenler ve Özellikler için serializer'ı kullanmıyoruz, string olarak veriyi alacağız.
    bedenler = serializers.CharField(required=False, allow_blank=True)
    ozellikler = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Urunler
        fields = ['urun_kategori', 'vitrin_kategori', 'baslik', 'slug', 'fiyat', 'kapak_fotografi', 'aciklama', 'bedenler', 'ozellikler','durum']

    def update(self, instance, validated_data):
        # Gelen verilerde bedenler ve ozellikler varsa, bunları JSON'dan çözerek alıyoruz.
        bedenler_data = validated_data.pop('bedenler', None)
        ozellikler_data = validated_data.pop('ozellikler', None)

        # PATCH isteklerinde sadece gelen veriler güncellenir
        if self.context['request'].method == 'PATCH':
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
        elif self.context['request'].method == 'PUT':
            # PUT: Tüm alanlar gönderilmeli, eksik olanlar mevcut değerlerle korunur
            instance.baslik = validated_data.get('baslik', instance.baslik)
            instance.slug = validated_data.get('slug', instance.slug)
            instance.fiyat = validated_data.get('fiyat', instance.fiyat)
            instance.kapak_fotografi = validated_data.get('kapak_fotografi', instance.kapak_fotografi)
            instance.aciklama = validated_data.get('aciklama', instance.aciklama)
            instance.urun_kategori = validated_data.get('urun_kategori', instance.urun_kategori)
            instance.vitrin_kategori = validated_data.get('vitrin_kategori', instance.vitrin_kategori)
            instance.durum = validated_data.get('durum', instance.durum)

        instance.save()

        # Eğer bedenler verisi varsa, string formatında geldiyse JSON'a çeviriyoruz
        if bedenler_data:
            try:
                bedenler_list = json.loads(bedenler_data)
                for beden_data in bedenler_list:
                    beden = Beden.objects.get(id=beden_data['id'])
                    beden.numara = beden_data.get('numara', beden.numara)
                    beden.durum = beden_data.get('durum', beden.durum)
                    beden.save()
            except json.JSONDecodeError:
                raise serializers.ValidationError("Bedenler verisi geçersiz formatta.")

        # Eğer ozellikler verisi varsa, string formatında geldiyse JSON'a çeviriyoruz
        if ozellikler_data:
            try:
                ozellikler_list = json.loads(ozellikler_data)
                for ozellik_data in ozellikler_list:
                    ozellik = Ozellik.objects.get(id=ozellik_data['id'])
                    ozellik.name = ozellik_data.get('name', ozellik.name)
                    ozellik.durum = ozellik_data.get('durum', ozellik.durum)
                    ozellik.save()
            except json.JSONDecodeError:
                raise serializers.ValidationError("Özellikler verisi geçersiz formatta.")

        return instance

## ürünler panel tarafı için ürün detay serializers


class UrunlerAramaSerializer(serializers.ModelSerializer):
    urun_kategori = UrunGetKategoriSerializer()
    vitrin_kategori = UrunGetVitrinSerializer()


    class Meta:
        model = Urunler
        fields = ['id','urun_kategori', 'vitrin_kategori', 'baslik', 'slug', 'fiyat', 'kapak_fotografi','durum']


import json

class UrunlerCreateSerializer(serializers.ModelSerializer):
    urun_kategori = serializers.PrimaryKeyRelatedField(queryset=UrunKategori.objects.all(), required=False)
    vitrin_kategori = serializers.PrimaryKeyRelatedField(queryset=UrunVitrin.objects.all(), required=False)

    # Bedenler and Özellikler as JSON strings
    bedenler = serializers.CharField(required=False, allow_blank=True)
    ozellikler = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = Urunler
        fields = ['id','urun_kategori', 'vitrin_kategori', 'baslik', 'slug', 'fiyat', 'kapak_fotografi', 'aciklama', 'bedenler', 'ozellikler']

    def create(self, validated_data):
        # Extract and parse 'bedenler' and 'ozellikler' JSON strings
        bedenler_data = validated_data.pop('bedenler', None)
        ozellikler_data = validated_data.pop('ozellikler', None)

        try:
            # Parse JSON strings if provided
            bedenler_data = json.loads(bedenler_data) if bedenler_data else []
            ozellikler_data = json.loads(ozellikler_data) if ozellikler_data else []
        except json.JSONDecodeError:
            raise serializers.ValidationError({
                "detail": "Invalid JSON format for 'bedenler' or 'ozellikler'."
            })

        # Create the product
        urun = Urunler.objects.create(**validated_data)

        # Create 'bedenler' if data exists
        for beden in bedenler_data:
            Beden.objects.create(urun=urun, **beden)

        # Create 'ozellikler' if data exists
        for ozellik in ozellikler_data:
            Ozellik.objects.create(urun=urun, **ozellik)

        return urun





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


