import json
import re
from django.shortcuts import render,redirect
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AddressSerializers
from .models import PanelMaster, SpatialPolygon
from django.views.decorators.csrf import csrf_exempt
from django.db import connection
cursor = connection.cursor()
from django.contrib.gis.geos.polygon import Polygon
# Create your views here.


class AddressViewSet(APIView):

    def post(self, request):
        print(request.data)
        serilalizer = AddressSerializers(data=request.data, many=True)
        if serilalizer.is_valid():
            serilalizer.save()
            return Response({"result": "success", "data": serilalizer.data,
                             "status": status.HTTP_200_OK})
        else:
            return Response({"result": "error", "data": serilalizer.errors,
                             "status": status.HTTP_400_BAD_REQUEST})


class AddressDetailsView(APIView):

    def get(self, request):
        item = PanelMaster.objects.filter(postal_code=request.GET['post_code'])
        serializer = AddressSerializers(item, many=True)
        if item:
            return Response({"result": "success",
                             "data": list(serializer.data),
                             "status": status.HTTP_200_OK})
        elif not item:
            items = PanelMaster.objects.filter(status='Active')[:50]
            serializer = AddressSerializers(items, many=True)
            if items:
                return Response({"result": "success",
                                 "data": list(serializer.data),
                                 "status": status.HTTP_200_OK})
            else:
                return Response({"result": "Data Not founded"})
        else:
            return Response({"result": "Data Not founded"})


def create_address_view(request):
    return render(request, 'adam/create_address.html')


def view_address(request):
    if request.user.is_authenticated:
        address_data = []
        query = '''select panel.panel_no,panel_st.player_no,panel.latitude,panel.longitude,panel.market_name,
                    panel_st.submarket,panel_st.media_type,panel_st.unit_type,
                    panel.status,panel_st.description,panel_st.code,
                    panel_st.city,panel_st.site,panel_st.wk4_imp,panel_st.media_type,
                    translate(panel_st.player_no,panel_st.code||'-','') as panel_st_panel_code
                    from adam_panelstaticdetails panel_st
                    join adam_panelmaster panel
                    on panel.panel_no = translate(panel_st.player_no,panel_st.code||'-','') limit 500 
                '''
        cursor.execute(query)
        if (cursor.rowcount > 0):
            for row in cursor.fetchall():
                record = {}
                record['panel_no'] = row[0]
                record['player_no'] = row[1]
                record['market_name'] = row[4]
                record['longitude'] = row[3]
                record['latitude'] = row[2]
                record['description'] = row[9]
                record['city'] = row[11]
                record['media_type'] = row[6]
                record['sub_market'] = row[5]
                record['unit_type'] = row[7]
                record['wk4_imp'] = row[13]

                address_data.append(record)

        # print(address_data)
        context = {
                    'user_id': request.user.id,
                    'address_data': address_data
                }

        return render(request, 'adam/view_address.html', context)
    return redirect('login')


def find_address(request):
    return render(request, 'adam/find_address.html')


@csrf_exempt
def create_address(request):
    if request.method == 'POST' and request.is_ajax():
        obj = PanelMaster()
        obj.address_title = request.POST.get('address_title')
        obj.address_type = request.POST.get('address_type')
        obj.address_line1 = request.POST.get('address_line1')
        obj.address_line2 = request.POST.get('address_line2')
        obj.city = request.POST.get('city')
        obj.state = request.POST.get('state')
        obj.country = request.POST.get('country')
        obj.latitude = request.POST.get('latitude')
        obj.longitude = request.POST.get('longitude')
        obj.save()
        # serilalizer = AddressSerializers(data=request.POST)
        # if serilalizer.is_valid():
        #      serilalizer.save()
        #      print("saved")
        # else:
        #      print("not valid")
        return HttpResponse(json.dumps({'status': "success"}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'status': "bad request"}), content_type="application/json")


