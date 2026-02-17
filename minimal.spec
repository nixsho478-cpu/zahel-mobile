[app]

# Titre
title = ZAHEL

# Package
package.name = zahel
package.domain = com.zahel

# Version
version = 1.0

# Source
source.dir = zahel_mobile
source.include_exts = py,png,jpg,kv,json

# Configuration Android
android.arch = armeabi-v7a
android.minapi = 21
android.sdk = 23
android.ndk = 23b

# Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION

# Python
python.version = 3.9

# Requirements SIMPLES
requirements = python3,kivy,requests

# Icône
icon.filename = %(source.dir)s/assets/icon.png