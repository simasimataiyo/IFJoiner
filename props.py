
import bpy

class IFJ_MessageMapItem(bpy.types.PropertyGroup):

    min_value: bpy.props.FloatVectorProperty(
        name='Min',
        size=3
    )

    max_value: bpy.props.FloatVectorProperty(
        name='Max',
        size=3
    )

    exec_ops_name: bpy.props.StringProperty(
        name='Identifier of Operator',
        description='受信時に実行するオペレータのIdentifier',
        default='',
        subtype='NONE'
    )

    exec_ops_args: bpy.props.StringProperty(
        name='Arguments of Operator',
        description='オペレータの引数',
        default='',
        subtype='NONE'
    )

    map_item_id: bpy.props.IntProperty(
        name='Map Item ID',
        default = 0,
    )


class IFJ_MessageMap(bpy.types.PropertyGroup):

    osc_message: bpy.props.StringProperty(
        name='OSC Message',
        description='',
        default='/address_pattern',
        subtype='NONE'
    )

    show_expanded: bpy.props.BoolProperty(
        name='show_expanded',
    )

    message_type: bpy.props.EnumProperty(
        name='Module Type',
        description='モジュールの種類を選択',
        default='MS',
        items=[
            ('MS', 'MomentarySwitch', 'MomentarySwitch Module'),
            ('SL', 'Slider', 'Slider Module'),
            ('RE', 'RotaryEncoder', 'RotaryEncoder Module'),
            ('JS', 'Joystick', 'Joystick Module'),
            ('OT', 'Other', 'Thirdparty Module'),
        ]
    )

    map_items: bpy.props.CollectionProperty(
        type = IFJ_MessageMapItem
    )

    map_id: bpy.props.IntProperty(
        name='Map_ID',
        default = 0,
    )

    def register():
        bpy.types.WindowManager.cmc_messagemaps = bpy.props.CollectionProperty(type = IFJ_MessageMap)

    def unregister():
        del bpy.types.WindowManager.cmc_messagemaps