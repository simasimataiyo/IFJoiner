
from bpy_extras.io_utils import ImportHelper, ExportHelper
import bpy
import queue
import socket
import oscpy
import time
from pathlib import Path
import json
from collections import OrderedDict

# OSC Server
class IFJ_OT_OSCCommunicator(bpy.types.Operator):

    bl_idname = 'ifj.oscserver'
    bl_label = 'OSC Server'
    bl_description = 'Control OSC Server'

    # タイマのハンドラ
    __timer = None

    sock = None
    osc_server = None

    # 通信用スレッドと受け取ったメッセージを共有するためのqueue
    q = queue.Queue()

    @classmethod
    def is_running(cls):
        # モーダルモード中はTrue
        return True if cls.__timer else False

    def __handle_add(self, context):
        co = IFJ_OT_OSCCommunicator
        if not co.is_running():
            # タイマを登録
            co.__timer = \
                context.window_manager.event_timer_add(
                    0.01, window=context.window
                )
            # モーダルモードへの移行
            context.window_manager.modal_handler_add(self)

    def __handle_remove(self, context):
        co = IFJ_OT_OSCCommunicator
        if co.is_running():
            # タイマの登録を解除
            context.window_manager.event_timer_remove(
                co.__timer)
            co.__timer = None
    
    # 受け取ったメッセージをqueueに貯めこむ
    def callback(self, address, *args):
        print(address, args)
        self.q.put( [address, args], block=True, timeout=None )

    # オペレータ発動処理
    def ops_condition_checker(self, arg, messagemap):
        for mmi in messagemap.map_items:
            # 受け取ったvalueとmin_value,max_valueを比較し全てtrueになるか判定
            true_count = 0
            if(len(arg) <= 3):
                for i, v in enumerate(arg):
                    if v >= mmi.min_value[i] and v <= mmi.max_value[i]:
                        true_count+=1
            else:
                for i in range(3):
                    if arg[i] >= mmi.min_value[i] and arg[i] <= mmi.max_value[i]:
                        true_count+=1
            
            # トリガーが全てtrueならオペレータ実行
            if true_count == len(arg) or true_count == 3:
                try:
                    exec( 'bpy.ops.' + mmi.exec_ops_name + '(' + mmi.exec_ops_args + ')' )
                except:
                    self.report({'ERROR'}, '(bThreeIF)Failed execute operator')
 
    #bpy.opsコールバック
    def exec_operator(self, item, messagemaps):
        if len(messagemaps) == 0:
            print('no messagemaps')
            return

        for mm in messagemaps:
            if mm.osc_message == item[0].decode():
                self.ops_condition_checker(item[1], mm)
                

    def modal(self, context, event):
        Messagemaps = context.window_manager.cmc_messagemaps

        # エリアを再描画
        if context.area:
            context.area.tag_redraw()

        # 終了ボタンを押すとモーダルモードから出る
        if not self.is_running():
            return {'FINISHED'}

        # start_time = time.perf_counter()
        if event.type == 'TIMER':
            # queueの中身を消化
            while not self.q.empty():
                item = self.q.get(block=False)
                self.exec_operator(item, Messagemaps)
        end_time = time.perf_counter()
        # elapsed_time = end_time - start_time
        # print( '{:.5f}'.format(elapsed_time) )

        return {'PASS_THROUGH'}

    def invoke(self, context, event):
        op_cls = self
        co = IFJ_OT_OSCCommunicator
        wm = context.window_manager

        if context.area.type == 'VIEW_3D':
            # [開始] ボタンが押された時の処理
            if not op_cls.is_running():
                try:
                    
                    #OSC通信開始
                    co.osc_server = oscpy.server.OSCThreadServer(encoding='utf8', default_handler=self.callback)
                    co.sock = self.osc_server.listen(address=context.preferences.addons[__package__].preferences.port_address, port=context.preferences.addons[__package__].preferences.port_number, default=False)

                    # モーダルモードを開始
                    self.__handle_add(context)
                    print('Start OSC Communication')
                    return {'RUNNING_MODAL'}

                except OSError:
                    self.report({'ERROR'}, 'OSError')
                    #OSC通信終了
                    co.osc_server.terminate_server()
                    time.sleep(0.5)
                    co.osc_server.stop_all()
                    print(co.osc_server.join_server())
                    co.osc_server = None
                    return {'FINISHED'}


            # [終了] ボタンが押された時の処理
            else:
                #OSC通信終了
                co.osc_server.terminate_server()
                time.sleep(0.5)
                co.osc_server.stop_all()
                print(co.osc_server.join_server())
                co.osc_server = None

                # モーダルモードを終了
                self.__handle_remove(context)
                print('Finish OSC Communication')

                return {'FINISHED'}
        else:
            return {'CANCELLED'}



