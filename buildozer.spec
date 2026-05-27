[app]

title = Мои финансы
package.name = myfinances
package.domain = org.myfinances
version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json

requirements = python3,kivy==2.1.0,kivymd==1.0.2,sqlite3,Pillow,plyer

orientation = portrait
fullscreen = 0

icon.filename = icon.png

android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 25b
android.ndk_api = 21

android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET
android.enable_androidx = True
android.archs = arm64-v8a

p4a.bootstrap = sdl2
p4a.android_gradle = True

log_level = 2
warn_on_root = 1
