import logging
import json
import urllib3

from kubernetes import client, config
from kubernetes.client import configuration


class Plugin:
    def __init__(self, *args, **kwargs):
        self.kwargs = kwargs
        logging.info('K8s plugin inited')
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    """
    Requires body params:
    k8s:
      deployment: 
      namespace:
      context: (optional - prod will be used)
      offset_secs: (optional - will be used 100)
    """
    async def process(self, body):
        logging.info('K8s plugin process called')

        config.load_kube_config(
            config_file=self.kwargs['global_config']['k8s']['config_file'],
            context=body.get('context', 'prod')
        )

        configuration.assert_hostname = True

        appsApi = client.AppsV1Api()

        deployment = appsApi.read_namespaced_deployment(
            body['deployment'],
            body['namespace'],
            pretty=True,
            exact=True,
            export=False
        )

        coreApi = client.CoreV1Api()

        pods = coreApi.list_namespaced_pod(
            namespace=body['namespace'],
            label_selector="app={}".format(body['deployment']),
            pretty=True
        )

        headers = ( 'name', 'node', 'status', 'reason' )
        result_formatted = ' | '.join(headers)
        result_formatted = '\n'.join( [
            result_formatted,
            '|'.join( ['-'] * len(headers) )
            ]
        )

        pods_data = []
        pods_list = []
        pods_logs = []

        for p in pods.items:
            pods_data.append(
                '|'.join(
                    (
                        p.metadata.name,
                        p.spec.node_name,
                        p.status.phase,
                        str(p.status.reason)
                    )
                )
            )

            pods_list.append(p.metadata.name)

            # TODO get logs here for p['metadata']['name']
            if p.status.phase != 'Failed':
                pods_logs.append("""
##### {}

<pre>
{}
</pre>

                """.format(
                    p.metadata.name,
                    coreApi.read_namespaced_pod_log(
                        name=p.metadata.name,
                        namespace=body['namespace'],
                        since_seconds=body.get('offset_secs', 100),
                        timestamps=True,
                        pretty=True,
                        )
                    )
                )

        result_formatted = '\n'.join( [ result_formatted ] + pods_data )

        pods_logs_formatted = '\n'.join(pods_logs)

        return {
                "head": "### {}.{}/{}".format(
                    body['context'],
                    body['namespace'],
                    body['deployment']
                    ),
                "body": """
#### Deployment definition

<pre>
{}
</pre>

#### Pods

{}

#### Pods logs

{}
                """.format(
                    deployment,
                    result_formatted,
                    pods_logs_formatted
                    )
                }
