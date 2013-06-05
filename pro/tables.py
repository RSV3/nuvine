import django_tables2 as tables
#from django_tables2.utils import A
from pro.models import WeeklyCompensation, MonthlyBonusCompensation, MonthlyQualification


class WeeklyCompensationTable(tables.Table):

    end_time = tables.Column(verbose_name="End Date")

    class Meta:

        model = WeeklyCompensation
        attrs = {"class": "paleblue"}
        exclude = ['id', 'pro', 'start_time']
        sequence = ('end_time', '...')


class MonthlyBonusCompensationTable(tables.Table):

    end_time = tables.Column(verbose_name="End Date")

    class Meta:

        model = MonthlyBonusCompensation
        attrs = {"class": "paleblue"}
        exclude = ['id', 'pro', 'start_time']
        sequence = ('end_time', '...')


class MonthlyQualificationTable(tables.Table):

    end_time = tables.Column(verbose_name="End Date")

    class Meta:

        model = MonthlyQualification
        attrs = {"class": "paleblue"}
        exclude = ['id', 'pro', 'start_time']
        sequence = ('end_time', '...')

