import json

from rest_framework.renderers import JSONRenderer


class CustomRenderer(JSONRenderer):
    charset = 'utf-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if 'ErrorDetail' in str(data):
            return json.dumps({
                'data': None,
                'exception': data
            })
        elif 'error' in str(data):
            return json.dumps({
                'data': None,
                'exception': data.get('error')
            })
        else:
            return json.dumps({
                'data': data.get('data'),
                'message': data.get('message')
            })
