
# Horizon Monitoring Dashboard

This is a simple Horizon based interface for Sensu Monitoring Framework with Known Error Database.

## Installation notes

* add 'horizon_monitoring' to INSTALLED_APPS tuple
* add 'monitoring' to 'dashboards' key in HORIZON_CONFIG
* add to horizon settings file
 
      SENSU_HOST='localhost'
      SENSU_PORT=4567

  and optionally

      KEDB_HOST='localhost'
      KEDB_PORT=6754

## Read more

* http://docs.openstack.org/developer/horizon/topics/tutorial.html
* http://sensuapp.org/docs/0.12/api
* http://docs.openstack.org/developer/horizon/_modules/horizon/tables/base.html
* http://docs.openstack.org/developer/horizon/ref/tables.html
* http://nagios.sourceforge.net/docs/3_0/flapping.html
* https://packages.debian.org/wheezy/nagios-plugins-openstack
* https://github.com/ehazlett/sensu-py/