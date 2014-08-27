
from django import http
from django import shortcuts
from django.core.urlresolvers import reverse
from django.core.urlresolvers import reverse_lazy
from django.utils.translation import ugettext_lazy as _

from horizon import tables
from horizon import exceptions
from horizon import forms
from horizon import tabs
from horizon import workflows

from horizon_monitoring.dashboard import include_kedb
from horizon_monitoring.events.tables import SensuEventsTable, FullScreenSensuEventsTable
from horizon_monitoring.events.tabs import SensuEventDetailTabs
from horizon_monitoring.events.forms import SilenceForm
from horizon_monitoring.utils.sensu_client import sensu_api, kedb_api
from .workflows import DetailEvent

class FullScreenIndexView(tables.DataTableView):
    table_class = FullScreenSensuEventsTable
    template_name = 'horizon_monitoring/events/fullscreen.html'

    def get_data(self):
        return sensu_api.event_list()

class IndexView(tables.DataTableView):
    table_class = SensuEventsTable
    template_name = 'horizon_monitoring/events/index.html'

    def get_data(self):
        return sensu_api.event_list(self.request)

class SilenceView(forms.ModalFormView):
    form_class = SilenceForm
    template_name = 'horizon_monitoring/events/silence_check.html'
    success_url = reverse_lazy('horizon:monitoring:events:index')

    def get_context_data(self, **kwargs):
        context = super(SilenceView, self).get_context_data(**kwargs)
        context['check'] = self.kwargs.get("check", None)
        context['client'] = self.kwargs.get("client", None)
        return context

    def get_initial(self):
        return self.get_context_data()

"""
class DetailView(workflows.WorkflowView):
    
    workflow_class = DetailEvent
    #template_name = 'horizon_monitoring/errors/update.html'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        event = sensu_api.event_detail(self.kwargs['check'], self.kwargs['client'])
        context['event'] = kedb_api.event_detail(event)
        return context

    def get_initial(self, **kwargs):
        #context['id'] = self.kwargs['id']
        context = {}
        event = sensu_api.event_detail(self.kwargs['check'], self.kwargs['client'])
        return kedb_api.event_detail(event)
"""

class DetailView(tabs.TabView):
    tab_group_class = SensuEventDetailTabs
    template_name = 'horizon_monitoring/events/detail.html'
    redirect_url = 'horizon:monitoring:events:index'

    def get_context_data(self, **kwargs):
        context = super(DetailView, self).get_context_data(**kwargs)
        context['check'] = self.kwargs['check']
        context['client'] = self.kwargs['client']
        return context

    def get_data(self):
        check = self.kwargs['check']
        client = self.kwargs['client']
        try:
            event = sensu_api.event_detail(check, client)
            if include_kedb:
                event = kedb_api.event_list([event])[0]
        except Exception:
            redirect = reverse(self.redirect_url)
            exceptions.handle(self.request,
                              _('Unable to retrieve details for '
                                'instance "%s".') % check,
                                redirect=redirect)
            # Not all exception types handled above will result in a redirect.
            # Need to raise here just in case.
            raise exceptions.Http302(redirect)
        return event

    def get_tabs(self, request, *args, **kwargs):
        instance = self.get_data()
        return self.tab_group_class(request, instance=instance, **kwargs)

"""
class UpdateView(workflows.WorkflowView):
    workflow_class = project_workflows.UpdateInstance
    success_url = reverse_lazy("horizon:project:instances:index")

    def get_context_data(self, **kwargs):
        context = super(UpdateView, self).get_context_data(**kwargs)
        context["instance_id"] = self.kwargs['instance_id']
        return context

    @memoized.memoized_method
    def get_object(self, *args, **kwargs):
        instance_id = self.kwargs['instance_id']
        try:
            return api.nova.server_get(self.request, instance_id)
        except Exception:
            redirect = reverse("horizon:project:instances:index")
            msg = _('Unable to retrieve instance details.')
            exceptions.handle(self.request, msg, redirect=redirect)

    def get_initial(self):
        initial = super(UpdateView, self).get_initial()
        initial.update({'instance_id': self.kwargs['instance_id'],
                'name': getattr(self.get_object(), 'name', '')})
        return initial
"""