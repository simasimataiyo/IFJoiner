
import bpy
import keyboard

class IFJ_OT_SendKeyPress(bpy.types.Operator):
    bl_idname = 'ifj.send_key_press'
    bl_label = 'send_key_press'
    bl_description = 'simulate keyboard and send key pressed'
    key: bpy.props.StringProperty()

    def execute(self, context):
        keyboard.press(self.key)
        return {'FINISHED'}

class IFJ_OT_SendKeyRelease(bpy.types.Operator):
    bl_idname = 'ifj.send_key_release'
    bl_label = 'send_key_release'
    bl_description = 'simulate keyboard and send key released'

    key: bpy.props.StringProperty()

    def execute(self, context):
        keyboard.release(self.key)
        return {'FINISHED'}

class IFJ_OT_SendKeyPressAndRelease(bpy.types.Operator):
    bl_idname = 'ifj.send_key_press_and_release'
    bl_label = 'send_key_press_and_release'
    bl_description = 'simulate keyboard and send key press_and_released'

    key: bpy.props.StringProperty()

    def execute(self, context):
        keyboard.press_and_release(self.key)
        return {'FINISHED'}