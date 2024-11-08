from django.shortcuts import render

# Create your views here.
from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.generics import ListAPIView

from rest_framework import status


from django.utils.translation import gettext as _
from rest_framework.authtoken.models import Token
from rest_framework.status import (
    HTTP_200_OK,
)
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from rest_framework.response import Response

from rest_framework.authtoken.views import ObtainAuthToken
from django.db.models import F

from django.contrib.auth.models import User
from rest_framework.mixins import ListModelMixin
from rest_framework.generics import GenericAPIView

from rest_framework.authtoken.views import ObtainAuthToken
from .authentication import token_expire_handler



from rest_framework import viewsets
from .models import Menu, MenuItem,BaslikGorsel
from .serializers import MenuSerializer, MenuItemSerializer,UserSerializer


# ---- user ----


class CustomAuthToken(ObtainAuthToken):
    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        try:
            token = Token.objects.get(user=user)
            is_expired, token = token_expire_handler(token)
        except Token.DoesNotExist:
            token = Token.objects.create(user=user)
        return Response({'token': token.key})

class CheckToken(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        return Response({'message': 'Token is valid'})

class Logout(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        # Get the token of the user from the request
        try:
            token = request.auth
            # Delete the token to effectively log the user out
            Token.objects.filter(key=token).delete()
            return Response({"message": "Successfully logged out"}, status=status.HTTP_200_OK)
        except:
            return Response({"error": "Something went wrong"}, status=status.HTTP_400_BAD_REQUEST)


class UserInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, format=None):
        user = request.user
        serializer = UserSerializer(user)
        return Response(serializer.data, status=status.HTTP_200_OK)


# --- menu ---

class MenuViewSet(viewsets.ModelViewSet):
    queryset = Menu.objects.all()
    serializer_class = MenuSerializer
    pagination_class = None
    def create(self, request, *args, **kwargs):
        selected = request.data.get('selected', False)

        # Eğer yeni menü seçili ise, diğer seçili menüyü bul ve selected değerini False yap
        if selected:
            try:
                existing_selected_menu = Menu.objects.get(selected=True)
                existing_selected_menu.selected = False
                existing_selected_menu.save()
            except Menu.DoesNotExist:
                pass  # Hiç seçili menü yok, devam et

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def perform_update(self, serializer):
        # Yeni verilerden seçili değerini kontrol et
        selected = serializer.validated_data.get('selected', False)
        if selected:
            try:
                existing_selected_menu = Menu.objects.get(selected=True)
                if existing_selected_menu != serializer.instance:
                    # Güncellenecek menü, zaten seçili menü değilse
                    existing_selected_menu.selected = False
                    existing_selected_menu.save()
            except Menu.DoesNotExist:
                pass  # Hiç seçili menü yok, devam et

        serializer.save()

#class MenuItemViewSet(viewsets.ModelViewSet):
#    queryset = MenuItem.objects.all()
#    serializer_class = MenuItemSerializer

#    def retrieve(self, request, pk=None):
#        # Belirli bir menüye ait MenuItem nesnelerini getir
#        menu_items = MenuItem.objects.filter(menu_id=pk)
#        serializer = self.get_serializer(menu_items, many=True)
#       return Response(serializer.data)

from rest_framework import generics
from .models import MenuItem,UrunKategori
from .serializers import MenuItemSerializer


# tüm menü ögelerini getirir
class MenuItemListCreateView(generics.ListAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    pagination_class = None


# x menuye aıt menu ogelerini getir ve yeni öge üretir.
class MenuItemByMenuView(generics.ListCreateAPIView):
    serializer_class = MenuItemSerializer
    pagination_class = None

    def get_queryset(self):
        menu_id = self.kwargs.get('menu_id')
        return MenuItem.objects.filter(menu__id=menu_id)





# menu ogelerin her birinin tekil olarak detaylarını getir.
class MenuItemDetailView(generics.RetrieveUpdateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    pagination_class = None




from rest_framework.decorators import action

# seçili menünün ögeleri listele
class MenuSelectedItemViewSet(viewsets.ModelViewSet):
    queryset = MenuItem.objects.filter(menu__selected=True,is_removed=False)
    serializer_class = MenuItemSerializer
    pagination_class = None

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_active']:
            # 'list', 'retrieve' ve 'get_active' için herhangi bir permission gerekmez
            permission_classes = []
        else:
            # Diğer tüm action'lar için IsAuthenticated kullan
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


    @action(detail=False, methods=['get'])
    def get_active(self, request):
        active = MenuItem.objects.filter(menu__selected=True,durum=True, is_removed=False)
        page = self.paginate_queryset(active)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['patch'])
    def update_status(self, request):
        changes = request.data
        print(changes)
        for item_id, status in changes.items():
            try:
                item = MenuItem.objects.get(id=item_id)
                item.durum = status
                # Update UrunKategori if needed
                try:
                    urun_kategori = UrunKategori.objects.get(slug=item.slug)
                    urun_kategori.durum = status
                    urun_kategori.save()
                    Urunler.objects.filter(urun_kategori=urun_kategori).update(urun_kategori=None)
                    baslik_gorsel = BaslikGorsel.objects.get(slug=item.slug)
                    baslik_gorsel.durum = status
                    baslik_gorsel.save()

                except UrunKategori.DoesNotExist:
                    pass
                item.save()
            except MenuItem.DoesNotExist:
                return Response({'error': f'Item with id {item_id} does not exist.'}, status=404)

        return Response({'message': 'Items updated successfully.'})


# SLİDERS
from .models import Sliders
from .serializers import SlidersSerializer
from django.db.models import F


class SlidersViewSet(viewsets.ModelViewSet):
    queryset = Sliders.objects.filter(is_removed=False).order_by('-id')
    serializer_class = SlidersSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_active_masaustu', 'get_active_mobil']:
            # 'list', 'retrieve' ve 'get_active' için herhangi bir permission gerekmez
            permission_classes = []
        else:
            # Diğer tüm action'lar için IsAuthenticated kullan
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def bulk_soft_delete(self, request):
        ids = request.data.get('ids', [])
        # Güvenli bir şekilde int listesi oluştur
        ids = [int(id) for id in ids if id.isdigit()]
        # Belirtilen ID'lere sahip nesneleri soft delete işlemi ile güncelle
        Sliders.objects.filter(id__in=ids).update(is_removed=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def get_active_masaustu(self, request):
        active = Sliders.objects.filter(durum=True, is_removed=False,device="masaüstü").order_by('-id')

        # Varsayılan paginasyonu devre dışı bırak
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def get_active_mobil(self, request):
        active = Sliders.objects.filter(durum=True, is_removed=False, device="mobil").order_by('-id')

        # Varsayılan paginasyonu devre dışı bırak
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

    def create(self, request, *args, **kwargs):
        order = request.data.get('order', None)
        device = request.data.get('device', None)

        if order is not None and device is not None:
            order = int(order)
            if Sliders.objects.filter(order=order, device=device, is_removed=False).exists():
                self.adjust_order_for_new_slider(order,device)

        print(request.data)


        response = super().create(request, *args, **kwargs)

        return response

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        new_order = request.data.get('order', None)
        new_device = request.data.get('device', instance.device)

        if new_order is not None:
            new_order = int(new_order)
        else:
            new_order = instance.order


        if new_order != instance.order or new_device != instance.device:
            if new_device == instance.device:
                if new_order > instance.order:
                    self._shift_orders_up(new_order, instance.order, new_device, exclude_id=instance.pk)
                elif new_order < instance.order:
                    self._shift_orders_down(new_order, instance.order, new_device, exclude_id=instance.pk)

            else:
                if Sliders.objects.filter(order=new_order, device=new_device,
                                                is_removed=False).exists():
                    self.adjust_order_for_new_slider(new_order, new_device)

        return super().update(request, *args, partial=partial, **kwargs)


    def _shift_orders_up(self, new_order,old_order,new_device, exclude_id=None ):
        if not Sliders.objects.filter(is_removed=False, device=new_device, order=new_order).exists():
            return

        sliders = Sliders.objects.filter(is_removed=False,device=new_device).exclude(pk=exclude_id).order_by('-order')

        for slider in sliders:
            if old_order <= slider.order <= new_order:
                next_order = slider.order - 1
                slider.order = next_order

                if not Sliders.objects.filter(order=next_order,device=new_device,is_removed=False).exists():
                    slider.save()
                    break
                slider.save()

    def _shift_orders_down(self, new_order,old_order,new_device, exclude_id=None):
        if not Sliders.objects.filter(is_removed=False, device=new_device, order=new_order).exists():
            return
        sliders = Sliders.objects.filter(is_removed=False,device=new_device).exclude(pk=exclude_id).order_by('order')
        for slider in sliders:
            if old_order >= slider.order >= new_order:
                prev_order = slider.order + 1
                slider.order = prev_order

                if not Sliders.objects.filter(order=prev_order,device=new_device,is_removed=False).exists():
                    slider.save()
                    break
                slider.save()

    def adjust_order_for_new_slider(self, order,device):
            # Eğer bu order değerine sahip bir slider varsa, bu order ve sonrasındaki tüm slider'ların order değerlerini güncelle
        sliders = Sliders.objects.filter(order__gte=order, device=device, is_removed=False).order_by('order')

        if not sliders.exists():
            return

        for slider in sliders:
            next_order = slider.order + 1
            # Bir sonraki order değeri zaten mevcut mu, kontrol et
            if not Sliders.objects.filter(order=next_order,device=device, is_removed=False).exists():
                # Eğer bir sonraki order değeri mevcut değilse, mevcut slider'ı güncelle ve döngüden çık
                slider.order = next_order
                slider.save()
                break
            else:
                # Eğer bir sonraki order değeri mevcutsa, güncellemeye devam et
                slider.order = next_order
                slider.save()



# ÜRÜN Kategori

from rest_framework import permissions
from django_filters import rest_framework as filters

from .models import Urunler
from .serializers import UrunlerSerializer

from .models import UrunKategori
from .serializers import UrunKategoriSerializer
from django.db.models import Max


class UrunKategoriViewSet(viewsets.ModelViewSet):
    queryset = UrunKategori.objects.filter(is_removed=False).order_by('-id')
    serializer_class = UrunKategoriSerializer

    def get_permissions(self):
        # Eğer action 'list', 'retrieve' veya 'get_active' ise, herkese izin ver.
        if self.action in ['list', 'retrieve', 'get_active']:
            return [permissions.AllowAny()]
        # Diğer tüm durumlar için kullanıcının oturum açmış olması gerekir.
        return [permissions.IsAuthenticated()]

    @action(detail=False, methods=['post'])
    def bulk_soft_delete(self, request):
        ids = request.data.get('ids', [])
        # Güvenli bir şekilde int listesi oluştur
        ids = [int(id) for id in ids if id.isdigit()]
        # Belirtilen ID'lere sahip nesneleri soft delete işlemi ile güncelle
        UrunKategori.objects.filter(id__in=ids).update(is_removed=True)

        # İlgili Urunler nesnelerinin durumunu ve kategori bağlantısını güncelle
        Urunler.objects.filter(urun_kategori__id__in=ids).update(urun_kategori=None)

        # İlgili MenuItem nesnelerinin is_removed alanını güncelle
        kategori_sluglari = UrunKategori.objects.filter(id__in=ids).values_list('slug', flat=True)
        MenuItem.objects.filter(slug__in=kategori_sluglari, parent__title='Ürünlerimiz').update(is_removed=True)
        BaslikGorsel.objects.filter(slug__in=kategori_sluglari).update(is_removed=True)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def get_active(self, request):
        # durum=True ve is_removed=False olanları seç ve başlığa göre alfabetik sırala
        active = UrunKategori.objects.filter(durum=True, is_removed=False).order_by('id')
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

    ## burası zaten ön yüz için yazılmış silinmöiş ve aktif olmayan nesneleri döndürmemeyi sağlıyordu.
    # biz ek olarak diğerlerinden ayrı burada paginations'u kaldırdık. çünkü kullanıcı arayüzü tarafında
    # kategorinin tamamının listelenmesini istioruz.

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        # Güncelleme işleminden önce eski 'durum' değerini kaydet
        old_durum = instance.durum
        old_baslik = instance.baslik
        self.perform_update(serializer)
        new_baslik = serializer.validated_data.get('baslik', old_baslik)
        new_durum = serializer.validated_data.get('durum', old_durum)

        # Eğer 'durum' değişmişse ve yeni durum False ise ilgili Urunler nesnelerini güncelle
        if old_durum != new_durum and not new_durum:
            Urunler.objects.filter(urun_kategori=instance).update(urun_kategori=None)

        if old_baslik != new_baslik:
            self.update_related_menu_item_title(instance)

        # Durum değişikliği varsa ilgili MenuItem'i güncelle
        if old_durum != new_durum:
            self.update_related_menu_item(instance, new_durum)

        return Response(serializer.data)

    def update_related_menu_item_title(self, instance):
        try:
            menu_item = MenuItem.objects.get(slug=instance.slug)
            menu_item.title = instance.baslik
            menu_item.save()
        except MenuItem.DoesNotExist:
            pass

        try:
            baslik_gorsel = BaslikGorsel.objects.get(slug=instance.slug)
            baslik_gorsel.name = instance.baslik
            baslik_gorsel.save()
        except BaslikGorsel.DoesNotExist:
            pass

    def update_related_menu_item(self, instance, new_durum):
        # Ürün kategorisinin başlığı ile eşleşen ve 'Ürünlerimiz' başlıklı parent menüye bağlı MenuItem nesnesini bul
        menu_item = MenuItem.objects.get(slug=instance.slug)
        if menu_item:
            # Eğer bulunan menu item varsa ve durumu güncel durumdan farklıysa güncelle
            if menu_item.durum != new_durum:
                menu_item.durum = new_durum
                menu_item.save()

        baslik_gorsel = BaslikGorsel.objects.get(slug=instance.slug)
        if baslik_gorsel:
            # Eğer bulunan menu item varsa ve durumu güncel durumdan farklıysa güncelle
            if baslik_gorsel.durum != new_durum:
                baslik_gorsel.durum = new_durum
                baslik_gorsel.save()



    def perform_create(self, serializer):
        instance = serializer.save()
        self.create_related_menu_item(instance)

    def create_related_menu_item(self, instance):

        parent_menu_item = MenuItem.objects.get(slug='urunlerimiz')

        # Eğer 'Ürünlerimiz' başlıklı bir üst menü elemanı varsa, alt menü elemanını oluştur
        if parent_menu_item:
            # Menü öğelerinin sıralamasını belirlemek için bir sonraki sıra numarasını al
            next_order = MenuItem.objects.filter(parent=parent_menu_item).aggregate(Max('order'))['order__max'] or 0
            order = next_order + 1

            MenuItem.objects.create(
                title=instance.baslik,
                slug=instance.slug,
                url=f'/urunlerimiz?tab={instance.slug}',
                menu=parent_menu_item.menu,
                parent=parent_menu_item,
                durum=True,
                is_removed=False,
                order=order  # Sıralama numarası atanıyor
            )

            BaslikGorsel.objects.create(
                name=instance.baslik,
                slug=instance.slug,
            )



class UrunKategoriListView(ListModelMixin, GenericAPIView):
    queryset = UrunKategori.objects.filter(is_removed=False,durum=True).order_by('-id')
    serializer_class = UrunKategoriSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)




## ürün vitrin ##



from .models import UrunVitrin
from .serializers import UrunVitrinSerializer

class UrunVitrinViewSet(viewsets.ModelViewSet):
    queryset = UrunVitrin.objects.filter(is_removed=False).order_by('-id')
    serializer_class = UrunVitrinSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_active']:
            # 'list', 'retrieve' ve 'get_active' için herhangi bir permission gerekmez
            permission_classes = []
        else:
            # Diğer tüm action'lar için IsAuthenticated kullan
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def bulk_soft_delete(self, request):
        ids = request.data.get('ids', [])
        # Güvenli bir şekilde int listesi oluştur
        ids = [int(id) for id in ids if id.isdigit()]
        # Belirtilen ID'lere sahip nesneleri soft delete işlemi ile güncelle
        UrunVitrin.objects.filter(id__in=ids).update(is_removed=True)

        Urunler.objects.filter(vitrin_kategori__id__in=ids).update(vitrin_kategori=None)

        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def get_active(self, request):
        active = UrunVitrin.objects.filter(durum=True,is_removed=False).order_by('order')

        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

    ## burası zaten ön yüz için yazılmış silinmöiş ve aktif olmayan nesneleri döndürmemeyi sağlıyordu.
    # biz ek olarak diğerlerinden ayrı burada paginations'u kaldırdık. çünkü kullanıcı arayüzü tarafında
    # kategorinin tamamının listelenmesini istioruz.


    def create(self, request, *args, **kwargs):
        order = request.data.get('order', None)

        if order is not None:
            order = int(order)
            if UrunVitrin.objects.filter(order=order, is_removed=False).exists():
                self.adjust_order_for_new_slider(order)

        response = super().create(request, *args, **kwargs)

        return response


    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()

       ### sıra
        new_order = request.data.get('order', None)

        if new_order is not None:
            new_order = int(new_order)
            if new_order != instance.order:
                if UrunVitrin.objects.filter(order=new_order, is_removed=False).exists():
                    if new_order > instance.order:
                        self._shift_orders_up(new_order, old_order=instance.order, exclude_id=instance.pk)
                    else:
                        self._shift_orders_down(new_order, old_order=instance.order, exclude_id=instance.pk)
        ### -----


        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        old_durum = instance.durum
        self.perform_update(serializer)

        # Güncelleme sonrası durum değerini al
        new_durum = serializer.validated_data.get('durum', old_durum)

        # Eğer 'durum' değişmişse ve yeni durum False ise ilgili Urunler nesnelerini güncelle
        if old_durum != new_durum and not new_durum:
            Urunler.objects.filter(vitrin_kategori=instance).update(vitrin_kategori=None)

        return Response(serializer.data)

    def _shift_orders_up(self, new_order, old_order, exclude_id=None):
        sliders = UrunVitrin.objects.filter(is_removed=False).exclude(pk=exclude_id).order_by('-order')
        for slider in sliders:
            if old_order <= slider.order <= new_order:
                next_order = slider.order - 1
                slider.order = next_order

                if not UrunVitrin.objects.filter(order=next_order, is_removed=False).exists():
                    slider.save()
                    break
                slider.save()

    def _shift_orders_down(self, new_order, old_order, exclude_id=None):
        sliders = UrunVitrin.objects.filter(is_removed=False).exclude(pk=exclude_id).order_by('order')
        for slider in sliders:
            if old_order >= slider.order >= new_order:
                prev_order = slider.order + 1
                slider.order = prev_order

                if not UrunVitrin.objects.filter(order=prev_order, is_removed=False).exists():
                    slider.save()
                    break
                slider.save()

    def adjust_order_for_new_slider(self, order):
        if UrunVitrin.objects.filter(order=order, is_removed=False).exists():
            # Eğer bu order değerine sahip bir slider varsa, bu order ve sonrasındaki tüm slider'ların order değerlerini güncelle
            sliders = UrunVitrin.objects.filter(order__gte=order, is_removed=False).order_by('order')
            for slider in sliders:
                next_order = slider.order + 1
                # Bir sonraki order değeri zaten mevcut mu, kontrol et
                if not UrunVitrin.objects.filter(order=next_order, is_removed=False).exists():
                    # Eğer bir sonraki order değeri mevcut değilse, mevcut slider'ı güncelle ve döngüden çık
                    slider.order = next_order
                    slider.save()
                    break
                else:
                    # Eğer bir sonraki order değeri mevcutsa, güncellemeye devam et
                    slider.order = next_order
                    slider.save()


class UrunVitrinListView(ListModelMixin, GenericAPIView):
    queryset = UrunVitrin.objects.filter(is_removed=False,durum=True).order_by('-id')
    serializer_class = UrunVitrinSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



### bedenler ###


from .models import Beden
from .serializers import BedenSerializer


class BedenViewSet(viewsets.ModelViewSet):
    queryset = Beden.objects.all().order_by('id')
    serializer_class = BedenSerializer

    @action(detail=False, methods=['get'], url_path='urun/(?P<urun_id>\d+)')
    def bedenler_by_urun(self, request, urun_id=None):
        queryset = Beden.objects.filter(urun__id=urun_id).order_by('id')
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], url_path='urun/(?P<urun_id>\d+)/update-durum')
    def bedenler_durum_update(self, request, urun_id=None):
        bedens_list = request.data.get('list', [])


        updated_bedens = []

        for beden_data in bedens_list:
            beden_id = beden_data.get('id')
            yeni_durum = beden_data.get('durum')

            try:
                beden = Beden.objects.get(id=beden_id, urun_id=urun_id)
                if beden.durum != yeni_durum:
                    beden.durum = yeni_durum
                    beden.save()
                    updated_bedens.append(beden_id)
            except Beden.DoesNotExist:
                return Response({'error': f'Beden with id {beden_id} not found for Urun {urun_id}.'},
                                status=status.HTTP_404_NOT_FOUND)

        return Response({'success': 'Beden durumları güncellendi.', 'updated_bedens': updated_bedens},
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='urun/(?P<urun_id>\d+)/create')
    def beden_create_toplu(self, request, urun_id=None):
        try:
            bedens_list = request.data.get('list', [])
            urun = Urunler.objects.get(id=urun_id)

            for beden_data in bedens_list:
                # Create Beden object for each item in bedens_list
                Beden.objects.create(
                    urun=urun,
                    numara=beden_data.get('numara'),
                    durum=beden_data.get('durum', False)  # Default value if durum is not provided
                )

            return Response({'message': 'Beden objects created successfully'}, status=status.HTTP_201_CREATED)

        except Urunler.DoesNotExist:
            return Response({'error': 'Urunler object does not exist'}, status=status.HTTP_404_NOT_FOUND)

        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)




