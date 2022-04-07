from django.contrib import admin
from django.contrib.gis import admin as gis_admin
from .models import PanelMaster, PanelStaticDetails, PanelPlayerDetails,PanelDocument,\
    SpatialPoint, SpatialPolygon, MarketMaster, Reservation, RegionMaster
from django_object_actions import DjangoObjectActions
from django.core.exceptions import ValidationError
from .adam import excel_to_csv
from django.conf import settings
import os

class PanelMasterAdmin(admin.ModelAdmin):
    readonly_fields = ['installed_date_str','retirement_date_str']
    list_display = ('panel_no','market_name','latitude','longitude','status','installed_date_str','retirement_date_str')
    search_fields = ['panel_no','market_name','latitude','longitude','status','installed_date_str','retirement_date_str']

    fieldsets = (
        ('', {'fields': ('panel_no','market_name','latitude', 'longitude', 'installed_date_str', 'retirement_date_str', 'status')}),
        ('Other Info', {'fields': ('address_title','address_type','address_line1','address_line2','city','state','country','postal_code'), 'classes': ['form-row-6columns']}),
    )

admin.site.register(PanelMaster, PanelMasterAdmin)

class PanelStaticDetailsAdmin(admin.ModelAdmin):
    readonly_fields = ['installed_date_str','retirement_date_str']
    list_display = ('player_no','panel_no','installed_date_str','retirement_date_str','code','site','city','wk4_imp','size','submarket','description','media_type','unit_type',)
    search_fields = ['player_no','panel_no','installed_date_str','retirement_date_str','code','site','city','wk4_imp','size','submarket','description','media_type','unit_type']
    fieldsets = ( ('', {'fields': ('player_no','panel_no','installed_date_str','retirement_date_str','code','site','city','wk4_imp','size','submarket','description','media_type','unit_type',), 'classes': ['wide']}),)
admin.site.register(PanelStaticDetails, PanelStaticDetailsAdmin)

class PanelPlayerDetailsAdmin(admin.ModelAdmin):
    readonly_fields = ['installed_date_str','retirement_date_str']
    list_display = ('player_no','panel_no','installed_date_str','retirement_date_str','code','site','city','wk4_imp','size','submarket','description','sales_spot',)
    search_fields = ['player_no','panel_no','installed_date_str','retirement_date_str','code','site','city','wk4_imp','size','submarket','description','sales_spot']
    fieldsets = ( ('', {'fields': ('player_no','panel_no','installed_date_str','retirement_date_str','code','site','city','wk4_imp','size','submarket','description','sales_spot',), 'classes': ['wide']}),)
admin.site.register(PanelPlayerDetails, PanelPlayerDetailsAdmin)


class PanelDocumentAdmin(admin.ModelAdmin):
    fieldsets = ( ('Basic Info', {'fields': ('name','document',), 'classes': ['wide']}),)

    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions

    def get_readonly_fields(self, request, obj=None):
        # make all fields readonly
        readonly_fields = self.readonly_fields
        if obj:
            readonly_fields = list(
                set([field.name for field in self.opts.local_fields] +
                    [field.name for field in self.opts.local_many_to_many]))
        return readonly_fields

    list_display = ("name", "uploaded_at",)
    search_fields = ['name']
    
    def change_view(self, request, object_id, extra_context=None):
        ''' customize add/edit form '''
        if object_id:
            extra_context = extra_context or {}
            extra_context['show_save_and_add_another'] = False
            extra_context['show_save_and_continue'] = False
            extra_context['show_save'] = False
            extra_context['show_delete'] = False
        return super(PanelDocumentAdmin, self).change_view(request, object_id, extra_context=extra_context)

    # def formfield_for_foreignkey(self, db_field, request, **kwargs):
    #     doc_obj = Document.objects.values('calculator_id').distinct()
    #     doc_ref_cal_rec = doc_obj and list(doc_obj) or []
    #     doc_ref_cal_rec = doc_obj and list(map(lambda x: x.get('calculator_id',False), doc_ref_cal_rec)) or []
    #     doc_ref_cal_rec = doc_ref_cal_rec and list(filter(lambda x: x != False, doc_ref_cal_rec)) or []
    #     if db_field.name == "calculator_id":
    #         filter_obj = False
    #         filters = {'active': True}
    #         filter_obj = CalculatorMaster.objects.filter(**filters)
    #         kwargs["queryset"] = filter_obj
    #     return super().formfield_for_foreignkey(db_field, request, **kwargs)

    def export_csv(self, request, obj):
        if settings.DATA_FILE_DIR and obj.document:
            excelfile = settings.DATA_FILE_DIR + obj.document.url
            excelfile = excelfile.replace("/", "\\")
            if excelfile and os.path.exists(excelfile):
                excel_to_csv(excelfile,calculator_directory=None)
                # import_csv_database(calculator_id=obj.calculator_id.id,calculator_directory=obj.calculator_id.directory_name)
                # prepare_csv_import_journal(calculator_id=obj.calculator_id.id,calculator_directory=obj.calculator_id.directory_name)

    # def import_journal(self, request, obj):
    #     if obj.calculator_id:
    #         import_csv_database(calculator_id=obj.calculator_id.id,calculator_directory=obj.calculator_id.directory_name)
    #         prepare_csv_import_journal(calculator_id=obj.calculator_id.id,calculator_directory=obj.calculator_id.directory_name)

    change_actions = (
        "export_csv"
    )

admin.site.register(PanelDocument, PanelDocumentAdmin)


class SecureOSM(gis_admin.GeoModelAdmin):
    openlayers_url = 'https://cdnjs.cloudflare.com/ajax/libs/openlayers/2.13.1/OpenLayers.js'
# @gis_admin.register(SpatialPoint)
# class SpatialPointAdmin(gis_admin.OSMGeoAdmin):
#     # gis_widget = OSMWidget
#     list_display = ('points', 'panelmaster_id')
gis_admin.site.register(SpatialPoint, SecureOSM)


class MarketMasterAdmin(admin.ModelAdmin):
    list_display = ('code','market',)
    search_fields = ['code','market']
admin.site.register(MarketMaster, MarketMasterAdmin)


class RegionMasterAdmin(admin.ModelAdmin):
    list_display = ('code','city',)
    search_fields = ['code','city']
admin.site.register(RegionMaster, RegionMasterAdmin)


class ReservationAdmin(admin.ModelAdmin):
    list_display = ('from_date_str','to_date_str','sales_person','contract_type','sub_contract_type', 'advertiser','panel_no','segment_name','weekdays','spots', 'value',)
    search_fields = ['sales_person','contract_type','sub_contract_type','advertiser','segment_name']


admin.site.register(Reservation, ReservationAdmin)
