[app]

title = ZAHEL
package.name = zaheltransport
package.domain = com.zahel

version = 1.0.0

source.dir = .
source.include_exts = py,png,jpg,kv,atlas,ttf,json,html,txt
source.exclude_dirs = tests, bin, .git, __pycache__, cache, env_zahel, venv, backend, database, zahel_mobile

android.arch = arm64-v8a

android.permissions = INTERNET, ACCESS_FINE_LOCATION, ACCESS_COARSE_LOCATION
android.minapi = 21
android.sdk = 31
android.ndk = 25b

orientation = portrait
fullscreen = 0
python.version = 3

requirements = python3,kivy==2.3.0,requests,plyer,pillow,sentry-sdk

icon.filename = zahel_mobile/assets/icon.png

log.level = 2
build.clean_build = True

android.accept_sdk_license = True
android.debug = True
