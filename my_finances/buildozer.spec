[app]

# Основная информация
title = Мои финансы
package.name = myfinances
package.domain = org.myfinances
version = 1.0.0

# Исходники
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,db,json

# ВАЖНО: БЕЗ фиксации версии Python (это работает!)
requirements = python3,kivy==2.1.0,kivymd==1.0.2,sqlite3,Pillow,plyer

# Ориентация
orientation = portrait
fullscreen = 0

# Иконка
icon.filename = icon.png

# Android настройки
android.api = 33
android.minapi = 21
android.sdk = 33
android.ndk = 28c
android.ndk_api = 21

# Разрешения
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET

# AndroidX
android.enable_androidx = True

# Архитектура
android.arch = arm64-v8a

# Bootstrap
p4a.bootstrap = sdl2
p4a.android_gradle = True

# Логи
log_level = 2
warn_on_root = 1
