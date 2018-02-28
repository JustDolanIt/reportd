import logging


class Scenario:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        self.plugins = kwargs['plugins']
        logging.info('Test scenario inited')

    """
    Example kwargs:
    {
      "k8s": [
        {
          "deployment": "abonent",
          "namespace": "api",
          "context": "prod"
        }
      ],
      "grafana": [
        {
          "url": "https://grafana.app.ipl/render/d-solo/000000038/bc?refresh=1m&panelId=20&orgId=1&width=1000&height=500&tz=UTC%2B03%3A00",
          "offset_secs": 600
        }
      ],
      "http": [
        {
          "url": "https://zabbix.app.ipl/",
          "ssl_verify": false
        },
        {
          "url": "http://alerta.app.ipl/"
        }
      ],
      "pg": [
        {
          "host": "pg3.db.ipl",
          "query": "select * from reportd.reports",
          "database": "mon_celery"
        }
      ],
      "ssh": [
        {
          "host": "testfield.test.ipl",
          "user": "ddunaev",
          "commands": "hostname && date && sudo systemctl status zabbix-agent"
        }
      ],
      "web": [
        {
          "page": "http://alerta.app.ipl/#/alerts?status=open&status=unknown",
          "wait": 10,
          "width": 1024,
          "xpath": "/html/body/div/div/div[3]/div[2]/table/tbody/tr[2]",
          "height": 1024
        },
        {
          "page": "http://office.app.ipl/time",
          "width": 768,
          "height": 1700
        }
      ]
    }
    """
    async def process(self, alert):
        logging.info('Test scenario process called')

        ex_plug = self.plugins['example_plugin'].Plugin(**self.kwargs)
        ex_result = await ex_plug.process(alert)
        ex_result_formatted = """
{}

{}
        """.format(ex_result['head'], ex_result['body'])

        ssh_requests = []
        ssh_plug = self.plugins['ssh_plugin'].Plugin(**self.kwargs)
        for ssh_data in self.kwargs['ssh']:
            ssh_requests.append(await ssh_plug.process(ssh_data))
        ssh_requests_formatted = "\n".join(["""
{}

{}

        """.format(s['head'], s['body']) for s in ssh_requests])

        screenshots = []
        web_screen_plug = self.plugins['web_screenshot_plugin'].Plugin(**self.kwargs)
        for web_data in self.kwargs['web']:
            screenshots.append(await web_screen_plug.process(web_data))
        screenshots_formatted = "\n".join(["""
{}

{}

        """.format(s['head'], s['body']) for s in screenshots])

        pg = []
        pg_plug = self.plugins['pg_plugin'].Plugin(**self.kwargs)
        for pg_data in self.kwargs['pg']:
            pg.append(await pg_plug.process(pg_data))

        pg_formatted = "\n".join(["""
{}

{}

        """.format(s['head'], s['body']) for s in pg])

        http = []
        http_plug = self.plugins['http_plugin'].Plugin(**self.kwargs)
        for http_data in self.kwargs['http']:
            http.append(await http_plug.process(http_data))

        http_formatted = "\n".join(["""
{}

{}

        """.format(s['head'], s['body']) for s in http])

        grafana = []
        grafana_plug = self.plugins['grafana_plugin'].Plugin(**self.kwargs)
        for grafana_data in self.kwargs['grafana']:
            grafana.append(await grafana_plug.process(grafana_data))
        grafana_formatted = "\n".join(["""
{}

{}

        """.format(s['head'], s['body']) for s in grafana])

        k8s = []
        k8s_plug = self.plugins['k8s_plugin'].Plugin(**self.kwargs)
        for k8s_data in self.kwargs['k8s']:
            k8s.append(await k8s_plug.process(k8s_data))
        k8s_formatted = "\n".join(["""
{}

{}

        """.format(s['head'], s['body']) for s in k8s])

        kibana_screens = []
        kibana_plug = self.plugins['kibana_plugin'].Plugin(**self.kwargs)
        for kibana_data in self.kwargs['kibana']:
            kibana_screens.append(await kibana_plug.process(kibana_data))
        kibana_screens_formatted = "\n".join(["""
{}

{}

        """.format(s['head'], s['body']) for s in kibana_screens])

        return """
## Alert data

{}

---

## SSH requests

{}

---

## Screenshots

{}

---

## PostgreSQL

{}

---

## HTTP

{}

---

## Grafana

{}

---

## K8s

{}

---

## Kibana

{}
        """.format(
            ex_result_formatted,
            ssh_requests_formatted,
            screenshots_formatted,
            pg_formatted,
            http_formatted,
            grafana_formatted,
            k8s_formatted,
            kibana_screens_formatted
            )
