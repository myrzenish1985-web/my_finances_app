[app]

title = Мои финансы
package.name = myfinances
package.domain = org.myfinances
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json
version = 1.0.0
requirements = python3,kivy==2.1.0,kivymd==1.0.2,plyer,sqlite3,android,pyjnius
orientation = portrait
fullscreen = 0

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 27
android.ndk_api = 21
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE
android.archs = arm64-v8a
android.accept_sdk_license = True
android.p4a_ignore_recipe = jpeg

[buildozer]
log_level = 2
warn_on_root = 1