# AddonPreference用 MessageMap操作オペレータ
# MessageMapを一つ追加
class IFJ_OT_AddMessageMap(bpy.types.Operator):

    bl_idname = 'ifj.add_message_map'
    bl_label = 'Add Message Map'
    bl_description = 'モジュールマップを1つ追加'

    def execute(self, context):
        mms = context.window_manager.cmc_messagemaps
        newItem = mms.add()

        for i, mm in enumerate(mms):
            mm.map_id = i
        
        return {'FINISHED'}


# MessageMapをJSONファイルから一つ追加
class IFJ_OT_AddMessageMapFromJSON(bpy.types.Operator, ImportHelper):

    bl_idname = 'ifj.add_message_map_from_json'
    bl_label = 'Import From JSON'
    bl_description = 'モジュールマップをJSONファイルから1つ追加'

    filename_ext = '.json'

    filter_glob: bpy.props.StringProperty(
        default='*.json',
        options={'HIDDEN'},
        maxlen=255,
    )

    def add_from_json(self, context, filepath):
        mms = context.window_manager.cmc_messagemaps

        dict_map = {}

        p = Path(filepath)

        with p.open() as f:
            dict_map = json.load(f)

        newItem = mms.add()
        newItem.osc_message = dict_map['osc_message']
        newItem.message_type = dict_map['message_type']
        # newItem.show_expanded = mm['show_expanded']
        # newItem.map_id = mm['map_id']

        for mmi in dict_map['map_items']:
            item = newItem.map_items.add()
            item.min_value = mmi['min_value']
            item.max_value = mmi['max_value']
            item.exec_ops_name = mmi['exec_ops_name']
            item.exec_ops_args = mmi['exec_ops_args']
            item.map_item_id = mmi['map_item_id']

        for i, mm in enumerate(mms):
            mm.map_id = i
        
        return {'FINISHED'}

    def execute(self, context):
        return self.add_from_json(context, self.filepath)


# MessageMapを一つ削除
class IFJ_OT_RemoveMessageMap(bpy.types.Operator):

    bl_idname = 'ifj.romove_message_map'
    bl_label = 'Remove Message Map'
    bl_description = 'モジュールマップを削除'

    selected_map: bpy.props.IntProperty(default=0)

    def execute(self, context):
        mm = context.window_manager.cmc_messagemaps
        mm.remove( self.selected_map )
        for i, mmi in enumerate(mm):
            mmi.map_id = i

        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)


