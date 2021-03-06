
import horizon
from django.utils.translation import ugettext_lazy as _
from horizon_monitoring import dashboard

class InfoPanel(horizon.Panel):
    name = _("Monitoring status")
    slug = 'info'

dashboard.MonitoringDashboard.register(InfoPanel)
