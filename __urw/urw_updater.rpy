####################################################################
####            Universal Ren'Py Walkthrough System             ####
####               (C) Knox Emberlyn 2025-2026                  ####
####                 Auto Updater System                        ####
####################################################################

init -10 python:
    import urllib.request
    import urllib.error
    import json
    import threading
    import os
    import zipfile
    import shutil
    import store
    import ssl

    try:
        _urw_ssl_context = ssl.create_default_context()
        _urw_ssl_context.check_hostname = False
        _urw_ssl_context.verify_mode = ssl.CERT_NONE
    except AttributeError:
        _urw_ssl_context = None

    class URWUpdater:
        REPO = "BCassO/universal-renpy-walkthrough"
        API_URL = "https://api.github.com/repos/{}/releases/latest".format(REPO)
        
        def __init__(self):
            self.status = "idle"  # idle, checking, available, up_to_date, downloading, extracting, success, error
            self.message = "Click 'Check for Updates' to verify if a new version is available."
            self.latest_version = None
            self.download_url = None
            
        def reset(self):
            self.status = "idle"
            self.message = "Click 'Check for Updates' to verify if a new version is available."
            
        def check_update_bg(self):
            self.status = "checking"
            self.message = "Checking for updates..."
            renpy.restart_interaction()
            t = threading.Thread(target=self._check_update_thread)
            t.daemon = True
            t.start()
            
        def _check_update_thread(self):
            try:
                req = urllib.request.Request(self.API_URL, headers={'User-Agent': 'URW-Updater'})
                with urllib.request.urlopen(req, timeout=10, context=_urw_ssl_context) as response:
                    data = json.loads(response.read().decode())
                
                tag = data.get("tag_name", "")
                self.latest_version = tag.lstrip('v')
                self.download_url = data.get("zipball_url", "")
                
                current = getattr(store.urw_config, 'VERSION', '0.0.0').lstrip('v')
                
                if self._compare_versions(self.latest_version, current):
                    self.status = "available"
                    self.message = "Version {} is available! (Current: {})".format(self.latest_version, current)
                else:
                    self.status = "up_to_date"
                    self.message = "You are already running the latest version ({}).".format(current)
            except urllib.error.URLError as e:
                self.status = "error"
                self.message = "Network error: {}".format(e.reason)
            except Exception as e:
                self.status = "error"
                self.message = "Failed to check for updates: {}".format(str(e))
            finally:
                renpy.restart_interaction()
                
        def _compare_versions(self, latest, current):
            def parse(v):
                return [int(x) for x in v.split('.') if x.isdigit()]
            return parse(latest) > parse(current)
            
        def download_and_install_bg(self):
            self.status = "downloading"
            self.message = "Downloading update..."
            renpy.restart_interaction()
            t = threading.Thread(target=self._install_thread)
            t.daemon = True
            t.start()
            
        def _install_thread(self):
            # Build folder name dynamically to prevent Ren'Py name mangling
            urw_folder = "_" + "_urw"
            urw_folder_slash = urw_folder + "/"
            search_slash = "/" + urw_folder_slash
            
            try:
                zip_path = os.path.join(renpy.config.basedir, "urw_update.zip")
                req = urllib.request.Request(self.download_url, headers={'User-Agent': 'URW-Updater'})
                with urllib.request.urlopen(req, timeout=30, context=_urw_ssl_context) as response, open(zip_path, 'wb') as out_file:
                    shutil.copyfileobj(response, out_file)
                    
                self.status = "extracting"
                self.message = "Extracting and installing files..."
                renpy.restart_interaction()
                
                game_dir = renpy.config.gamedir
                target_dir = os.path.join(game_dir, urw_folder)
                
                with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                    urw_prefix = None
                    for member in zip_ref.namelist():
                        if search_slash in member or member.startswith(urw_folder_slash):
                            idx = member.find(urw_folder_slash)
                            urw_prefix = member[:idx + len(urw_folder_slash)]
                            break
                            
                    if not urw_prefix:
                        raise Exception("Could not find " + urw_folder + " folder in the downloaded zip.")
                        
                    for member in zip_ref.namelist():
                        if member.startswith(urw_prefix) and not member.endswith('/'):
                            rel_path = member[len(urw_prefix):]
                            dest = os.path.join(target_dir, rel_path)
                            
                            os.makedirs(os.path.dirname(dest), exist_ok=True)
                            with zip_ref.open(member) as source, open(dest, "wb") as target:
                                shutil.copyfileobj(source, target)
                             
                os.remove(zip_path)
                
                self.status = "success"
                self.message = "Update installed successfully! Restart is required."
            except Exception as e:
                self.status = "error"
                self.message = "Installation failed: {}".format(str(e))
                if os.path.exists(os.path.join(renpy.config.basedir, "urw_update.zip")):
                    try:
                        os.remove(os.path.join(renpy.config.basedir, "urw_update.zip"))
                    except:
                        pass
            finally:
                renpy.restart_interaction()

    urw_updater_instance = URWUpdater()

