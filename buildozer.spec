[app]

# AJOUTE CES 3 LIGNES :
strategy = reuse
p4a.source_dir = %(source.dir)s
android.skip_update = True

# Titre de l'application
title = ZAHEL 

# Nom du package (UNIQUE - important pour Android)
package.name = zahel.transport.comores
package.domain = com.zahel

# Version
version = 1.0.0

# Dossier source (ton code)
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,db,txt,i18n
source.exclude_exts = spec
source.exclude_dirs = tests, bin, .git, __pycache__, cache, env_zahel, venv, backend, database

# Architecture Android
android.arch = armeabi-v7a

# PERMISSIONS ANDROID (COMPLÈTES POUR MAPBOX)
android.permissions = 
    INTERNET,
    ACCESS_FINE_LOCATION,
    ACCESS_COARSE_LOCATION,
    ACCESS_BACKGROUND_LOCATION,
    ACCESS_NETWORK_STATE,
    ACCESS_WIFI_STATE,
    VIBRATE,
    WAKE_LOCK,
    FOREGROUND_SERVICE,
    WRITE_EXTERNAL_STORAGE,
    READ_EXTERNAL_STORAGE

# CONFIGURATION DES INTENT FILTERS (pour recevoir les localisations WhatsApp)
android.extra_manifest = 
    <activity android:name=".MainActivity">
        <intent-filter>
            <action android:name="android.intent.action.VIEW" />
            <category android:name="android.intent.category.DEFAULT" />
            <data android:scheme="geo" />
        </intent-filter>
        <intent-filter>
            <action android:name="android.intent.action.VIEW" />
            <category android:name="android.intent.category.DEFAULT" />
            <category android:name="android.intent.category.BROWSABLE" />
            <data android:scheme="http" />
            <data android:scheme="https" />
            <data android:host="maps.google.com" />
        </intent-filter>
    </activity>

# Version Android
android.minapi = 21
android.sdk = 31
android.ndk = 25b

# Configuration écran
orientation = portrait
fullscreen = 0
window.size = 360, 640

# Version Python
python.version = 3.9

# Icône (on la créera après)
icon.filename = assets/icon.png

# DÉPENDANCES PYTHON (COMPLÈTES POUR MAPBOX)
requirements = python3,kivy==2.3.0,requests,plyer,pillow,sentry-sdk

# DOSSIER DE CACHE POUR LES TUILES MAPBOX
android.add_authorities = zahel.transport.comores.fileprovider
android.add_activity = 
    org.kivy.android.PythonActivity
    android.permission.WRITE_EXTERNAL_STORAGE

# Pour permettre l'écriture en cache
android.gradle_dependencies = 
    'androidx.core:core:1.12.0',
    'androidx.appcompat:appcompat:1.6.1',
    'com.google.android.material:material:1.11.0'

# PERMETTRE LE CHARGEMENT DES RESSOURCES MAPBOX
android.add_network_security_config = True
android.allow_backup = True
android.debug = True

# POUR LE CACHE DES TUILES
android.storage_path = /sdcard/Android/data/zahel.transport.comores/files

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