@csrf_exempt
def check_area(request):
    if request.method == 'POST' and request.is_ajax():
        # res = Polygon([[(-81.27058013661991, 35.294380959284894), (-81.19077879693572, 35.32694110417019), (-81.13713456303682, 35.30306494604871), (-81.2262460590176, 35.28026749345226)]])
        # print("*************", res)
        # cods = request.POST.get('cods')
        # min_lng = request.POST.get('min_lng')
        # max_lng = request.POST.get('max_lng')
        # min_lat = request.POST.get('min_lat')
        # max_lat = request.POST.get('max_lat')
        # print(min_lng, max_lng)
        # result = PanelMaster.objects.filter(longitude__range=(min_lng, max_lng)
        #                                 # latitude__range=(min_lat, max_lat)
        #                                 ).values('longitude', 'latitude', 'city', 'state', 'country')
        # # print(list(result))
        # data = [{'longitude': '-79.955272', 'latitude': '32.837121', 'panel': '10710', 'market': 'charleston',
        #          'mediatype': 'Bulletin'},
        #         {'longitude': '-79.978316', 'latitude': '32.851848', 'panel': '11520', 'market': 'charleston',
        #          'mediatype': 'Poster'},
        #         {'longitude': '-79.986786', 'latitude': '32.847946', 'panel': 'P3716', 'market': 'charleston',
        #          'mediatype': 'Poster'},
        #         {'longitude': '-79.967356', 'latitude': '32.841073', 'panel': '1245', 'market': 'charleston',
        #          'mediatype': 'Bulletin'},
        #         {'longitude': '-79.944102', 'latitude': '32.797972', 'panel': '1012', 'market': 'charleston',
        #         'mediatype': 'Bulletin'}]
        cods = request.POST.get('cods')
        cods = json.loads(cods)
        # geo_polygon = Polygon(( (0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0) ))

        points = tuple((c[0], c[1]) for c in cods) + ((cods[0][0], cods[0][1]),)
        print(points)
        # geo_polygon = Polygon((
        #     (cods[0][0], cods[0][1]),
        #     (cods[1][0], cods[1][1]),
        #     (cods[2][0], cods[2][1]),
        #     (cods[3][0], cods[3][1]),
        #     (cods[4][0], cods[4][1]),
        #     (cods[5][0], cods[5][1]),
        #     (cods[0][0], cods[0][1])
        # ), srid=4326)
        geo_polygon = Polygon(points, srid=4326)
        poly = SpatialPolygon.objects.create(poly=geo_polygon)
        poly.save()
        # filter = geo_polygon.within(SpatialPanel.objects.all())
        # query = SpatialPanel.objects.filter(points__contains=geo_polygon)
        # query = SpatialPanel.objects.all()
        query = '''SELECT ST_X(point.points) AS x,
                            ST_Y(point.points) AS y,
                            ST_AsText(point.points) AS xy, 
                            point.panelmaster_id AS id
                            FROM public."adam_spatialpoint" point, public."adam_spatialpolygon" polygon
                            WHERE ST_Contains(polygon.poly, point.points) and polygon.id = {}
                        '''.format(poly.id)
        cursor.execute(query)

        res = list()
        lng = list()
        lat = list()
        panel_id = list()
        for q in cursor.fetchall():
            co = dict()
            co['longitude'] = q[0]
            co['latitude'] = q[1]
            res.append(co)
            lng.append(q[0])
            lat.append(q[1])
            panel_id.append(q[3])
        # print(panel_id)
        # lng = lng[1:5]
        # lat = lat[1:5]
        # str1 = ','.join(str(e) for e in lng)
        # str2 = ','.join(str(e) for e in lat)
        pid = ','.join(str(e) for e in panel_id)
        query = '''select panel.panel_no,panel_st.player_no,panel.latitude,panel.longitude,panel.market_name,
                            panel_st.submarket,panel_st.media_type,panel_st.unit_type,
                            panel.status,panel_st.description,panel_st.code,
                            panel_st.city,panel_st.site,panel_st.wk4_imp,panel_st.media_type,
                            translate(panel_st.player_no,panel_st.code||'-','') as panel_st_panel_code,
                            panel_st.installed_date_str
                            from adam_panelstaticdetails panel_st
                            join adam_panelmaster panel
                            on panel.panel_no = translate(panel_st.player_no,panel_st.code||'-','')
                            and panel.id in (
                            select unnest(string_to_array('{}', ',')):: numeric)
                        '''.format(pid)
        cursor.execute(query)
        address_data = []
        if (cursor.rowcount > 0):
            count = cursor.rowcount
            for row in cursor.fetchall():
                record = {}
                record['panel_no'] = row[0]
                record['player_no'] = row[1]
                record['market_name'] = row[4]
                record['longitude'] = row[3]
                record['latitude'] = row[2]
                record['description'] = row[9]
                record['city'] = row[11]
                record['media_type'] = row[6]
                record['wk4_imp'] = row[13]
                record['installed_date'] = row[16]

                address_data.append(record)
        else:
            count = 0
        return HttpResponse(json.dumps({'status': "success", "data": list(address_data), "count": count}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'status': "bad request"}), content_type="application/json")


@csrf_exempt
def view_data(request):
    if request.method == 'POST' and request.is_ajax():
        player_no = request.POST.get('player')

        query = '''select sales_person,contract_no,contract_type,sub_contract_type,advertiser,panel_no,
                segment,segment_name,spots,value,from_date_str,to_date_str 
                from adam_reservation where player_no = '{}' order by value desc
                '''.format(player_no)
        # print(query)
        cursor.execute(query)
        view_data = []
        if(cursor.rowcount > 0):
            count = cursor.rowcount
            for row in cursor.fetchall():
                record = {}
                record['sales_person'] = row[0]
                record['contract_no'] = row[1]
                record['contract_type'] = row[2]
                record['sub_contract_type'] = row[3]
                record['advertiser'] = row[4]
                record['panel_no'] = row[5]
                record['segment'] = row[6]
                record['segment_name'] = row[7]
                record['spots'] = row[8]
                record['value'] = row[9]
                record['from_date_str'] = row[10]
                record['to_date_str'] = row[11]
                view_data.append(record)
        else:
            count = 0

        return HttpResponse(json.dumps({'status': "success", "data": list(view_data), "count": count}),
                            content_type="application/json")