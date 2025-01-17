import json
import re
from django.shortcuts import render,redirect
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers import AddressSerializers
from .models import PanelMaster, SpatialPolygon, RegionMaster, MarketMaster
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
        region_city = RegionMaster.objects.all()
        market_value = MarketMaster.objects.all()
        # print(list(region_city))
        context = {
                    'user_id': request.user.id,
                    'address_data': address_data,
                    'region_city': list(region_city),
                    'market_value': list(market_value)
                }

        return render(request, 'adam/view_address.html', context)
    return redirect('login')


@csrf_exempt
def view_panel_details(request):
    if request.method == 'POST' and request.is_ajax():
        city = request.POST.get('city')
        market = request.POST.get('market')
        market_val = market.lower()
        if market_val != 'all':
            market_qry = "and panel.market_name = '{}'".format(market_val)
        else:
            market_qry = ''

        address_data = []
        # query = '''select panel.panel_no,panel_st.player_no,panel.latitude,panel.longitude,panel.market_name,
        #                     panel_st.submarket,panel_st.media_type,panel_st.unit_type,
        #                     panel.status,panel_st.description,panel_st.code,
        #                     panel_st.city,panel_st.site,panel_st.wk4_imp,panel_st.media_type,
        #                     translate(panel_st.player_no,panel_st.code||'-','') as panel_st_panel_code
        #                     from adam_panelstaticdetails panel_st
        #                     join adam_panelmaster panel
        #                     --on panel.panel_no = translate(panel_st.player_no,panel_st.code||'-','')
        #                     on panel.panel_no = panel_st.panel_no
        #                     and panel_st.city='{}'
        #                 '''.format(city)
        query = '''select panel.panel_no,panel_st.player_no,panel.latitude,panel.longitude,panel.market_name,
                            panel_st.submarket,panel_st.media_type,panel_st.unit_type,
                            panel.status,panel_st.description,panel_st.code,
                            panel_st.city,panel_st.site,panel_st.wk4_imp,panel_st.media_type,
                            translate(panel_st.player_no,panel_st.code||'-','') as panel_st_panel_code,
                            panel_ply.city,panel_ply.site,panel_ply.wk4_imp,panel_ply.player_no,
                            panel_ply.description,panel_ply.submarket
                            from adam_panelmaster panel
                            left join adam_panelstaticdetails panel_st
                            on panel.panel_no = panel_st.panel_no
                            left join adam_panelplayerdetails panel_ply
                            on panel.panel_no = panel_ply.panel_no
                            where (panel_st.city='{}' or panel_ply.city='{}')
                            '''.format(city, city)
        query = query + "" + market_qry
        cursor.execute(query)
        if (cursor.rowcount > 0):
            count = cursor.rowcount
            for row in cursor.fetchall():
                record = {}
                record['panel_no'] = row[0]
                record['player_no'] = row[1] if row[1] else row[19]
                record['market_name'] = row[4]
                record['longitude'] = row[3]
                record['latitude'] = row[2]
                record['description'] = row[9] if row[9] else row[20]
                record['city'] = row[11] if row[11] else row[16]
                record['media_type'] = row[6] if row[6] else 'others'
                record['sub_market'] = row[5] if row[5] else row[21]
                record['unit_type'] = row[7] if row[7] else 'others'
                record['wk4_imp'] = row[13] if row[13] else row[18]

                address_data.append(record)
        else:
            count = 0
        return HttpResponse(json.dumps({'status': "success", "data": list(address_data), "count": count}),
                            content_type="application/json")


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
        return HttpResponse(json.dumps({'status': "success"}), content_type="application/json")
    else:
        return HttpResponse(json.dumps({'status': "bad request"}), content_type="application/json")


@csrf_exempt
def check_area(request):
    if request.method == 'POST' and request.is_ajax():

        cods = request.POST.get('cods')
        cods = json.loads(cods)
        # geo_polygon = Polygon(( (0.0, 0.0), (0.0, 50.0), (50.0, 50.0), (50.0, 0.0), (0.0, 0.0) ))

        points = tuple((c[0], c[1]) for c in cods) + ((cods[0][0], cods[0][1]),)
        # print(points)
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
        # str1 = ','.join(str(e) for e in lng)
        # str2 = ','.join(str(e) for e in lat)
        pid = ','.join(str(e) for e in panel_id)
        # query = '''select panel.panel_no,panel_st.player_no,panel.latitude,panel.longitude,panel.market_name,
        #                     panel_st.submarket,panel_st.media_type,panel_st.unit_type,
        #                     panel.status,panel_st.description,panel_st.code,
        #                     panel_st.city,panel_st.site,panel_st.wk4_imp,panel_st.media_type,
        #                     translate(panel_st.player_no,panel_st.code||'-','') as panel_st_panel_code,
        #                     panel_st.installed_date_str
        #                     from adam_panelstaticdetails panel_st
        #                     join adam_panelmaster panel
        #                     --on panel.panel_no = translate(panel_st.player_no,panel_st.code||'-','')
        #                     on panel.panel_no = panel_st.panel_no
        #                     and panel.id in (
        #                     select unnest(string_to_array('{}', ',')):: numeric)
        #                 '''.format(pid)
        query = '''select panel.panel_no,panel_st.player_no,panel.latitude,panel.longitude,panel.market_name,
                                    panel_st.submarket,panel_st.media_type,panel_st.unit_type,
                                    panel.status,panel_st.description,panel_st.code,
                                    panel_st.city,panel_st.site,panel_st.wk4_imp,panel_st.media_type,
                                    translate(panel_st.player_no,panel_st.code||'-','') as panel_st_panel_code,
                                    panel_st.installed_date_str,
                                    panel_ply.city,panel_ply.site,panel_ply.wk4_imp,panel_ply.player_no,
                                    panel_ply.description,panel_ply.submarket
                                    from adam_panelmaster panel
                                    left join adam_panelstaticdetails panel_st
                                    on panel.panel_no = panel_st.panel_no
                                    left join adam_panelplayerdetails panel_ply
                                    on panel.panel_no = panel_ply.panel_no
                                    --on panel.panel_no = translate(panel_st.player_no,panel_st.code||'-','')
                                    where panel.id in (
                                    select unnest(string_to_array('{}', ',')):: numeric)
                                '''.format(pid)
        cursor.execute(query)
        address_data = []
        if (cursor.rowcount > 0):
            count = cursor.rowcount
            for row in cursor.fetchall():
                record = {}
                record['panel_no'] = row[0]
                record['player_no'] = row[1] if row[1] else row[20]
                record['market_name'] = row[4]
                record['longitude'] = row[3]
                record['latitude'] = row[2]
                record['description'] = row[9] if row[9] else row[21]
                record['city'] = row[11] if row[11] else row[17]
                record['media_type'] = row[6] if row[6] else 'others'
                record['wk4_imp'] = row[13] if row[13] else row[19]
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