screen URW_updater_screen():
    tag menu
    modal True
    zorder 205
    
    add "#000" alpha 0.0:
        at transform:
            alpha 0.0
            ease 0.3 alpha 0.85
    
    key "game_menu" action Hide("URW_updater_screen", transition=dissolve)
    key "K_ESCAPE" action Hide("URW_updater_screen", transition=dissolve)
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize int(650 * _urw_calc_responsive()['avg_scale'])
        ysize int(350 * _urw_calc_responsive()['avg_scale'])
        background Frame("#1a1a2e", 20, 20)
        padding (int(30 * _urw_calc_responsive()['avg_scale']), int(30 * _urw_calc_responsive()['avg_scale']))
        
        at transform:
            yoffset -60
            alpha 0.0
            ease 0.4 yoffset 0 alpha 1.0
            
        vbox:
            spacing int(20 * _urw_calc_responsive()['avg_scale'])
            xalign 0.5
            
            text "{color=#4fc3f7}{b}URW Auto-Updater{/b}{/color}" size urw_dim(24):
                xalign 0.5
                
            add "#4fc3f7" xsize int(400 * _urw_calc_responsive()['avg_scale']) ysize 2 xalign 0.5
            
            null height int(20 * _urw_calc_responsive()['avg_scale'])
            
            text "{color=#fff}[urw_updater_instance.message]{/color}" size urw_dim(18):
                xalign 0.5
                text_align 0.5
                
            null height int(40 * _urw_calc_responsive()['avg_scale'])
            
            hbox:
                spacing int(20 * _urw_calc_responsive()['avg_scale'])
                xalign 0.5
                
                if urw_updater_instance.status in ["idle", "error", "up_to_date"]:
                    textbutton "Check for Updates":
                        action Function(urw_updater_instance.check_update_bg)
                        background Frame("#2196F3", 8, 8)
                        hover_background Frame("#42A5F5", 8, 8)
                        text_color "#fff"
                        padding (int(15 * _urw_calc_responsive()['avg_scale']), int(10 * _urw_calc_responsive()['avg_scale']))
                        text_size int(16 * _urw_calc_responsive()['avg_scale'])
                
                if urw_updater_instance.status == "available":
                    textbutton "Download & Install":
                        action Function(urw_updater_instance.download_and_install_bg)
                        background Frame("#4CAF50", 8, 8)
                        hover_background Frame("#66BB6A", 8, 8)
                        text_color "#fff"
                        padding (int(15 * _urw_calc_responsive()['avg_scale']), int(10 * _urw_calc_responsive()['avg_scale']))
                        text_size int(16 * _urw_calc_responsive()['avg_scale'])
                        
                if urw_updater_instance.status == "success":
                    textbutton "Restart Game":
                        action Function(renpy.quit, relaunch=True)
                        background Frame("#FF9800", 8, 8)
                        hover_background Frame("#FFB74D", 8, 8)
                        text_color "#fff"
                        padding (int(15 * _urw_calc_responsive()['avg_scale']), int(10 * _urw_calc_responsive()['avg_scale']))
                        text_size int(16 * _urw_calc_responsive()['avg_scale'])
                        
                if urw_updater_instance.status not in ["downloading", "extracting", "checking", "success"]:
                    textbutton "Close":
                        action [Function(urw_updater_instance.reset), Hide("URW_updater_screen", transition=dissolve)]
                        background Frame("#f44336", 8, 8)
                        hover_background Frame("#ef5350", 8, 8)
                        text_color "#fff"
                        padding (int(15 * _urw_calc_responsive()['avg_scale']), int(10 * _urw_calc_responsive()['avg_scale']))
                        text_size int(16 * _urw_calc_responsive()['avg_scale'])