# 選択したMessageMapデータをJSONにExport
class IFJ_OT_ExportMessageMap(bpy.types.Operator, ExportHelper):

    bl_idname = 'ifj.export_message_map'
    bl_label = 'Export Message Map'
    bl_description = 'このMessage MapをJSONファイルに書き出す'

    selected_map: bpy.props.IntProperty(default=0)

    filename_ext = '.json'

    filter_glob: bpy.props.StringProperty(
        default='*.json',
        options={'HIDDEN'},
        maxlen=255,
    )

    def write_json_data(self, context, filepath):
        mm = context.window_manager.cmc_messagemaps[self.selected_map]

        dict_map = {}
        dict_map_items = []
        
        for mmi in mm.map_items:
            item = {}
            min_v = []
            max_v = []
            for miv in mmi.min_value:
                min_v.append(miv)
            for mav in mmi.max_value:
                max_v.append(mav)
            
            item['min_value'] = min_v
            item['max_value'] = max_v
            item['exec_ops_name'] = mmi.exec_ops_name
            item['exec_ops_args'] = mmi.exec_ops_args
            item['map_item_id'] = mmi.map_item_id

            dict_map_items.append(item)

        dict_map['osc_message'] = mm.osc_message
        dict_map['message_type'] = mm.message_type
        dict_map['show_expanded'] = mm.show_expanded
        dict_map['map_id'] = mm.map_id
        dict_map['map_items'] = dict_map_items

        p = Path(filepath)

        with p.open('w') as f:
            json.dump(dict_map, f, indent=3)
        return {'FINISHED'}

    def execute(self, context):
        return self.write_json_data(context, self.filepath)


# MessageMapItemを追加
class IFJ_OT_AddMessageMapItem(bpy.types.Operator):

    bl_idname = 'ifj.add_message_map_item'
    bl_label = 'Add Message Map Item'
    bl_description = '実行するオペレータを1つ追加'

    selected_map: bpy.props.IntProperty(default=0)

    def execute(self, context):
        mm = context.window_manager.cmc_messagemaps
        newItem = mm[self.selected_map].map_items.add()
        for i, mmi in enumerate(mm[self.selected_map].map_items):
            mmi.map_item_id = i
        
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)



# MessageMapItemを削除
class IFJ_OT_RemoveMessageMapItem(bpy.types.Operator):

    bl_idname = 'ifj.remove_message_map_item'
    bl_label = 'Remove Message Map Item'
    bl_description = '実行するオペレータを1つ削除'

    selected_map: bpy.props.IntProperty(default=0)
    selected_map_item: bpy.props.IntProperty(default=0)

    def execute(self, context):
        mmi = context.window_manager.cmc_messagemaps[self.selected_map].map_items
        mmi.remove( self.selected_map_item )

        for i, mmi in enumerate(mmi):
            mmi.map_item_id = i
        
        print(self.selected_map, self.selected_map_item)
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)



# MessageMapItemの入れ替え
class IFJ_OT_MoveMessageMapItem(bpy.types.Operator):

    bl_idname = 'ifj.move_message_map_item'
    bl_label = 'Move Message Map Item'
    bl_description = '実行するオペレータを1つ前か後ろに移動'

    selected_map: bpy.props.IntProperty(default=0)
    selected_map_item: bpy.props.IntProperty(default=0)
    direction: bpy.props.BoolProperty(default=True)

    def execute(self, context):
        mmi = context.window_manager.cmc_messagemaps[self.selected_map].map_items

        if self.direction:
            mmi.move( self.selected_map_item,  self.selected_map_item+1)
        else:
            mmi.move( self.selected_map_item,  self.selected_map_item-1)

        for i, mmi in enumerate(mmi):
            mmi.map_item_id = i
        return {'FINISHED'}
    
    def invoke(self, context, event):
        return self.execute(context)





