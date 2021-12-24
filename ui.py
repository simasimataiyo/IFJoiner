
from . import osccom_op
import bpy

# View3DのPanelに表示するUI
class IFJ_PT_OSCCommunicator(bpy.types.Panel):

    bl_label = 'I/F Joiner'
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'UI'
    bl_category = 'I/F Joiner'
    # bl_context = 'objectmode'

    def draw(self, context):
        op_osccom = osccom_op.IFJ_OT_OSCCommunicator
        layout = self.layout

        # [開始] / [停止] ボタンを追加
        if not op_osccom.is_running():
            layout.prop(context.preferences.addons[__package__].preferences, 'port_address')
            layout.prop(context.preferences.addons[__package__].preferences, 'port_number')
            layout.operator(op_osccom.bl_idname, text='Start', icon='PLAY')
        else:
            layout.operator(op_osccom.bl_idname, text='Stop', icon='PAUSE')


# Preferenceに表示する設定パネル
class IFJ_MT_AddonPreferences(bpy.types.AddonPreferences):
    bl_idname = __package__

    port_address: bpy.props.StringProperty(
        name='IP Address',
        description='接続先のIPアドレスを入力します',
        default='127.0.0.1',
        maxlen=64, # 最大文字数
        subtype='NONE'
    )

    port_number: bpy.props.IntProperty(
        name='Port Number',
        description='接続先のポート番号を指定します',
        default=10000,
        subtype='NONE'
    )

    settings_file_path: bpy.props.StringProperty(
        default='',
        maxlen=255
    )
    
    # display each MapItems
    def draw_mmi(self, layout, mm, mmi):
        # operators
        op_remove_map_items = osccom_op.IFJ_OT_RemoveMessageMapItem
        op_move_map_items = osccom_op.IFJ_OT_MoveMessageMapItem

        box = layout.box()

        row = box.row()
        row.alignment = 'RIGHT'
        rmmpi = row.operator(op_remove_map_items.bl_idname, text='Delete', icon='PANEL_CLOSE')
        rmmpi.selected_map = mm.map_id
        rmmpi.selected_map_item = mmi.map_item_id

        mvmpi_up = row.operator(op_move_map_items.bl_idname, text='', icon='TRIA_UP')
        mvmpi_up.selected_map = mm.map_id
        mvmpi_up.selected_map_item = mmi.map_item_id
        mvmpi_up.direction = False

        mvmpi_down = row.operator(op_move_map_items.bl_idname, text='', icon='TRIA_DOWN')
        mvmpi_down.selected_map = mm.map_id
        mvmpi_down.selected_map_item = mmi.map_item_id
        mvmpi_down.direction = True

        col = box.column()
        col.use_property_split = True
        col.prop(mmi, 'exec_ops_name')
        col.prop(mmi, 'exec_ops_args')

        col.separator(factor=2)

        col.use_property_split = False
        col.label(text='Event Trigger:')
        cond_row = col.row(align=True)
        split = cond_row.split(factor=0.5, align=True)
        split.prop(mmi, 'min_value')
        split.prop(mmi, 'max_value')
        


    # display each Message Map
    def draw_mm(self, layout, mm):
        # operators
        op_remove_message_map = osccom_op.IFJ_OT_RemoveMessageMap
        op_export_message_map = osccom_op.IFJ_OT_ExportMessageMap
        op_add_message_map_item = osccom_op.IFJ_OT_AddMessageMapItem

        if mm.show_expanded:
            # header bar
            box = layout.box()
            split = box.split(factor=0.7, align=True)
            
            row = split.row(align=True)
            row.prop(mm, 'show_expanded', text='', icon='TRIA_DOWN' if mm.show_expanded else 'TRIA_RIGHT', emboss=False)
            row.prop(mm, 'osc_message', text='', expand=True)
            row = split.row()
            row.alignment = 'RIGHT'
            row.operator(op_export_message_map.bl_idname, text='Export', icon='EXPORT').selected_map = mm.map_id
            row.operator(op_remove_message_map.bl_idname, text='Delete', icon='PANEL_CLOSE').selected_map = mm.map_id
            
            split = box.split(factor=0.1, align=True)
            subcol = split.column()
            subcol = split.column()
            subcol.label(text='Operators:',icon='NONE')

            if len(mm.map_items) > 0:
                for mmi in mm.map_items:
                    self.draw_mmi(subcol, mm, mmi)

            subcol.separator(factor=1)
            admpi = subcol.operator(op_add_message_map_item.bl_idname, text='Add', icon='ADD')
            admpi.selected_map = mm.map_id
            subcol.separator(factor=1)
        
        else:
            # header bar
            split = layout.split(factor=0.7, align=True)
            row = split.row(align=True)
            row.prop(mm, 'show_expanded', text='', icon='TRIA_DOWN' if mm.show_expanded else 'TRIA_RIGHT', emboss=False)
            row.prop(mm, 'osc_message', text='', expand=True)
            row = split.row()
            row.alignment = 'RIGHT'
            row.operator(op_export_message_map.bl_idname, text='Export', icon='EXPORT').selected_map = mm.map_id
            row.operator(op_remove_message_map.bl_idname, text='Delete', icon='PANEL_CLOSE').selected_map = mm.map_id
            
            


    # Main draw
    def draw(self, context):
        # messagemap_collection
        mms = context.window_manager.cmc_messagemaps

        # operators
        op_add_message_map = osccom_op.IFJ_OT_AddMessageMap
        op_addmm_from_json = osccom_op.IFJ_OT_AddMessageMapFromJSON
        op_svmms = osccom_op.IFJ_OT_SaveMessageMaps
        op_ldmms = osccom_op.IFJ_OT_OpenMessageMaps

        layout = self.layout     
        box = layout.box()
        server = box.column(heading='OSC Server')
        server.label(text='OSC Server:')
        server.use_property_split = True
        server.prop(context.preferences.addons[__package__].preferences, 'port_address')
        server.prop(context.preferences.addons[__package__].preferences, 'port_number')

        
        messages = layout.box()
        messages.label(text='Message Maps:')
        split = messages.split(factor=0.05, align=True)
        subcol = split.column()
        subcol = split.column()
        if len(mms) > 0:
            for mm in mms:
                self.draw_mm(subcol, mm)
        else:
            subcol.label(text='   No Message Maps')
        
        # add message map

        row = subcol.row()
        row.operator(op_add_message_map.bl_idname, text='Add New Message Map', icon='ADD')
        row.operator(op_addmm_from_json.bl_idname, text='Import Message Map from .json', icon='IMPORT')
        subcol.separator(factor=1)
        row = subcol.row()
        row.label(text='Preferences File:')
        row = subcol.row()
        row.prop(context.preferences.addons[__package__].preferences, 'settings_file_path', text='')
        row.operator(op_svmms.bl_idname, text='Save', icon='FILE_TICK')
        row.operator( op_ldmms.bl_idname, text='Load', icon='IMPORT')


        