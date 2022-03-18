from django.db import models
import os
import datetime
from django.conf import settings
from .adam import *
# Create your models here.

class PanelAbstract(models.Model):

    panel_no = models.CharField(max_length=50, verbose_name=u"Panel Number", help_text=u"Panel Number", null=True, blank=True)
    installed_date_str = models.CharField(max_length=50,verbose_name=u"Installed Date", editable=False, null=True, blank=True)
    retirement_date_str = models.CharField(max_length=50,verbose_name=u"Retirement Date", editable=False, null=True, blank=True)
    installed_date = models.DateField(verbose_name=u"Installed Date", null=True, blank=True)
    retirement_date = models.DateField(verbose_name=u"Retirement Date", null=True, blank=True)

    class Meta:
        abstract = True


class PanelDetailAbstract(models.Model):

    code = models.CharField(max_length=50, verbose_name=u"Code", help_text=u"Code Number", null=True, blank=True)
    player_no = models.CharField(max_length=50, verbose_name=u"Player Number", help_text=u"Player Number", null=True, blank=True)
    site = models.CharField(max_length=100,verbose_name=u"Site", null=True, blank=True)
    city = models.CharField(max_length=100,verbose_name=u"City", null=True, blank=True)
    wk4_imp = models.CharField(max_length=100,verbose_name=u"4 Week Impressions", null=True, blank=True)
    size = models.CharField(max_length=100,verbose_name=u"Size", null=True, blank=True)
    submarket = models.CharField(max_length=100,verbose_name=u"Submarket", null=True, blank=True)
    description = models.CharField(max_length=100,verbose_name=u"Description", null=True, blank=True)

    class Meta:
        abstract = True

address_type_choice = (
    ('billing', 'Billing'), ('shipping', 'Shipping'),
    ('office', 'Office'), ('personal', 'Personal'),
    ('Other', 'Other'), ('current', 'Current'),
    ('permanent', 'Permanent')
)

class PanelMaster(PanelAbstract):

    market_name = models.CharField(max_length=100, verbose_name=u"Market Name", help_text=u"Market Name", null=True, blank=True)
    latitude = models.FloatField(verbose_name=u"Latitude", null=True, blank=True)
    longitude = models.FloatField(verbose_name=u"Longitude", null=True, blank=True)
    status = models.CharField(max_length=50, verbose_name=u"Status", help_text=u"Status", null=True, blank=True)
    city = models.CharField(max_length=50, null=True, blank=True)
    state = models.CharField(max_length=50, null=True, blank=True)
    country = models.CharField(max_length=50, null=True, blank=True)
    postal_code = models.CharField(max_length=50, null=True, blank=True)
    address_title = models.CharField(max_length=40, null=True, blank=True)
    address_type = models.CharField(max_length=40,
                                    choices=address_type_choice, null=True, blank=True)
    address_line1 = models.CharField(max_length=100, null=True, blank=True)
    address_line2 = models.CharField(max_length=100, null=True, blank=True)

    def __str__(self):
        return "%s | %s" % (self.market_name, self.panel_no)

    class Meta:
        verbose_name_plural = '    Panel Master'

class PanelStaticDetails(PanelAbstract,PanelDetailAbstract):

    media_type = models.CharField(max_length=100,verbose_name=u"Media Type", null=True, blank=True)
    unit_type = models.CharField(max_length=100,verbose_name=u"Unit Type", null=True, blank=True)

    def __str__(self):
        return "%s | %s" % (self.panel_no, self.player_no)

    class Meta:
        verbose_name_plural = '    Panel Static Details'

class PanelPlayerDetails(PanelAbstract,PanelDetailAbstract):
    sales_spot = models.CharField(max_length=100, verbose_name=u"Sales Spot", help_text=u"Sales Spot", null=True, blank=True)

    def __str__(self):
        return "%s | %s" % (self.panel_no, self.player_no)

    class Meta:
        verbose_name_plural = '    Panel Player Details'

def get_upload_to(instance, filename):
    directory_name = None
    custom_date = datetime.date.today().strftime('%Y.%m.%d')
    if isinstance(instance, str):
        directory_name = instance
    else:
        directory_name = instance.calculator_id.directory_name
    if filename:
        return os.path.join(custom_date, directory_name, filename)
    return os.path.join(custom_date, directory_name)


class PanelDocument(models.Model):
    name = models.CharField(max_length=255, verbose_name=u"Description", blank=True)
    uploaded_at = models.DateTimeField(verbose_name=u"Uploaded at",auto_now_add=True)
    document = models.FileField(verbose_name=u"Document", upload_to='scripts/')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = ' PanelDocument'

    def get_file_name(self):
        base = os.path.basename(str(self.document))
        os.path.splitext(base)
        return '{}{}'.format(os.path.splitext(base)[0], os.path.splitext(base)[1])

    def clean(self):
        self.is_cleaned = True
        if False:
            raise ValidationError("Something went wrong!")
        super(PanelDocument, self).clean()

    def save(self, *args, **kwargs):
        print('panel document save .....')
        old_instance = False
        new_instance = False
        obj = super(PanelDocument, self).save(*args, **kwargs)
        if self.id:
            new_instance = PanelDocument.objects.get(id=self.id)
            print('new_instance ====', new_instance.document)
            print('excel ....')
            if settings.DATA_FILE_DIR and new_instance.document:
                excelfile = settings.DATA_FILE_DIR + new_instance.document.url
                excelfile = excelfile.replace("/", "\\")
                print('\n excel file =======')
                excel_to_csv(excelfile)
        return obj

class Address(models.Model):
    address_title = models.CharField(max_length=40)
    address_type = models.CharField(max_length=40,
                                    choices=address_type_choice, null=True)
    address_line1 = models.CharField(max_length=100)
    address_line2 = models.CharField(max_length=100)
    city = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    country = models.CharField(max_length=50)
    postal_code = models.CharField(max_length=50)
    latitude = models.CharField(max_length=50)
    longitude = models.CharField(max_length=50)
    enable = models.BooleanField(default=True)

    def __str__(self):
        return str(self.address_title)