#### urunler ###


class UrunlerFilter(filters.FilterSet):
    kategori = filters.CharFilter(field_name='urun_kategori__slug', method='filter_kategori')
    vitrin_kategori = filters.NumberFilter(method='filter_vitrin_kategori')

    def filter_kategori(self, queryset, name, value):
        # Kategoriye göre filtreleme yaparken, aynı zamanda durum=True koşulunu da uygula
        return queryset.filter(**{name: value, 'durum': True})

    def filter_vitrin_kategori(self, queryset, name, value):
        # Vitrin kategorisine ve durum=True koşuluna göre filtreleme yap
        return queryset.filter(**{name: value, 'durum': True})

    class Meta:
        model = Urunler
        fields = ['kategori', 'vitrin_kategori']


class UrunlerViewSet(viewsets.ModelViewSet):
    queryset = Urunler.objects.filter(is_removed=False).order_by('-id').select_related('urun_kategori','vitrin_kategori')
    serializer_class = UrunlerSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = UrunlerFilter

    def get_permissions(self):
        # Eğer metot GET ise ya da 'kategori' sorgu parametresi varsa, herkese izin ver (AllowAny).
        if self.request.method == 'GET' or self.request.query_params.get('kategori') is not None:
            permission_classes = [permissions.AllowAny]
        else:
            # Diğer tüm istekler için kullanıcının oturum açmış olması gerekiyor (IsAuthenticated).
            permission_classes = [permissions.IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def bulk_soft_delete(self, request):
        ids = request.data.get('ids', [])
        # Güvenli bir şekilde int listesi oluştur
        ids = [int(id) for id in ids if id.isdigit()]
        # Belirtilen ID'lere sahip nesneleri soft delete işlemi ile güncelle
        Urunler.objects.filter(id__in=ids).update(is_removed=True)


        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def get_active(self, request):
        active = Urunler.objects.filter(durum=True,is_removed=False).order_by('-id').select_related('urun_kategori','vitrin_kategori')
        page = self.paginate_queryset(active)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)




