[app]
title = KANCHI AI
package.name = kanchi
package.domain = com.kanchi.ai
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json
version = 1.0
version.regex = __version__ = ['"]([^'"]*)['"]
version.filename = %(source.dir)s/main.py
requirements = python3,kivy==2.2.0,plyer,pyjnius
orientation = portrait
fullscreen = 0
android.permissions = INTERNET,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,CAMERA,RECORD_AUDIO,CALL_PHONE,SEND_SMS,READ_CONTACTS,WAKE_LOCK,FOREGROUND_SERVICE,VIBRATE,FLASHLIGHT
android.api = 33
android.minapi = 21
android.ndk = 25b
android.sdk = 33
android.accept_sdk_license_agreements = True
android.ant = auto
p4a.branch = v2023.12.24
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