# Message Maps(各モジュ―ルに対するbpy.opsへのマッピング情報)をJSON形式にして保存
class IFJ_OT_SaveMessageMaps(bpy.types.Operator, ExportHelper):

    bl_idname = 'ifj.save_message_maps'
    bl_label = 'Save Settings File'
    bl_description = 'モジュールマップを保存'

    filename_ext = '.json'

    filter_glob: bpy.props.StringProperty(
        default='*.json',
        options={'HIDDEN'},
        maxlen=255,
    )

    def write_json_data(self, context, filepath):
        mms_dict = OrderedDict()
        mms = context.window_manager.cmc_messagemaps
        context.preferences.addons[__package__].preferences.settings_file_path = filepath
        if context.preferences.addons[__package__].preferences.settings_file_path == '':
            bpy.ops.ifj.get_filepath('INVOKE_DEFAULT')

        for i, mm in  enumerate(mms):
            dict_map = {}
            dict_map_items = []
            
            for mmi in mm.map_items:
                item = {}
                min_v = []
                max_v = []
                for miv in mmi.min_value:
                    min_v.append(miv)
                for mav in mmi.max_value:
                    max_v.append(mav)
                
                item['min_value'] = min_v
                item['max_value'] = max_v
                item['exec_ops_name'] = mmi.exec_ops_name
                item['exec_ops_args'] = mmi.exec_ops_args
                item['map_item_id'] = mmi.map_item_id

                dict_map_items.append(item)

            dict_map['osc_message'] = mm.osc_message
            dict_map['message_type'] = mm.message_type
            dict_map['show_expanded'] = mm.show_expanded
            dict_map['map_id'] = mm.map_id
            dict_map['map_items'] = dict_map_items

            mms_dict[i]=dict_map
        
        p = Path(context.preferences.addons[__package__].preferences.settings_file_path)

        with p.open('w') as f:
            json.dump(mms_dict, f, indent=4)
        return {'FINISHED'}

    def execute(self, context):
        return self.write_json_data(context, self.filepath)


# Message MapsのJSONファイルを開く
class IFJ_OT_OpenMessageMaps(bpy.types.Operator, ImportHelper):

    bl_idname = 'ifj.open_message_maps'
    bl_label = 'Open Settings File'
    bl_description = 'モジュールマップを開く'

    # ImportHelper mixin class uses this
    filename_ext = '.json'

    filter_glob: bpy.props.StringProperty(
        default='*.json',
        options={'HIDDEN'},
        maxlen=255,
    )
    def open_json_data(self, context, filepath):
        bpy.ops.ifj.load_message_maps(filepath=filepath)
        return {'FINISHED'}

    def execute(self, context):
        return self.open_json_data(context, self.filepath)



# JSONファイルからMessageMapを復元
class IFJ_OT_LoadMessageMaps(bpy.types.Operator):

    bl_idname = 'ifj.load_message_maps'
    bl_label = 'Load Message Maps'
    bl_description = 'モジュールマップを復元'

    filepath:bpy.props.StringProperty(
        default='',
        options={'HIDDEN'},
        maxlen=255
    )

    def execute(self, context):
        if self.filepath != '':
            p = Path(self.filepath)
        elif context.preferences.addons[__package__].preferences.settings_file_path != '':
            p = Path(context.preferences.addons[__package__].preferences.settings_file_path)
        else:
            return {'FINISHED'}
        
        mms_dict = OrderedDict()
        mms = context.window_manager.cmc_messagemaps
        mms.clear()

        if not p.exists():
            return {'FINISHED'}

        with p.open() as f:
            mms_dict = json.load(f)

        for mm in mms_dict.values():
            message_map = mms.add()
            message_map.osc_message = mm['osc_message']
            message_map.message_type = mm['message_type']
            message_map.show_expanded = mm['show_expanded']
            message_map.map_id = mm['map_id']

            for mmi in mm['map_items']:
                item = message_map.map_items.add()
                item.min_value = mmi['min_value']
                item.max_value = mmi['max_value']
                item.exec_ops_name = mmi['exec_ops_name']
                item.exec_ops_args = mmi['exec_ops_args']
                item.map_item_id = mmi['map_item_id']
        return {'FINISHED'}



# PCのIPアドレスを取得
class IFJ_OT_GetIPAddress(bpy.types.Operator):

    bl_idname = 'ifj.get_ipaddress'
    bl_label = 'Get IP Address'
    bl_description = 'IPアドレスを取得'

    def execute(self, context):
        ip = socket.gethostbyname(socket.gethostname())
        print(ip)
        context.preferences.addons[__package__].preferences.port_address = ip
        
        return {'FINISHED'}
