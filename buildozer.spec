[app]

title = ZAHEL
package.name = zaheltransport
package.domain = com.zahel

version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,html,txt
source.exclude_dirs = __pycache__, zahel_mobile, backend, database, env_zahel

android.arch = arm64-v8a
android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION
android.minapi = 21
android.sdk = 34
android.ndk = 25c

orientation = portrait
fullscreen = 0

requirements = python3,kivy==2.2.1,requests,plyer,pillow,sentry-sdk

icon.filename = assets/icon.png

log.level = 2
build.clean_build = True
android.accept_sdk_license = True
android.debug = True