class FotoGaleriListView(ListModelMixin, GenericAPIView):
    queryset = Urunler.objects.filter(is_removed=False, durum=True).order_by('-id')
    serializer_class = UrunlerSerializer
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)



## IMAGE

from .models import Image
from .serializers import ImageSerializer

class ImageFilter(filters.FilterSet):
    kategori = filters.NumberFilter(field_name='urun__id')  # URL'de kategori olarak geçecek

    class Meta:
        model = Image
        fields = ['kategori']
class ImageViewSet(viewsets.ModelViewSet):
    queryset = Image.objects.filter(is_removed=False).select_related('urun').order_by('-id')
    serializer_class = ImageSerializer

    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ImageFilter
    pagination_class = None

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            permission_classes = []
        else:
            # Diğer tüm action'lar için IsAuthenticated kullan
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def bulk_soft_delete(self, request):
        ids = request.data.get('ids', [])
        # Güvenli bir şekilde int listesi oluştur
        ids = [int(id) for id in ids if id.isdigit()]
        # Belirtilen ID'lere sahip nesneleri soft delete işlemi ile güncelle
        Image.objects.filter(id__in=ids).update(is_removed=True)
        return Response(status=status.HTTP_204_NO_CONTENT)







#medya


from .models import SMedya
from .serializers import MedyaSerializer

