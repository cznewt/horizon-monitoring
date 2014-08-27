from django.conf import settings
from django.core import urlresolvers
from django.template.defaultfilters import timesince
from django.utils.http import urlencode
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon_contrib.tables.actions import FilterAction

from horizon_contrib.tables.filters import timestamp_to_datetime, \
    nonbreakable_spaces, join_list_with_comma, unit_times, status_image

from horizon_monitoring.utils.sensu_client import sensu_api, kedb_api

from horizon_monitoring.dashboard import include_kedb

class FullScreenView(tables.LinkAction):
    name = "fullscreen_view"
    verbose_name = _("Fullscreen Mode")
    url = "horizon:monitoring:events:fullscreen_index"
    classes = ("btn")

    def get_link_url(self):
        return urlresolvers.reverse(self.url, args=[])

class EventAction(tables.BatchAction):
    """base event action"""
    data_type_singular = _("Event")
    data_type_plural = _("Events")

    verbose_name = _("Resolve Event")
    success_url = "horizon:monitoring:events:index"
    classes = ("btn-primary", "btn-danger")

    def get_check_client(self, object_id):
        check, client = None, None
        client, check = object_id.split(" ")
        return check, client

    def resolve(self, request, object_id):
        check, client = self.get_check_client(object_id)
        response = sensu_api.event_resolve(check, client)

    def recheck(self, request, object_id):
        check, client = self.get_check_client(object_id)
        response = sensu_api.event_recheck(check, client)

    def action(self, request, object_id):
        pass

class RecheckEvent(EventAction):
    action_present = ("Recheck",)
    action_past = ("Rechecked",)
    name = "recheck_event"
    verbose_name = _("Recheck Event")
    success_url = "horizon:monitoring:events:index"
    classes = ("btn-primary", "btn-danger", "btn-info")

    def action(self, request, object_id):
        self.recheck(request, object_id)

    def allowed(self, request, instance):
        return True

class ResolveEvent(EventAction):
    action_present = ("Resolve",)
    action_past = ("Resolved",)
    name = "resolve_event"
    verbose_name = _("Resolve Event")
    success_url = "horizon:monitoring:events:index"
    classes = ("btn-primary", "btn-danger", "btn-success")

    def action(self, request, object_id):
        self.resolve(request, object_id)

    def allowed(self, request, instance):
        return True

class EventDetail(tables.LinkAction):
    name = "event_detail"
    verbose_name = _("Event Detail")
    url = "horizon:monitoring:events:detail"
    classes = ("btn-edit")

    def get_link_url(self, event):
        return urlresolvers.reverse(self.url, args=[event['check'], event['client']])
        
    def allowed(self, request, instance):
        return True

class ErrorCreate(tables.LinkAction):
    """error create
    """
    name = "error_create"
    verbose_name = _("Create Known Error")
    classes = ("ajax-modal", "btn-edit")
    url = "horizon:monitoring:errors:create_check"
    
    def get_link_url(self, datum):
        return urlresolvers.reverse(self.url, kwargs={'check':datum.get("check"), 'client':datum.get("client")})

    def allowed(self, request, instance):
        allowed = False
        if include_kedb:
            if not instance.get("known_error", False):
                allowed = True
        return allowed

"""
class SilenceCheck(tables.LinkAction):
    name = "silence_check"  
    verbose_name = _("Globally Silence Check")
    url = "horizon:monitoring:events:silence_check"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, event):
        return urlresolvers.reverse(self.url, args=[event['check'],])
"""

class StashDelete(tables.DeleteAction):
    action_present = ("Delete",)
    action_past = ("Deleted",)
    data_type_singular = _("Stash")
    data_type_plural = _("stashes")
    name = "stash_delete"
    success_url = "horizon:monitoring:events:index"

    def get_check_client(self, object_id):
        check, client = None, None
        client, check = object_id.split(" ")
        return client, check

    def is_client(self, client, check):
        """zjisti jestli jestli je stashlej jenom client/check nebo celej client
        neprisli sme na lepsi reseni
        """
        events = sensu_api.event_list
        stashes = sensu_api.stash_list
        if include_kedb:
          events = kedb_api.event_list(events)
        stash_map = []
        for stash in stashes:
            stash_map.append(stash['path'])
        for event in events:
            if 'silence/%s/%s' % (event['client'], event['check']) in stash_map:
                return False
            elif 'silence/%s'% event['client'] in stash_map:
                return True
        return False

    def delete(self, request, path):
        client, check = self.get_check_client(path)
        _path = "silence/%s" % client
        if not self.is_client(client, check):
            _path = "%s/%s" % (_path, check)
        sensu_api.stash_delete(_path)

    def allowed(self, request, instance):
        if instance.get("silenced", False):
            return True
        return False

class SilenceClient(tables.LinkAction):
    name = "silence_client"  
    verbose_name = _("Silence All Checks on Client")
    url = "horizon:monitoring:events:silence_client"
    classes = ("ajax-modal", "btn-edit")

    def get_link_url(self, event):
        return urlresolvers.reverse(self.url, args=[event['client'],])

class SilenceClientCheck(tables.LinkAction):
    name = "silence_client_check"
    verbose_name = _("Silence Check on Client")
    url = "horizon:monitoring:events:silence_client_check"
    classes = ("ajax-modal", "btn")

    def get_link_url(self, event):
        return urlresolvers.reverse(self.url, args=[event['client'], event['check']])

class SensuEventsTable(tables.DataTable):

    def get_error_link(self):
        url = "horizon:monitoring:errors:update"
        error_id = self.get("error_id", None)
        if error_id:
            return urlresolvers.reverse(url, args=(error_id,))
        return ""

    client = tables.Column('client', verbose_name=_("Client"))
    check = tables.Column('check', verbose_name=_("Check"))
    
    if include_kedb:
        #known_error = tables.Column('known_error', verbose_name=_("Known"))
        error_name = tables.Column('error_name', verbose_name=_("Error name"))
#        severity = tables.Column('severity', verbose_name=_("Error severity"))
    output = tables.Column('output', verbose_name=_("Output"), truncate=70)
    status = tables.Column('status', verbose_name=_("Status"), classes=('status_column',), hidden=True)
    flapping = tables.Column('flapping', verbose_name=_("Flapping"), classes=('silenced_column', 'centered'), filters=(status_image,))
    silenced = tables.Column('silenced', verbose_name=_("Silenced"), classes=('silenced_column', 'centered'), filters=(status_image,))
    occurrences = tables.Column('occurrences', verbose_name=_("Occured"), filters=(unit_times, ))
    issued = tables.Column('issued', verbose_name=_("Last occurence"), filters=(timestamp_to_datetime, timesince, nonbreakable_spaces))

    def get_object_id(self, datum):
        return '%s %s' % (datum['client'], datum['check'])

    def get_object_display(self, datum):
        return '%s %s' % (datum['client'], datum['check'])

    class Meta:
        name = "events"
        verbose_name = _("Current Events")
        row_actions = (EventDetail,
                        ResolveEvent,
                        RecheckEvent,
                        #SilenceCheck,
                        SilenceClient,
                        SilenceClientCheck,
                        ErrorCreate,
                        StashDelete)
        table_actions = (FullScreenView,
                         ResolveEvent,
                         FilterAction,
                         RecheckEvent )

class FullScreenSensuEventsTable(SensuEventsTable):
    
    def get_object_id(self, datum):
        return '%s %s' % (datum['client'], datum['check'])

    class Meta:
        name = "events"
        verbose_name = _("Current Events")
        columns = ("client", "check", "output", "status", "issued")