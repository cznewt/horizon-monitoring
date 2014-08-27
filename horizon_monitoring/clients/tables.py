

from django.utils.translation import ugettext_lazy as _
from horizon import tables

from django.template.defaultfilters import timesince

from horizon_monitoring.utils.filters import timestamp_to_datetime, nonbreakable_spaces, join_list_with_comma
from horizon_contrib.tables.actions import FilterAction

class SensuClientsTable(tables.DataTable):
    name = tables.Column('name', verbose_name=_("Client Name"))
    address = tables.Column('address', verbose_name=_("Address"))
    subscriptions = tables.Column('subscriptions', verbose_name=_("Subscriptions"), filters=(join_list_with_comma,))
    timestamp = tables.Column('timestamp', verbose_name=_("Last Checkin"), filters=(timestamp_to_datetime, timesince, nonbreakable_spaces))

    def get_object_id(self, datum):
        return datum['name']

    def get_object_display(self, datum):
        return datum['name']

    class Meta:
        name = "clients"
        verbose_name = _("Monitored Clients")
        table_actions = (FilterAction, )