class MedyaViewSet(viewsets.ModelViewSet):
    queryset = SMedya.objects.all().order_by('id')
    serializer_class = MedyaSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # 'list', 'retrieve' ve 'get_active' için herhangi bir permission gerekmez
            permission_classes = []
        else:
            # Diğer tüm action'lar için IsAuthenticated kullan
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]




# REFERANSLAR

from .models import References
from .serializers import ReferencesSerializer


class ReferencesViewSet(viewsets.ModelViewSet):
    queryset = References.objects.filter(is_removed=False).order_by('-id')
    serializer_class = ReferencesSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_active']:
            # 'list', 'retrieve' ve 'get_active' için herhangi bir permission gerekmez
            permission_classes = []
        else:
            # Diğer tüm action'lar için IsAuthenticated kullan
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def bulk_soft_delete(self, request):
        ids = request.data.get('ids', [])
        # Güvenli bir şekilde int listesi oluştur
        ids = [int(id) for id in ids if id.isdigit()]
        # Belirtilen ID'lere sahip nesneleri soft delete işlemi ile güncelle
        References.objects.filter(id__in=ids).update(is_removed=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def get_active(self, request):
        active = References.objects.filter(durum=True, is_removed=False).order_by('-id').select_related('urun_kategori',
                                                                                                     'vitrin_kategori')
        page = self.paginate_queryset(active)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)

        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)



