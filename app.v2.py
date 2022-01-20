import routing
import dataclasses

from routing import labels

'''
Notes:
    * Just focus on URIs? This was can benefit from passing parameters?
        - No, that should be an extension on top of this library
'''


@labels.route('/foo', '/bar')
@labels.mount('/mount')
def foo():
    ...

@labels.middleware
def bar():
    ...