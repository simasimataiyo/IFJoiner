

# keyboard
# MIT License

# Copyright (c) 2016 Lucas Boppre Niehues

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



# OSCpy
# Copyright (c) 2018 Gabriel Pettier & al

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.



bl_info = {
    'name': 'I/F Joiner',
    'author': 'simasimataiyo',
    'version': (0.01, 0),
    'blender': (2, 80, 0),
    'location': '3Dビューポート > Sidebar > I/F Joiner',
    'description': 'Execute the operator in response to the received OSC message',
    'warning': '',
    'support': 'COMMUNITY',
    'wiki_url': '',
    'tracker_url': 'https://github.com/simasimataiyo/IFJoiner',
    'category': 'Interface'
}

import sys
import os
sys.path.append( os.path.dirname( os.path.realpath(__file__) ) )

# import modules
if 'bpy' in locals():
    import importlib
    importlib.reload(op)
    importlib.reload(skop)
    importlib.reload(ui)
    importlib.reload(props)
    importlib.reload(custom_operators)
else:
    from . import osccom_op as op
    from . import send_key_op as skop
    from . import ui
    from . import props
    from .custom_operators import *


import bpy
from bpy.app.handlers import persistent


# Blenderに登録するAddon本体のクラス
classes = [
    props.IFJ_MessageMapItem,
    props.IFJ_MessageMap,
    op.IFJ_OT_OSCCommunicator,
    op.IFJ_OT_AddMessageMap,
    op.IFJ_OT_RemoveMessageMap,
    op.IFJ_OT_AddMessageMapItem,
    op.IFJ_OT_AddMessageMapFromJSON,
    op.IFJ_OT_RemoveMessageMapItem,
    op.IFJ_OT_ExportMessageMap,
    op.IFJ_OT_MoveMessageMapItem,
    op.IFJ_OT_SaveMessageMaps,
    op.IFJ_OT_OpenMessageMaps,
    op.IFJ_OT_LoadMessageMaps,
    op.IFJ_OT_GetIPAddress,
    skop.IFJ_OT_SendKeyPress,
    skop.IFJ_OT_SendKeyRelease,
    skop.IFJ_OT_SendKeyPressAndRelease,
    ui.IFJ_PT_OSCCommunicator,
    ui.IFJ_MT_AddonPreferences,
]


@persistent
def load_handler(dummy):
    bpy.ops.ifj.load_message_maps()
    bpy.ops.ifj.get_ipaddress()

# addon_register
def register():
    # カスタムオペレータの自動登録
    custom_classes = []
    for fnl in custom_operators.file_name_list:
        module = getattr(custom_operators, fnl)
        for attr in dir(module):
            if attr.startswith('IFJ_'):
                print(attr)
                custom_classes.append( getattr(module, attr) )
    
    for c in classes:
        bpy.utils.register_class(c)

    for cc in custom_classes:
        bpy.utils.register_class(cc)
    
    bpy.app.handlers.load_post.append(load_handler)

# addon_unregister
def unregister():
     # カスタムオペレータの自動解除
    custom_classes = []
    for fnl in custom_operators.file_name_list:
        module = getattr(custom_operators, fnl)
        for attr in dir(module):
            if attr.startswith('IFJ_'):
                print(attr)
                custom_classes.append( getattr(module, attr) )

    for c in classes:
        bpy.utils.unregister_class(c)

    for cc in custom_classes:
        bpy.utils.unregister_class(cc)

# main
if __name__ == '__main__':
    register()

