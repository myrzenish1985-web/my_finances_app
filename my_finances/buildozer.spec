[app]

# (str) Title of your application
title = Мои финансы

# (str) Package name
package.name = myfinances

# (str) Package domain (needed for android/ios packaging)
package.domain = org.myfinances

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,atlas,ttf,txt,json,db,spec

# (list) List of inclusions using pattern matching
#source.include_patterns = assets/*, images/*.png

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin, .buildozer, .git, __pycache__

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license, images/*/.jpg

# (str) Application versioning (method 1)
version = 1.0.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3==3.10.12,kivy==2.1.0,kivymd==1.1.1,plyer,sqlite3,android,pyjnius,requests,Pillow

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
icon.filename = icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
android.permissions = INTERNET, WRITE_EXTERNAL_STORAGE, READ_EXTERNAL_STORAGE

# (int) Android API to use
android.api = 33

# (int) Minimum API required
android.minapi = 21

# (int) Android SDK version
android.sdk = 33

# (str) Android NDK version
android.ndk = 23b

# (int) Android NDK API to use
android.ndk_api = 21

# (bool) Use --private data storage instead of --dir
android.private_storage = True

# (str) Android arch
android.arch = arm64-v8a

# (str) bootstrap mode for android
p4a.bootstrap = sdl2

# (bool) If True, then opens debug log
android.debug = 1

# (bool) If True, then logcat logs are redirected to stdout
android.logcat_filters = *:S python:D

# (bool) If True, then sort the java files by package name
android.gradle_plugin_offline = False

# (str) Android logcat filters to use
#android.logcat_filters = *:S python:D

# (str) Android additional Java arguments
#android.add_java_args = -Xmx2048M

# (bool) Enable AndroidX support
android.enable_androidx = True

# (bool) Enable the Android Keystore
#android.keystore = 

# (str) Private key for the Android Keystore
#android.private_key = 

# (str) Certificate for the Android Keystore
#android.certificate = 

# (str) The Android Java source directory
#android.add_src = 

# (str) The Android Java assets directory
#android.add_assets = 

# (str) The Android Java AIDL directory
#android.add_aidl = 

# (str) The Android Java JAR directory
#android.add_jar = 

# (bool) Use the Android NDK toolchain instead of the standalone toolchain
android.use_ndk_toolchain = True

# (str) The Java source directory for the Android Gradle project
#android.gradle_source_dir = 

# (str) The Java build directory for the Android Gradle project
#android.gradle_build_dir = 

# (str) The path to the Android Gradle project
#android.gradle_project_dir = 

# (str) The path to the Android Gradle project properties file
#android.gradle_properties_file = 

# (str) The path to the Android Gradle project wrapper
#android.gradle_wrapper = 

# (bool) If True, then use the Android Gradle project wrapper
#android.use_gradle_wrapper = True

# (str) The path to the Java source directory for the Android Gradle project
#android.gradle_source_dir = 

# (str) The path to the Java build directory for the Android Gradle project
#android.gradle_build_dir = 

# (str) The path to the Android Gradle project
#android.gradle_project_dir = 

# (list) The list of Android Gradle project dependencies
#android.gradle_dependencies = 

# (list) The list of Android Gradle project repositories
#android.gradle_repositories = 

# (str) The path to the Android NDK
#android.ndk_path = 

# (str) The path to the Android SDK
#android.sdk_path = 

# (str) The path to the Android ANT
#android.ant_path = 

# (bool) If True, then use the Android ANT build
#android.use_ant = False

# (bool) If True, then use the Android SDK build
#android.use_sdk = True

# (bool) If True, then use the Android NDK build
#android.use_ndk = True

# (bool) If True, then use the Android AAPT2
#android.use_aapt2 = True

# (list) The list of Java classes to add to the Android project
#android.add_java = 

# (list) The list of Java packages to add to the Android project
#android.add_packages = 

# (list) The list of Java activities to add to the Android project
#android.add_activities = 

# (bool) If True, then use the Android Gradle build
p4a.android_gradle = True

# (str) The Android Gradle build type (debug/release)
p4a.android_gradle_build_type = debug

# (str) The Android Gradle build flavor
#p4a.android_gradle_build_flavor = 

# (bool) If True, then use the Android Gradle build with the offline mode
p4a.android_gradle_offline = False

# (str) The Android Gradle build directory
#p4a.android_gradle_build_dir = 

# (str) The path to the Android Gradle project
#p4a.android_gradle_project_dir = 

# (str) The Android Gradle project properties file
#p4a.android_gradle_properties_file = 

# (str) The Android Gradle project wrapper
#p4a.android_gradle_wrapper = 

# (bool) If True, then use the Android Gradle project wrapper
p4a.use_gradle_wrapper = False

# (list) The list of Android Gradle project dependencies
#p4a.gradle_dependencies = 

# (list) The list of Android Gradle project repositories
#p4a.gradle_repositories = 

# (str) The path to the Android NDK
#p4a.ndk_path = 

# (str) The path to the Android SDK
#p4a.sdk_path = 

# (str) The path to the Android ANT
#p4a.ant_path = 

# (bool) If True, then use the Android ANT build
#p4a.use_ant = False

# (bool) If True, then use the Android SDK build
#p4a.use_sdk = True

# (bool) If True, then use the Android NDK build
#p4a.use_ndk = True

# (bool) If True, then use the Android AAPT2
#p4a.use_aapt2 = True

# (list) The list of Java classes to add to the Android project
#p4a.add_java = 

# (list) The list of Java packages to add to the Android project
#p4a.add_packages = 

# (list) The list of Java activities to add to the Android project
#p4a.add_activities = 

# (str) The Android package name (e.g. org.myfinances.myapp)
#p4a.package_name = 

# (str) The Android package domain (e.g. org.myfinances)
#p4a.package_domain = 

# (str) The Android application version (e.g. 1.0.0)
#p4a.version = 

# (str) The Android application version code (e.g. 1)
#p4a.version_code = 

# (str) The Android application icon
#p4a.icon = 

# (str) The Android application presplash
#p4a.presplash = 

# (str) The Android application permission
#p4a.permission = 

# (str) The Android application orientation
#p4a.orientation = 

# (str) The Android application fullscreen
#p4a.fullscreen = 

# (str) The Android application window
#p4a.window = 

# (str) The Android application blacklist
#p4a.blacklist = 

# (str) The Android application whitelist
#p4a.whitelist = 

# (str) The Android application meta data
#p4a.meta_data = 

# (str) The Android application custom data
#p4a.custom_data = 

# (str) The Android application service
#p4a.service = 

# (str) The Android application receiver
#p4a.receiver = 

# (str) The Android application activity
#p4a.activity = 

# (str) The Android application intent filter
#p4a.intent_filter = 

# (str) The Android application library
#p4a.library = 

# (str) The Android application asset
#p4a.asset = 

# (str) The Android application resource
#p4a.resource = 

# (str) The Android application source
#p4a.source = 

# (str) The Android application AIDL
#p4a.aidl = 

# (str) The Android application JAR
#p4a.jar = 

# (str) The Android application Gradle dependency
#p4a.gradle_dependency = 

# (str) The Android application Gradle repository
#p4a.gradle_repository = 

# (str) The Android application Gradle plugin
#p4a.gradle_plugin = 

# (str) The Android application Gradle project
#p4a.gradle_project = 

# (str) The Android application Gradle build
#p4a.gradle_build = 

# (str) The Android application Gradle build type
#p4a.gradle_build_type = 

# (str) The Android application Gradle build flavor
#p4a.gradle_build_flavor = 

# (bool) If True, then use the Android Gradle build
#p4a.use_gradle = True

# (bool) If True, then use the Android Gradle build with the offline mode
#p4a.gradle_offline = False

# (str) The Android application Gradle build directory
#p4a.gradle_build_dir = 

# (str) The Android application Gradle project directory
#p4a.gradle_project_dir = 

# (str) The Android application Gradle properties file
#p4a.gradle_properties_file = 

# (str) The Android application Gradle wrapper
#p4a.gradle_wrapper = 

# (bool) If True, then use the Android Gradle project wrapper
#p4a.use_gradle_wrapper = False

[buildozer]

# (str) Path to buildozer global directory (default: ~/.buildozer)
#buildozer_dir = /home/user/.buildozer

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (bool) Wether to warn if root is used (sudo) with buildozer
warn_on_root = 1

# (bool) Enable build in a docker container
#build_in_docker = False

# (str) The docker image to use
#docker_image = 

# (str) The docker command to use
#docker_cmd = docker

# (bool) Enable build in a virtual machine
#build_in_vm = False

# (str) The virtual machine provider to use
#vm_provider = virtualbox

# (str) The virtual machine name to use
#vm_name = buildozer

# (str) The virtual machine snapshot to use
#vm_snapshot = 

# (str) The virtual machine command to use
#vm_cmd = VBoxManage

# (bool) If True, then use the virtual machine GUI
#vm_gui = False

# (str) The path to the virtual machine shared folder
#vm_shared_folder = 

# (str) The path to the virtual machine shared folder mount point
#vm_shared_folder_mount = 

# (str) The virtual machine OS
#vm_os = 

# (str) The virtual machine architecture
#vm_arch = 

# (str) The virtual machine CPU
#vm_cpu = 

# (str) The virtual machine memory
#vm_memory = 

# (str) The virtual machine disk size
#vm_disk_size = 

# (str) The virtual machine network adapter
#vm_network_adapter = 

# (str) The virtual machine network adapter type
#vm_network_adapter_type = 

# (str) The virtual machine network adapter bridge
#vm_network_adapter_bridge = 

# (str) The virtual machine network adapter name
#vm_network_adapter_name = 

# (str) The virtual machine network adapter MAC
#vm_network_adapter_mac = 

# (str) The virtual machine network adapter DHCP
#vm_network_adapter_dhcp = 

# (str) The virtual machine network adapter IP
#vm_network_adapter_ip = 

# (str) The virtual machine network adapter netmask
#vm_network_adapter_netmask = 

# (str) The virtual machine network adapter gateway
#vm_network_adapter_gateway = 

# (str) The virtual machine network adapter DNS
#vm_network_adapter_dns = 

# (str) The virtual machine network adapter hostname
#vm_network_adapter_hostname = 

# (str) The virtual machine network adapter domain
#vm_network_adapter_domain = 

# (str) The virtual machine network adapter search domain
#vm_network_adapter_search_domain = 

# (str) The virtual machine network adapter proxy
#vm_network_adapter_proxy = 

# (str) The virtual machine network adapter proxy port
#vm_network_adapter_proxy_port = 

# (str) The virtual machine network adapter proxy user
#vm_network_adapter_proxy_user = 

# (str) The virtual machine network adapter proxy password
#vm_network_adapter_proxy_password = 

# (str) The virtual machine network adapter proxy bypass
#vm_network_adapter_proxy_bypass = 

# (str) The virtual machine network adapter proxy exclude
#vm_network_adapter_proxy_exclude =