# HIZLI LİNKLER

from .models import HizliLinkler
from .serializers import HizliLinklerSerializer


class HizliLinklerViewSet(viewsets.ModelViewSet):
    queryset = HizliLinkler.objects.filter(is_removed=False).order_by('-id')
    serializer_class = HizliLinklerSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_active']:
            # 'list', 'retrieve' ve 'get_active' için herhangi bir permission gerekmez
            permission_classes = []
        else:
            # Diğer tüm action'lar için IsAuthenticated kullan
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def bulk_soft_delete(self, request):
        ids = request.data.get('ids', [])
        # Güvenli bir şekilde int listesi oluştur
        ids = [int(id) for id in ids if id.isdigit()]
        # Belirtilen ID'lere sahip nesneleri soft delete işlemi ile güncelle
        HizliLinkler.objects.filter(id__in=ids).update(is_removed=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def get_active(self, request):
        active = HizliLinkler.objects.filter(durum=True, is_removed=False).order_by('id')

        # Varsayılan paginasyonu devre dışı bırak
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)


#iletişim


from .models import Contact
from .serializers import ContactSerializer

class ContactViewSet(viewsets.ModelViewSet):
    queryset = Contact.objects.all().order_by('id')
    serializer_class = ContactSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # 'list', 'retrieve' ve 'get_active' için herhangi bir permission gerekmez
            permission_classes = []
        else:
            # Diğer tüm action'lar için IsAuthenticated kullan
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]



