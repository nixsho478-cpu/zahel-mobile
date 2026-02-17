[app]

# AJOUTE CES 3 LIGNES :
strategy = reuse
p4a.source_dir = %(source.dir)s
android.skip_update = True

# Titre de l'application
title = ZAHEL Transport

# Nom du package (UNIQUE - important pour Android)
package.name = zahel.transport.comores
package.domain = com.zahel

# Version
version = 1.0.0

# Dossier source (ton code)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,db,txt
source.exclude_exts = spec
source.exclude_dirs = tests, bin, .git, __pycache__, cache, env_zahel, venv, backend, database

# Architecture Android
android.arch = armeabi-v7a

# PERMISSIONS ANDROID (CRITIQUE)
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION, ACCESS_NETWORK_STATE, ACCESS_WIFI_STATE, VIBRATE, WAKE_LOCK, FOREGROUND_SERVICE

# Version Android
android.minapi = 21
android.sdk = 23
android.ndk = 23b

# Configuration écran
orientation = portrait
fullscreen = 0
window.size = 360, 640

# Version Python
python.version = 3.9

# Dossiers de build
build.dir = C:/Users/USER/Desktop/zahel/build
bin.dir = C:/Users/USER/Desktop/zahel/bin

# Icône (on la créera après)
icon.filename = assets/icon.png

# DÉPENDANCES PYTHON (CRITIQUE POUR ZAHEL)
requirements = 
    python3,
    kivy,
    kivy_garden.mapview,
    requests,
    pillow

# Services Kivy
android.services = org.kivy.android.PythonService

# Thème
android.apptheme = "@android:style/Theme.NoTitleBar"
android.meta_data = 
android.add_src = 

# Licence SDK
android.accept_sdk_license = True

# Nettoyage
build.clean_build = True
build.clean_dirs = True

# Version numérique
android.numeric_version = 1

# Journalisation
log.build = %(bin.dir)s/build.log
log.cmd = %(bin.dir)s/cmd.log

# Options finales
android.wakelock = True
android.orientation = portrait