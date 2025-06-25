bl_info = {
    "name": "Discord Reminder Notifier",
    "author": "Clothica",
    "version": (1, 0, 0),
    "blender": (4, 2, 0),
    "location": "3D View > Sidebar > Discord Notifier",
    "description": "Send periodic notifications to Discord via webhook while working in Blender.",
    "category": "3D View"
}

import bpy
import requests

# ----------- 通知送信関数 -----------
def send_discord_message(webhook_url, message):
    try:
        requests.post(webhook_url, json={"content": message})
    except Exception as e:
        print(f"❌ Discord通知エラー: {e}")

# ----------- タイマーループ関数 -----------
def notifier_timer():
    scene = bpy.context.scene
    props = scene.discord_notifier_props

    if props.enabled and props.webhook_url:
        send_discord_message(props.webhook_url, props.message)
        return props.interval * 60  # 次の通知までの秒数
    return None  # タイマー停止

# ----------- プロパティ定義 -----------
class DiscordNotifierProperties(bpy.types.PropertyGroup):
    webhook_url: bpy.props.StringProperty(
        name="Discord Webhook URL",
        description="通知先のWebhook URL",
        default=""
    )
    interval: bpy.props.IntProperty(
        name="通知間隔（分）",
        description="通知を送る時間間隔（分）",
        default=30, min=1, max=240
    )
    message: bpy.props.StringProperty(
        name="通知メッセージ",
        default="Blender作業中です！"
    )
    enabled: bpy.props.BoolProperty(
        name="通知を有効にする",
        default=False
    )

# ----------- UIパネル -----------
class DISCORDNOTIFIER_PT_panel(bpy.types.Panel):
    bl_label = "Discord通知"
    bl_idname = "DISCORDNOTIFIER_PT_panel"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "Discord Notifier"

    def draw(self, context):
        layout = self.layout
        props = context.scene.discord_notifier_props

        layout.prop(props, "enabled")
        layout.prop(props, "webhook_url")
        layout.prop(props, "interval")
        layout.prop(props, "message")
        layout.operator("discord.send_now", text="今すぐ通知")

# ----------- 即時通知ボタン -----------
class DISCORDNOTIFIER_OT_send_now(bpy.types.Operator):
    bl_idname = "discord.send_now"
    bl_label = "今すぐ通知を送信"

    def execute(self, context):
        props = context.scene.discord_notifier_props
        send_discord_message(props.webhook_url, props.message)
        self.report({'INFO'}, "通知を送信しました")
        return {'FINISHED'}

# ----------- 登録処理 -----------
classes = (
    DiscordNotifierProperties,
    DISCORDNOTIFIER_PT_panel,
    DISCORDNOTIFIER_OT_send_now,
)

def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.discord_notifier_props = bpy.props.PointerProperty(type=DiscordNotifierProperties)
    bpy.app.timers.register(notifier_timer, first_interval=10)

def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.discord_notifier_props

if __name__ == "__main__":
    register()
