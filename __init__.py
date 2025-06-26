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

# ----------- 通知送信関数（ログ付き）-----------
def send_discord_message(webhook_url, message, props=None):
    try:
        response = requests.post(webhook_url, json={"content": message})
        if response.ok:
            log = "✅ Discord通知成功"
        else:
            log = f"⚠️ Discord通知失敗: ステータス {response.status_code}"
    except Exception as e:
        log = f"❌ Discord通知エラー: {e}"

    print(log)
    if props:
        props.log_message = log


# ----------- タイマーループ関数（ログ対応）-----------
def notifier_timer():
    try:
        props = bpy.context.scene.discord_notifier_props
        if props.enabled and props.webhook_url:
            send_discord_message(props.webhook_url, props.message, props)
            return props.interval * 60.0
        return 60.0
    except Exception as e:
        print(f"⏱ タイマー実行エラー: {e}")
        return 60.0


# ----------- プロパティ定義（ログプロパティ追加）-----------
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
    log_message: bpy.props.StringProperty(
        name="ログメッセージ",
        default="",
        options={'SKIP_SAVE'}
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

        if props.log_message:
            layout.label(text="ログ:")
            layout.label(text=props.log_message)


# ----------- 即時通知ボタン -----------
class DISCORDNOTIFIER_OT_send_now(bpy.types.Operator):
    bl_idname = "discord.send_now"
    bl_label = "今すぐ通知を送信"

    def execute(self, context):
        props = context.scene.discord_notifier_props
        send_discord_message(props.webhook_url, props.message, props)
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
