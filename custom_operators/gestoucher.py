
import bpy
import mathutils

class IFJ_OT_UpdateGestoucher(bpy.types.Operator):

    bl_idname = 'ifj.update_gestoucher'
    bl_label = 'update_gestoucher'
    bl_description = 'Gestoucherのループ処理'

    input_value: bpy.props.FloatVectorProperty(size = 7)
    angle_scale: bpy.props.FloatProperty(default = 1.0)
    
    calibrate_quat = mathutils.Quaternion()
    raw_quat = mathutils.Quaternion()
    quat = mathutils.Quaternion()
    pre_quat = mathutils.Quaternion()
    delta_quat = mathutils.Quaternion()
    
    def setQuat(self):
        op_class = IFJ_OT_UpdateGestoucher

        op_class.raw_quat.w = self.input_value[3]
        op_class.raw_quat.x = -self.input_value[5]
        op_class.raw_quat.y = -self.input_value[6]
        op_class.raw_quat.z = -self.input_value[4]

        op_class.quat = op_class.raw_quat @ op_class.calibrate_quat

        if op_class.pre_quat == None:
            op_class.pre_quat = op_class.quat.copy()

        op_class.delta_quat = op_class.quat.rotation_difference(op_class.pre_quat)
        op_class.delta_quat.angle *= self.angle_scale

        # quatをpre_quatに保存
        op_class.pre_quat = op_class.quat.copy()

    def getScreen(self, areas):
         for a in areas:
            if a.type == 'VIEW_3D':
                return a.spaces[0]

    # ビュー座標で操作→ワールド座標に変換
    def to_world_from_view(self, view_matrix, target_matrix, delta_matrix):
        inverted_view_mat = view_matrix.copy()
        inverted_view_mat.invert()

        # view座標系に変換
        to_view = view_matrix @ target_matrix
        # view座標系で操作
        translate = delta_matrix @ to_view
        # view座標を逆行列しておいたものを掛けてワールド座標に戻す
        to_world = inverted_view_mat @ translate
        return to_world

    # カメラの回転
    def rotate_camera(self):
        screen = self.getScreen(bpy.context.screen.areas)
        camera_rot_quat = self.delta_quat
        camera_rot_quat.invert()
        
        if screen != None:
            screen.region_3d.view_rotation = self.to_world_from_view(
                screen.region_3d.view_matrix, 
                screen.region_3d.view_rotation.to_matrix().to_4x4(), 
                camera_rot_quat.to_matrix().to_4x4()
                ).to_quaternion()

    def invoke(self, context, event):
        op_class = IFJ_OT_UpdateGestoucher
        op_class.pre_quat = None
        return {'FINISHED'}

    def execute(self, context):
        self.setQuat()
        self.rotate_camera()
        return {'FINISHED'}


class IFJ_OT_CalibrateGestoucher(bpy.types.Operator):
    bl_idname = 'ifj.calibrate_gestoucher'
    bl_label = 'calibrate_gestoucher'
    bl_description = 'Gestoucherの初期座標を設定'

    input_value: bpy.props.FloatVectorProperty(size = 7)

    def execute(self, context):
        op_update = IFJ_OT_UpdateGestoucher
        op_update.raw_quat.w = self.input_value[3]
        op_update.raw_quat.x = -self.input_value[5]
        op_update.raw_quat.y = -self.input_value[6]
        op_update.raw_quat.z = -self.input_value[4]

        op_update.calibrate_quat = op_update.raw_quat.rotation_difference( mathutils.Quaternion( (0.0, 0.0, 0.0, 1.0) ) )
        # print(op_update.raw_quat)
        # print(op_update.calibrate_quat)
        return {'FINISHED'}