from .models import Hakkimizda
from .serializers import HakkimizdaSerializer

# hakkımızda

class HakkimizdaViewSet(viewsets.ModelViewSet):
    queryset = Hakkimizda.objects.all().order_by('id')
    serializer_class = HakkimizdaSerializer
    def get_permissions(self):
        if self.action in ['list', 'retrieve']:
            # 'list', 'retrieve' için herhangi bir permission gerekmez
            permission_classes = []
        else:
            # Diğer tüm action'lar için IsAuthenticated kullan
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]


# BAŞLIK GÖRSEL

from .models import BaslikGorsel
from .serializers import BalikGorselSerializer



class BalikGorselViewSet(viewsets.ModelViewSet):
    queryset = BaslikGorsel.objects.filter(is_removed=False).order_by('-id')
    serializer_class = BalikGorselSerializer

    def get_permissions(self):
        if self.action in ['list', 'retrieve', 'get_active','get_gorsel']:
            # 'list', 'retrieve' ve 'get_active' için herhangi bir permission gerekmez
            permission_classes = []
        else:
            # Diğer tüm action'lar için IsAuthenticated kullan
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

    @action(detail=False, methods=['post'])
    def bulk_soft_delete(self, request):
        ids = request.data.get('ids', [])
        # Güvenli bir şekilde int listesi oluştur
        ids = [int(id) for id in ids if id.isdigit()]
        # Belirtilen ID'lere sahip nesneleri soft delete işlemi ile güncelle
        BaslikGorsel.objects.filter(id__in=ids).update(is_removed=True)
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=False, methods=['get'])
    def get_active(self, request):
        active = BaslikGorsel.objects.filter(durum=True, is_removed=False).order_by('-id')

        # Varsayılan paginasyonu devre dışı bırak
        serializer = self.get_serializer(active, many=True)
        return Response(serializer.data)

    @action(detail=False, methods=['get'], url_path='get-by-name/(?P<slug>.+)')
    def get_gorsel(self, request, slug):
        # İsmi verilen ve aktif durumda olan görselleri filtrele
        images = BaslikGorsel.objects.filter(slug=slug, durum=True, is_removed=False).order_by('-id')

        if images.exists():
            # İlk veriyi al
            image = images.first()  # veya images.last()

            serializer = self.get_serializer(image)
            return Response(serializer.data)
        else:
            # Veri bulunamadığında boş bir liste dön
            return Response([], status=status.HTTP_200_OK)


class CountViewSet(viewsets.ViewSet):
    permission_classes = [IsAuthenticated]

    def list(self, request):
        urunler_count = Urunler.objects.filter(is_removed=False, durum=True).count()
        urun_kategori_count = UrunKategori.objects.filter(is_removed=False, durum=True).count()
        references_count = References.objects.filter(is_removed=False, durum=True).count()

        data = {
            'urun_adedi': urunler_count,
            'urun_kategori_adedi': urun_kategori_count,
            'referanslar_adedi': references_count,
        }

        return Response(data)
