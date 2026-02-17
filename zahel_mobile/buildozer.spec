[app]

# Titre
title = ZAHEL Transport

# Package
package.name = zahel.transport
package.domain = com.zahel

# Version
version = 1.0.0

# Dossier source (MAINTENANT on est DANS zahel_mobile)
source.dir = .
source.include_exts = py,png,jpg,kv,json,txt,db
source.exclude_exts = spec
source.exclude_dirs = tests, bin, .git, __pycache__, cache, env_zahel

# Point d'entrée (IMPORTANT !)
orientation = portrait
fullscreen = 0

# Android
android.arch = armeabi-v7a
android.minapi = 21
android.sdk = 23
android.ndk = 23b
android.ndk_api = 21

# Permissions
android.permissions = INTERNET,ACCESS_FINE_LOCATION,ACCESS_COARSE_LOCATION,ACCESS_NETWORK_STATE

# Python
python.version = 3.9

# Chemin de build
build.dir = C:/Users/USER/Desktop/zahel/build
bin.dir = C:/Users/USER/Desktop/zahel/bin

# Icône
icon.filename = assets/icon.png

# Dépendances SIMPLIFIÉES
requirements = python3,kivy==2.3.0,requests,pillow,kivy_garden.mapview

# Options
android.accept_sdk_license = True
android.wakelock = True
android.orientation = portrait
log_level = 2