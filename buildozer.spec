[app]

# Application metadata
title = Excuse Generator
package.name = excuseapp
package.domain = com.mhmdaslam
source.dir = .
source.include_exts = py,png,jpg,json,kv,ttf
version = 1.0
requirements = 
    python3,
    kivy==2.1.0,
    android,
    pyjnius,
    openssl,
    kivy.garden

# Android specific configurations
android.api = 33
android.minapi = 21
android.ndk = 23b
android.sdk = 24
android.archs = arm64-v8a
osx.python_version = 3
osx.kivy_version = 2.1.0
android.enable_androidx = True
android.allow_backup = False
p4a.branch = 2023.08.04
android.add_src = ./kivy-options.txt
android.permissions = 
    READ_EXTERNAL_STORAGE,
    WRITE_EXTERNAL_STORAGE,
    VIBRATE

# App components
orientation = portrait
fullscreen = 0
presplash.filename = assets/applogo.png
icon.filename = assets/applogo.png

# Build optimization
[buildozer]
log_level = 1
warn_on_root = 1
android.accept_sdk_license = true
android.skip_build_check = True

# Kivy configuration
[app:kivy]
log_level = info
window_icon = assets/applogo.png