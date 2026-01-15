####################################################################
####     Universal Ren'Py Walkthrough System v2.0 (Enhanced)    ####
####               (C) Knox Emberlyn 2025-2026                  ####
####                 User Interface & Screens                   ####
####################################################################

init python:
    def _urw_calc_responsive():
        """Calculate responsive UI sizes based on current screen resolution"""
        base_width = config.screen_width
        base_height = config.screen_height
        
        # Reference resolution (1920x1080)
        ref_width = 1920
        ref_height = 1080
        
        scale_x = base_width / ref_width
        scale_y = base_height / ref_height
        avg_scale = (scale_x + scale_y) / 2
        
        return {
            'scale_x': scale_x,
            'scale_y': scale_y,
            'avg_scale': avg_scale,
            'width': base_width,
            'height': base_height,
        }
    
    def urw_dim(reference_size):
        """Convert reference dimension (based on 1920x1080) to current screen size"""
        dims = _urw_calc_responsive()
        return int(reference_size * dims['avg_scale'])

##################################################################
#                URW MAIN PREFERENCES SCREEN                     #
##################################################################

screen URW_preferences():
    tag menu
    modal True
    zorder 200
    
    add "#000" alpha 0.0:
        at transform:
            alpha 0.0
            ease 0.3 alpha 0.85
    
    key "game_menu" action Hide("URW_preferences", transition=dissolve)
    key "K_ESCAPE" action Hide("URW_preferences", transition=dissolve)
    
    frame:
        xalign 0.5
        yalign 0.5
        xmaximum int(800 * _urw_calc_responsive()['avg_scale'])
        ymaximum int(700 * _urw_calc_responsive()['avg_scale'])
        background Frame("#1a1a2e", 20, 20)
        xpadding int(40 * _urw_calc_responsive()['avg_scale'])
        ypadding int(30 * _urw_calc_responsive()['avg_scale'])
        
        at transform:
            yoffset -80
            alpha 0.0
            ease 0.4 yoffset 0 alpha 1.0
        
        vbox:
            spacing int(20 * _urw_calc_responsive()['avg_scale'])
            xalign 0.5
            
            # Header
            vbox:
                spacing int(8 * _urw_calc_responsive()['avg_scale'])
                xalign 0.5
                
                hbox:
                    spacing int(15 * _urw_calc_responsive()['avg_scale'])
                    xalign 0.5
                    
                    text "{color=#4fc3f7}{size=32}{b}URW 2.0{/b}{/size}{/color}":
                        at URW_fade_in
                    
                    text "{color=#81d4fa}{size=32}{b}Walkthrough System{/b}{/size}{/color}":
                        at transform:
                            alpha 0.0
                            pause 0.1
                            ease 0.4 alpha 1.0
                
                text "{color=#90caf9}{size=16}{i}Enhanced Gaming Experience{/i}{/size}{/color}":
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        pause 0.2
                        ease 0.4 alpha 1.0
                
                add "#4fc3f7" xsize 0 ysize 2 xalign 0.5:
                    at transform:
                        xsize 0
                        pause 0.3
                        ease 0.6 xsize int(400 * _urw_calc_responsive()['avg_scale'])
            
            null height int(10 * _urw_calc_responsive()['avg_scale'])
            
            viewport:
                scrollbars "vertical"
                mousewheel True
                xsize int(720 * _urw_calc_responsive()['avg_scale'])
                ysize int(480 * _urw_calc_responsive()['avg_scale'])
                
                vbox:
                    spacing int(25 * _urw_calc_responsive()['avg_scale'])
                    xsize int(700 * _urw_calc_responsive()['avg_scale'])
                    
                    frame:
                        background Frame("#16213e", 15, 15)
                        xfill True
                        padding (int(25 * _urw_calc_responsive()['avg_scale']), int(20 * _urw_calc_responsive()['avg_scale']))
                        
                        at URW_slide_in_left
                        
                        hbox:
                            spacing int(30 * _urw_calc_responsive()['avg_scale'])
                            xalign 0.5
                            
                            vbox:
                                spacing int(5 * _urw_calc_responsive()['avg_scale'])
                                text "{color=#fff}{size=20}{b}Enable Walkthrough{/b}{/size}{/color}"
                                text "{color=#888}{size=12}Toggle walkthrough hints on/off{/size}{/color}"
                            
                            textbutton (_("ENABLED") if persistent.urw_enabled else _("DISABLED")):
                                action ToggleVariable("persistent.urw_enabled")
                                xsize int(140 * _urw_calc_responsive()['avg_scale'])
                                ysize int(45 * _urw_calc_responsive()['avg_scale'])
                                text_size int(16 * _urw_calc_responsive()['avg_scale'])
                                text_xalign 0.5
                                if persistent.urw_enabled:
                                    background Frame("#4CAF50", 8, 8)
                                    hover_background Frame("#66BB6A", 8, 8)
                                    text_color "#fff"
                                else:
                                    background Frame("#455a64", 8, 8)
                                    hover_background Frame("#546E7A", 8, 8)
                                    text_color "#aaa"
                    
                    frame:
                        background Frame("#16213e", 15, 15)
                        xfill True
                        padding (int(25 * _urw_calc_responsive()['avg_scale']), int(20 * _urw_calc_responsive()['avg_scale']))
                        
                        at transform:
                            alpha 0.0
                            xoffset 50
                            pause 0.15
                            ease 0.4 alpha 1.0 xoffset 0
                        
                        vbox:
                            spacing int(20 * _urw_calc_responsive()['avg_scale'])
                            
                            text "{color=#4fc3f7}{size=18}{b}📐 Display Settings{/b}{/size}{/color}"
                            
                            vbox:
                                spacing int(10 * _urw_calc_responsive()['avg_scale'])
                                
                                hbox:
                                    spacing int(15 * _urw_calc_responsive()['avg_scale'])
                                    
                                    text "{color=#fff}{size=16}Text Size:{/size}{/color}"
                                    text "{color=#4fc3f7}{size=18}{b}[persistent.urw_text_size]{/b}{/size}{/color}"
                                
                                hbox:
                                    spacing int(10 * _urw_calc_responsive()['avg_scale'])
                                    xalign 0.5
                                    
                                    textbutton "−":
                                        action If(persistent.urw_text_size is not None and persistent.urw_text_size > 12, 
                                                SetVariable("persistent.urw_text_size", persistent.urw_text_size - 2))
                                        style "URW_size_button"
                                        text_size int(24 * _urw_calc_responsive()['avg_scale'])
                                        xsize int(40 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(40 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                    
                                    bar:
                                        value VariableValue("persistent.urw_text_size", range=40, style="URW_slider")
                                        xsize int(350 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(20 * _urw_calc_responsive()['avg_scale'])
                                        left_bar Frame("#4fc3f7", 5, 5)
                                        right_bar Frame("#333", 5, 5)
                                        thumb None
                                    
                                    textbutton "+":
                                        action If(persistent.urw_text_size is not None and persistent.urw_text_size < 40, 
                                                SetVariable("persistent.urw_text_size", persistent.urw_text_size + 2))
                                        style "URW_size_button"
                                        text_size int(24 * _urw_calc_responsive()['avg_scale'])
                                        xsize int(40 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(40 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    xalign 0.5
                                    
                                    text "{color=#888}{size=12}Quick:{/size}{/color}":
                                        yalign 0.5
                                    
                                    for size in [14, 18, 22, 25, 30, 35]:
                                        textbutton "[size]":
                                            action SetVariable("persistent.urw_text_size", size)
                                            xsize int(40 * _urw_calc_responsive()['avg_scale'])
                                            ysize int(28 * _urw_calc_responsive()['avg_scale'])
                                            text_size int(12 * _urw_calc_responsive()['avg_scale'])
                                            text_xalign 0.5
                                            if persistent.urw_text_size == size:
                                                background Frame("#4fc3f7", 5, 5)
                                                text_color "#000"
                                            else:
                                                background Frame("#333", 5, 5)
                                                text_color "#aaa"
                                            hover_background Frame("#5fd3f7", 5, 5)
                            
                            vbox:
                                spacing int(10 * _urw_calc_responsive()['avg_scale'])
                                
                                hbox:
                                    spacing int(15 * _urw_calc_responsive()['avg_scale'])
                                    
                                    text "{color=#fff}{size=16}Max Consequences:{/size}{/color}"
                                    text "{color=#4fc3f7}{size=18}{b}[persistent.urw_max_consequences]{/b}{/size}{/color}"
                                
                                hbox:
                                    spacing int(10 * _urw_calc_responsive()['avg_scale'])
                                    xalign 0.5
                                    
                                    textbutton "−":
                                        action If(persistent.urw_max_consequences > 1, 
                                                SetVariable("persistent.urw_max_consequences", persistent.urw_max_consequences - 1))
                                        style "URW_size_button"
                                        text_size int(24 * _urw_calc_responsive()['avg_scale'])
                                        xsize int(40 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(40 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                    
                                    bar:
                                        value VariableValue("persistent.urw_max_consequences", range=10, style="URW_slider")
                                        xsize int(250 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(20 * _urw_calc_responsive()['avg_scale'])
                                        left_bar Frame("#4fc3f7", 5, 5)
                                        right_bar Frame("#333", 5, 5)
                                        thumb None
                                    
                                    textbutton "+":
                                        action If(persistent.urw_max_consequences < 10, 
                                                SetVariable("persistent.urw_max_consequences", persistent.urw_max_consequences + 1))
                                        style "URW_size_button"
                                        text_size int(24 * _urw_calc_responsive()['avg_scale'])
                                        xsize int(40 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(40 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    xalign 0.5
                                    
                                    text "{color=#888}{size=12}Quick:{/size}{/color}":
                                        yalign 0.5
                                    
                                    for count in [1, 2, 3, 5, 8, 10]:
                                        textbutton "[count]":
                                            action SetVariable("persistent.urw_max_consequences", count)
                                            xsize int(35 * _urw_calc_responsive()['avg_scale'])
                                            ysize int(28 * _urw_calc_responsive()['avg_scale'])
                                            text_size int(12 * _urw_calc_responsive()['avg_scale'])
                                            text_xalign 0.5
                                            if persistent.urw_max_consequences == count:
                                                background Frame("#4fc3f7", 5, 5)
                                                text_color "#000"
                                            else:
                                                background Frame("#333", 5, 5)
                                                text_color "#aaa"
                                            hover_background Frame("#5fd3f7", 5, 5)
                            
                            # Show All Toggle
                            hbox:
                                spacing int(20 * _urw_calc_responsive()['avg_scale'])
                                xalign 0.5
                                
                                vbox:
                                    spacing int(3 * _urw_calc_responsive()['avg_scale'])
                                    text "{color=#fff}{size=16}Show All Consequences:{/size}{/color}"
                                    text "{color=#888}{size=11}When enabled, ignores max limit{/size}{/color}"
                                
                                textbutton (_("ON") if persistent.urw_show_all else _("OFF")):
                                    action ToggleVariable("persistent.urw_show_all")
                                    xsize int(70 * _urw_calc_responsive()['avg_scale'])
                                    ysize int(35 * _urw_calc_responsive()['avg_scale'])
                                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                                    text_xalign 0.5
                                    if persistent.urw_show_all:
                                        background Frame("#4fc3f7", 5, 5)
                                        text_color "#000"
                                    else:
                                        background Frame("#455a64", 5, 5)
                                        text_color "#aaa"
                                    hover_background Frame("#5fd3f7", 5, 5)
                            
                            # Full Text Toggle
                            hbox:
                                spacing int(20 * _urw_calc_responsive()['avg_scale'])
                                xalign 0.5
                                
                                vbox:
                                    spacing int(3 * _urw_calc_responsive()['avg_scale'])
                                    text "{color=#fff}{size=16}Full Text Display:{/size}{/color}"
                                    text "{color=#888}{size=11}Show complete text without truncation{/size}{/color}"
                                
                                textbutton (_("ON") if persistent.urw_full_text else _("OFF")):
                                    action ToggleVariable("persistent.urw_full_text")
                                    xsize int(70 * _urw_calc_responsive()['avg_scale'])
                                    ysize int(35 * _urw_calc_responsive()['avg_scale'])
                                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                                    text_xalign 0.5
                                    if persistent.urw_full_text:
                                        background Frame("#4fc3f7", 5, 5)
                                        text_color "#000"
                                    else:
                                        background Frame("#455a64", 5, 5)
                                        text_color "#aaa"
                                    hover_background Frame("#5fd3f7", 5, 5)
                    
                    # Theme Section
                    frame:
                        background Frame("#16213e", 15, 15)
                        xfill True
                        padding (25, 20)
                        
                        at transform:
                            alpha 0.0
                            xoffset -50
                            pause 0.3
                            ease 0.4 alpha 1.0 xoffset 0
                        
                        vbox:
                            spacing 15
                            
                            text "{color=#4fc3f7}{size=18}{b}🎨 Theme{/b}{/size}{/color}"
                            
                            hbox:
                                spacing 15
                                xalign 0.5
                                
                                for theme_name in ["modern", "classic", "minimal", "dark"]:
                                    textbutton theme_name.capitalize():
                                        action SetVariable("persistent.urw_theme", theme_name)
                                        xsize 120
                                        ysize 40
                                        text_size 14
                                        text_xalign 0.5
                                        if persistent.urw_theme == theme_name:
                                            background Frame("#4fc3f7", 8, 8)
                                            text_color "#000"
                                        else:
                                            background Frame("#333", 8, 8)
                                            text_color "#aaa"
                                        hover_background Frame("#5fd3f7", 8, 8)
                            
                            # Theme preview
                            frame:
                                background "#0d1117"
                                xfill True
                                padding (15, 10)
                                
                                $ _theme = urw_formatter.THEMES.get(persistent.urw_theme, urw_formatter.THEMES['modern'])
                                
                                text "{size=14}{color=" + _theme['increase'] + "}+trust{/color} | {color=" + _theme['decrease'] + "}-money{/color} | {color=" + _theme['assign'] + "}mood=happy{/color} | {color=" + _theme['condition'] + "}? if choice{/color}{/size}":
                                    xalign 0.5
                    
                    # Advanced Settings Button
                    frame:
                        background Frame("#16213e", 15, 15)
                        xfill True
                        padding (25, 20)
                        
                        at transform:
                            alpha 0.0
                            pause 0.45
                            ease 0.4 alpha 1.0
                        
                        vbox:
                            spacing 15
                            xalign 0.5
                            
                            text "{color=#4fc3f7}{size=18}{b}⚙️ Advanced Options{/b}{/size}{/color}":
                                xalign 0.5
                            
                            hbox:
                                spacing 20
                                xalign 0.5
                                
                                textbutton "🔧 Filters":
                                    action Show("URW_filters", transition=dissolve)
                                    xsize int(130 * _urw_calc_responsive()['avg_scale'])
                                    ysize int(45 * _urw_calc_responsive()['avg_scale'])
                                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                                    text_xalign 0.5
                                    background Frame("#2196F3", 8, 8)
                                    hover_background Frame("#42A5F5", 8, 8)
                                    text_color "#fff"
                                
                                textbutton "📊 Stats":
                                    action Show("URW_stats_screen", transition=dissolve)
                                    xsize int(120 * _urw_calc_responsive()['avg_scale'])
                                    ysize int(45 * _urw_calc_responsive()['avg_scale'])
                                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                                    text_xalign 0.5
                                    background Frame("#9C27B0", 8, 8)
                                    hover_background Frame("#AB47BC", 8, 8)
                                    text_color "#fff"
                                
                                textbutton "📋 Full Viewer":
                                    action Show("URW_full_viewer", transition=dissolve)
                                    xsize int(150 * _urw_calc_responsive()['avg_scale'])
                                    ysize int(45 * _urw_calc_responsive()['avg_scale'])
                                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                                    text_xalign 0.5
                                    background Frame("#00BCD4", 8, 8)
                                    hover_background Frame("#26C6DA", 8, 8)
                                    text_color "#fff"
                                
                                if urw_config.DEVELOPER:
                                    textbutton "🔍 Debug":
                                        action Show("URW_debug", transition=dissolve)
                                        xsize int(120 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(45 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(14 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        background Frame("#FF5722", 8, 8)
                                        hover_background Frame("#FF7043", 8, 8)
                                        text_color "#fff"
            
            # Footer
            hbox:
                spacing int(20 * _urw_calc_responsive()['avg_scale'])
                xalign 0.5
                
                at transform:
                    alpha 0.0
                    pause 0.6
                    ease 0.4 alpha 1.0
                
                textbutton "Close":
                    action Hide("URW_preferences", transition=dissolve)
                    xsize int(120 * _urw_calc_responsive()['avg_scale'])
                    ysize int(45 * _urw_calc_responsive()['avg_scale'])
                    text_size int(16 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background Frame("#4fc3f7", 8, 8)
                    hover_background Frame("#5fd3f7", 8, 8)
                    text_color "#000"
                
                textbutton "Reset All":
                    action [
                        SetVariable("persistent.urw_text_size", 25),
                        SetVariable("persistent.urw_max_consequences", 3),
                        SetVariable("persistent.urw_show_all", True),
                        SetVariable("persistent.urw_full_text", False),
                        SetVariable("persistent.urw_theme", "modern"),
                    ]
                    xsize int(120 * _urw_calc_responsive()['avg_scale'])
                    ysize int(45 * _urw_calc_responsive()['avg_scale'])
                    text_size int(16 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background Frame("#f44336", 8, 8)
                    hover_background Frame("#ef5350", 8, 8)
                    text_color "#fff"

##################################################################
#                URW FILTERS SCREEN                              #
##################################################################

screen URW_filters():
    tag menu
    modal True
    zorder 201
    
    add "#000" alpha 0.0:
        at transform:
            alpha 0.0
            ease 0.3 alpha 0.9
    
    key "game_menu" action Hide("URW_filters", transition=dissolve)
    key "K_ESCAPE" action Hide("URW_filters", transition=dissolve)
    
    frame:
        xalign 0.5
        yalign 0.5
        xmaximum int(850 * _urw_calc_responsive()['avg_scale'])
        ymaximum int(650 * _urw_calc_responsive()['avg_scale'])
        background Frame("#1a1a2e", 20, 20)
        xpadding int(35 * _urw_calc_responsive()['avg_scale'])
        ypadding int(25 * _urw_calc_responsive()['avg_scale'])
        
        at transform:
            yoffset -60
            alpha 0.0
            ease 0.4 yoffset 0 alpha 1.0
        
        vbox:
            spacing int(20 * _urw_calc_responsive()['avg_scale'])
            xalign 0.5
            
            vbox:
                spacing int(8 * _urw_calc_responsive()['avg_scale'])
                xalign 0.5
                
                text "{color=#4fc3f7}{size=28}{b}Filter Settings{/b}{/size}{/color}":
                    xalign 0.5
                
                text "{color=#888}{size=14}Customize which consequences are displayed{/size}{/color}":
                    xalign 0.5
                
                add "#4fc3f7" xsize int(300 * _urw_calc_responsive()['avg_scale']) ysize 2 xalign 0.5
            
            viewport:
                scrollbars "vertical"
                mousewheel True
                xsize int(780 * _urw_calc_responsive()['avg_scale'])
                ysize int(450 * _urw_calc_responsive()['avg_scale'])
                
                vbox:
                    spacing int(25 * _urw_calc_responsive()['avg_scale'])
                    xsize int(760 * _urw_calc_responsive()['avg_scale'])
                    
                    # Type Filters
                    frame:
                        background Frame("#16213e", 12, 12)
                        xfill True
                        padding (int(20 * _urw_calc_responsive()['avg_scale']), int(15 * _urw_calc_responsive()['avg_scale']))
                        
                        vbox:
                            spacing int(15 * _urw_calc_responsive()['avg_scale'])
                            
                            text "{color=#fff}{size=18}{b}Consequence Types{/b}{/size}{/color}"
                            
                            grid 3 3:
                                spacing int(15 * _urw_calc_responsive()['avg_scale'])
                                xalign 0.5
                                
                                # Variables
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton "±":
                                        action ToggleDict(persistent.urw_filters, 'variables')
                                        xsize int(35 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(35 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(18 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_filters.get('variables', True):
                                            background "#4CAF50"
                                            text_color "#fff"
                                        else:
                                            background "#444"
                                            text_color "#888"
                                        hover_background "#66BB6A"
                                    text "{color=#ccc}{size=14}Variables{/size}{/color}":
                                        yalign 0.5
                                
                                # Conditions
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton "?":
                                        action ToggleDict(persistent.urw_filters, 'conditions')
                                        xsize int(35 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(35 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(18 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_filters.get('conditions', True):
                                            background "#FFEB3B"
                                            text_color "#000"
                                        else:
                                            background "#444"
                                            text_color "#888"
                                        hover_background "#FFF176"
                                    text "{color=#ccc}{size=14}Conditions{/size}{/color}":
                                        yalign 0.5
                                
                                # Flow
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton "→":
                                        action ToggleDict(persistent.urw_filters, 'flow')
                                        xsize int(35 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(35 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(18 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_filters.get('flow', True):
                                            background "#FF9800"
                                            text_color "#fff"
                                        else:
                                            background "#444"
                                            text_color "#888"
                                        hover_background "#FFB74D"
                                    text "{color=#ccc}{size=14}Flow{/size}{/color}":
                                        yalign 0.5
                                
                                # Functions
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton "ƒ":
                                        action ToggleDict(persistent.urw_filters, 'functions')
                                        xsize int(35 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(35 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(18 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_filters.get('functions', True):
                                            background "#9C27B0"
                                            text_color "#fff"
                                        else:
                                            background "#444"
                                            text_color "#888"
                                        hover_background "#BA68C8"
                                    text "{color=#ccc}{size=14}Functions{/size}{/color}":
                                        yalign 0.5
                                
                                # Flags
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton "◆":
                                        action ToggleDict(persistent.urw_filters, 'flags')
                                        xsize int(35 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(35 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(18 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_filters.get('flags', True):
                                            background "#00BCD4"
                                            text_color "#fff"
                                        else:
                                            background "#444"
                                            text_color "#888"
                                        hover_background "#4DD0E1"
                                    text "{color=#ccc}{size=14}Flags{/size}{/color}":
                                        yalign 0.5
                                
                                # Relationships
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton "♥":
                                        action ToggleDict(persistent.urw_filters, 'relationships')
                                        xsize int(35 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(35 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(18 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_filters.get('relationships', True):
                                            background "#E91E63"
                                            text_color "#fff"
                                        else:
                                            background "#444"
                                            text_color "#888"
                                        hover_background "#F06292"
                                    text "{color=#ccc}{size=14}Relationships{/size}{/color}":
                                        yalign 0.5
                                
                                # Stats
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton "★":
                                        action ToggleDict(persistent.urw_filters, 'stats')
                                        xsize int(35 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(35 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(18 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_filters.get('stats', True):
                                            background "#FF5722"
                                            text_color "#fff"
                                        else:
                                            background "#444"
                                            text_color "#888"
                                        hover_background "#FF8A65"
                                    text "{color=#ccc}{size=14}Stats{/size}{/color}":
                                        yalign 0.5
                                
                                # Unknown
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton "?":
                                        action ToggleDict(persistent.urw_filters, 'unknown')
                                        xsize int(35 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(35 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(18 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_filters.get('unknown', False):
                                            background "#607D8B"
                                            text_color "#fff"
                                        else:
                                            background "#444"
                                            text_color "#888"
                                        hover_background "#90A4AE"
                                    text "{color=#ccc}{size=14}Unknown{/size}{/color}":
                                        yalign 0.5
                                
                                null
                    
                    # Name Filters
                    frame:
                        background Frame("#16213e", 12, 12)
                        xfill True
                        padding (int(20 * _urw_calc_responsive()['avg_scale']), int(15 * _urw_calc_responsive()['avg_scale']))
                        
                        vbox:
                            spacing int(15 * _urw_calc_responsive()['avg_scale'])
                            
                            text "{color=#fff}{size=18}{b}Name-based Filters{/b}{/size}{/color}"
                            
                            grid 2 3:
                                spacing int(20 * _urw_calc_responsive()['avg_scale'])
                                xalign 0.5
                                
                                # Hide underscore
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton (_("ON") if persistent.urw_name_filters.get('hide_underscore', True) else _("OFF")):
                                        action ToggleDict(persistent.urw_name_filters, 'hide_underscore')
                                        xsize int(55 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(30 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(12 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_name_filters.get('hide_underscore', True):
                                            background "#4fc3f7"
                                            text_color "#000"
                                        else:
                                            background "#555"
                                            text_color "#aaa"
                                        hover_background "#5fd3f7"
                                    text "{color=#ccc}{size=14}Hide _variables{/size}{/color}":
                                        yalign 0.5
                                
                                # Hide renpy
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton (_("ON") if persistent.urw_name_filters.get('hide_renpy', True) else _("OFF")):
                                        action ToggleDict(persistent.urw_name_filters, 'hide_renpy')
                                        xsize int(55 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(30 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(12 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_name_filters.get('hide_renpy', True):
                                            background "#4fc3f7"
                                            text_color "#000"
                                        else:
                                            background "#555"
                                            text_color "#aaa"
                                        hover_background "#5fd3f7"
                                    text "{color=#ccc}{size=14}Hide renpy.* calls{/size}{/color}":
                                        yalign 0.5
                                
                                # Hide config
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton (_("ON") if persistent.urw_name_filters.get('hide_config', False) else _("OFF")):
                                        action ToggleDict(persistent.urw_name_filters, 'hide_config')
                                        xsize int(55 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(30 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(12 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_name_filters.get('hide_config', False):
                                            background "#4fc3f7"
                                            text_color "#000"
                                        else:
                                            background "#555"
                                            text_color "#aaa"
                                        hover_background "#5fd3f7"
                                    text "{color=#ccc}{size=14}Hide config.* vars{/size}{/color}":
                                        yalign 0.5
                                
                                # Hide store
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton (_("ON") if persistent.urw_name_filters.get('hide_store', True) else _("OFF")):
                                        action ToggleDict(persistent.urw_name_filters, 'hide_store')
                                        xsize int(55 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(30 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(12 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_name_filters.get('hide_store', True):
                                            background "#4fc3f7"
                                            text_color "#000"
                                        else:
                                            background "#555"
                                            text_color "#aaa"
                                        hover_background "#5fd3f7"
                                    text "{color=#ccc}{size=14}Hide store.* vars{/size}{/color}":
                                        yalign 0.5
                                
                                # Hide internal
                                hbox:
                                    spacing int(8 * _urw_calc_responsive()['avg_scale'])
                                    textbutton (_("ON") if persistent.urw_name_filters.get('hide_internal', True) else _("OFF")):
                                        action ToggleDict(persistent.urw_name_filters, 'hide_internal')
                                        xsize int(55 * _urw_calc_responsive()['avg_scale'])
                                        ysize int(30 * _urw_calc_responsive()['avg_scale'])
                                        text_size int(12 * _urw_calc_responsive()['avg_scale'])
                                        text_xalign 0.5
                                        if persistent.urw_name_filters.get('hide_internal', True):
                                            background "#4fc3f7"
                                            text_color "#000"
                                        else:
                                            background "#555"
                                            text_color "#aaa"
                                        hover_background "#5fd3f7"
                                    text "{color=#ccc}{size=14}Hide __internal{/size}{/color}":
                                        yalign 0.5
                                
                                null  # Empty cell
                    
                    # Quick Presets
                    frame:
                        background Frame("#16213e", 12, 12)
                        xfill True
                        padding (int(20 * _urw_calc_responsive()['avg_scale']), int(15 * _urw_calc_responsive()['avg_scale']))
                        
                        vbox:
                            spacing int(15 * _urw_calc_responsive()['avg_scale'])
                            
                            text "{color=#fff}{size=18}{b}Quick Presets{/b}{/size}{/color}"
                            
                            hbox:
                                spacing int(15 * _urw_calc_responsive()['avg_scale'])
                                xalign 0.5
                                
                                textbutton "Show All":
                                    action [
                                        SetDict(persistent.urw_filters, 'variables', True),
                                        SetDict(persistent.urw_filters, 'conditions', True),
                                        SetDict(persistent.urw_filters, 'flow', True),
                                        SetDict(persistent.urw_filters, 'functions', True),
                                        SetDict(persistent.urw_filters, 'flags', True),
                                        SetDict(persistent.urw_filters, 'relationships', True),
                                        SetDict(persistent.urw_filters, 'stats', True),
                                        SetDict(persistent.urw_filters, 'unknown', True),
                                    ]
                                    xsize int(120 * _urw_calc_responsive()['avg_scale'])
                                    ysize int(40 * _urw_calc_responsive()['avg_scale'])
                                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                                    text_xalign 0.5
                                    background "#4CAF50"
                                    hover_background "#66BB6A"
                                    text_color "#fff"
                                
                                textbutton "Variables Only":
                                    action [
                                        SetDict(persistent.urw_filters, 'variables', True),
                                        SetDict(persistent.urw_filters, 'conditions', False),
                                        SetDict(persistent.urw_filters, 'flow', False),
                                        SetDict(persistent.urw_filters, 'functions', False),
                                        SetDict(persistent.urw_filters, 'flags', True),
                                        SetDict(persistent.urw_filters, 'relationships', True),
                                        SetDict(persistent.urw_filters, 'stats', True),
                                        SetDict(persistent.urw_filters, 'unknown', False),
                                    ]
                                    xsize int(140 * _urw_calc_responsive()['avg_scale'])
                                    ysize int(40 * _urw_calc_responsive()['avg_scale'])
                                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                                    text_xalign 0.5
                                    background "#2196F3"
                                    hover_background "#42A5F5"
                                    text_color "#fff"
                                
                                textbutton "Relationships":
                                    action [
                                        SetDict(persistent.urw_filters, 'variables', True),
                                        SetDict(persistent.urw_filters, 'conditions', False),
                                        SetDict(persistent.urw_filters, 'flow', False),
                                        SetDict(persistent.urw_filters, 'functions', False),
                                        SetDict(persistent.urw_filters, 'flags', False),
                                        SetDict(persistent.urw_filters, 'relationships', True),
                                        SetDict(persistent.urw_filters, 'stats', False),
                                        SetDict(persistent.urw_filters, 'unknown', False),
                                    ]
                                    xsize int(140 * _urw_calc_responsive()['avg_scale'])
                                    ysize int(40 * _urw_calc_responsive()['avg_scale'])
                                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                                    text_xalign 0.5
                                    background "#E91E63"
                                    hover_background "#F06292"
                                    text_color "#fff"
                                
                                textbutton "Minimal":
                                    action [
                                        SetDict(persistent.urw_filters, 'variables', True),
                                        SetDict(persistent.urw_filters, 'conditions', False),
                                        SetDict(persistent.urw_filters, 'flow', True),
                                        SetDict(persistent.urw_filters, 'functions', False),
                                        SetDict(persistent.urw_filters, 'flags', False),
                                        SetDict(persistent.urw_filters, 'relationships', True),
                                        SetDict(persistent.urw_filters, 'stats', True),
                                        SetDict(persistent.urw_filters, 'unknown', False),
                                    ]
                                    xsize int(100 * _urw_calc_responsive()['avg_scale'])
                                    ysize int(40 * _urw_calc_responsive()['avg_scale'])
                                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                                    text_xalign 0.5
                                    background "#607D8B"
                                    hover_background "#90A4AE"
                                    text_color "#fff"
            
            # Footer
            hbox:
                spacing int(20 * _urw_calc_responsive()['avg_scale'])
                xalign 0.5
                
                textbutton "← Back":
                    action Hide("URW_filters", transition=dissolve)
                    xsize int(100 * _urw_calc_responsive()['avg_scale'])
                    ysize int(40 * _urw_calc_responsive()['avg_scale'])
                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background "#455a64"
                    hover_background "#607D8B"
                    text_color "#fff"
                
                textbutton "Reset Filters":
                    action [
                        SetDict(persistent.urw_filters, 'variables', True),
                        SetDict(persistent.urw_filters, 'conditions', True),
                        SetDict(persistent.urw_filters, 'flow', True),
                        SetDict(persistent.urw_filters, 'functions', True),
                        SetDict(persistent.urw_filters, 'flags', True),
                        SetDict(persistent.urw_filters, 'relationships', True),
                        SetDict(persistent.urw_filters, 'stats', True),
                        SetDict(persistent.urw_filters, 'unknown', False),
                        SetDict(persistent.urw_name_filters, 'hide_underscore', True),
                        SetDict(persistent.urw_name_filters, 'hide_renpy', True),
                        SetDict(persistent.urw_name_filters, 'hide_config', False),
                        SetDict(persistent.urw_name_filters, 'hide_store', True),
                        SetDict(persistent.urw_name_filters, 'hide_internal', True),
                    ]
                    xsize int(140 * _urw_calc_responsive()['avg_scale'])
                    ysize int(40 * _urw_calc_responsive()['avg_scale'])
                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background "#f44336"
                    hover_background "#ef5350"
                    text_color "#fff"

##################################################################
#                URW STATISTICS SCREEN                           #
##################################################################

screen URW_stats_screen():
    tag menu
    modal True
    zorder 201
    
    add "#000" alpha 0.85
    
    key "game_menu" action Hide("URW_stats_screen", transition=dissolve)
    key "K_ESCAPE" action Hide("URW_stats_screen", transition=dissolve)
    
    frame:
        xalign 0.5
        yalign 0.5
        xmaximum int(600 * _urw_calc_responsive()['avg_scale'])
        background Frame("#1a1a2e", 20, 20)
        xpadding int(35 * _urw_calc_responsive()['avg_scale'])
        ypadding int(30 * _urw_calc_responsive()['avg_scale'])
        
        at URW_fade_in
        
        vbox:
            spacing int(20 * _urw_calc_responsive()['avg_scale'])
            xalign 0.5
            
            text "{color=#4fc3f7}{size=28}{b}📊 URW 2.0 Statistics{/b}{/size}{/color}":
                xalign 0.5
            
            add "#4fc3f7" xsize int(250 * _urw_calc_responsive()['avg_scale']) ysize 2 xalign 0.5
            
            null height int(10 * _urw_calc_responsive()['avg_scale'])
            
            python:
                _stats = urw_get_stats()
                _stat_version = _stats.get('version', 'N/A')
                _stat_session = _stats.get('session_start', 'N/A')
                _stat_menus = _stats.get('menus_analyzed', 0)
                _stat_consequences = _stats.get('consequences_shown', 0)
                _menu_cache = _stats.get('menu_cache', {})
                _menu_cache_size = _menu_cache.get('size', 0)
                _menu_cache_max = _menu_cache.get('max_size', 0)
                _menu_cache_hit = _menu_cache.get('hit_rate', '0%')
                _cons_cache = _stats.get('consequence_cache', {})
                _cons_cache_size = _cons_cache.get('size', 0)
                _cons_cache_max = _cons_cache.get('max_size', 0)
                _cons_cache_hit = _cons_cache.get('hit_rate', '0%')
            
            # Version info
            frame:
                background "#16213e"
                xfill True
                padding (int(20 * _urw_calc_responsive()['avg_scale']), int(15 * _urw_calc_responsive()['avg_scale']))
                
                vbox:
                    spacing int(10 * _urw_calc_responsive()['avg_scale'])
                    
                    hbox:
                        text "{color=#888}{size=14}Version:{/size}{/color}"
                        text "{color=#4fc3f7}{size=14} [_stat_version]{/size}{/color}"
                    
                    hbox:
                        text "{color=#888}{size=14}Session Started:{/size}{/color}"
                        text "{color=#fff}{size=14} [_stat_session]{/size}{/color}"
            
            # Usage stats
            frame:
                background "#16213e"
                xfill True
                padding (int(20 * _urw_calc_responsive()['avg_scale']), int(15 * _urw_calc_responsive()['avg_scale']))
                
                vbox:
                    spacing int(10 * _urw_calc_responsive()['avg_scale'])
                    
                    text "{color=#fff}{size=16}{b}Usage{/b}{/size}{/color}"
                    
                    hbox:
                        text "{color=#888}{size=14}Menus Analyzed:{/size}{/color}"
                        text "{color=#4CAF50}{size=14} [_stat_menus]{/size}{/color}"
                    
                    hbox:
                        text "{color=#888}{size=14}Consequences Shown:{/size}{/color}"
                        text "{color=#2196F3}{size=14} [_stat_consequences]{/size}{/color}"
            
            # Cache stats
            frame:
                background "#16213e"
                xfill True
                padding (int(20 * _urw_calc_responsive()['avg_scale']), int(15 * _urw_calc_responsive()['avg_scale']))
                
                vbox:
                    spacing int(10 * _urw_calc_responsive()['avg_scale'])
                    
                    text "{color=#fff}{size=16}{b}Cache Performance{/b}{/size}{/color}"
                    
                    hbox:
                        text "{color=#888}{size=14}Menu Cache:{/size}{/color}"
                        text "{color=#fff}{size=14} [_menu_cache_size]/[_menu_cache_max] ([_menu_cache_hit] hit rate){/size}{/color}"
                    
                    hbox:
                        text "{color=#888}{size=14}Consequence Cache:{/size}{/color}"
                        text "{color=#fff}{size=14} [_cons_cache_size]/[_cons_cache_max] ([_cons_cache_hit] hit rate){/size}{/color}"
            
            null height int(10 * _urw_calc_responsive()['avg_scale'])
            
            hbox:
                spacing int(20 * _urw_calc_responsive()['avg_scale'])
                xalign 0.5
                
                textbutton "Clear Caches":
                    action Function(urw_clear_caches)
                    xsize int(130 * _urw_calc_responsive()['avg_scale'])
                    ysize int(40 * _urw_calc_responsive()['avg_scale'])
                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background "#FF5722"
                    hover_background "#FF7043"
                    text_color "#fff"
                
                textbutton "Close":
                    action Hide("URW_stats_screen", transition=dissolve)
                    xsize int(100 * _urw_calc_responsive()['avg_scale'])
                    ysize int(40 * _urw_calc_responsive()['avg_scale'])
                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background "#4fc3f7"
                    hover_background "#5fd3f7"
                    text_color "#000"

##################################################################
#                URW DEBUG SCREEN                                #
##################################################################

screen URW_debug():
    tag menu
    modal True
    zorder 201
    
    add "#000" alpha 0.9
    
    key "game_menu" action Hide("URW_debug", transition=dissolve)
    key "K_ESCAPE" action Hide("URW_debug", transition=dissolve)
    
    frame:
        xalign 0.5
        yalign 0.5
        xmaximum int(800 * _urw_calc_responsive()['avg_scale'])
        ymaximum int(600 * _urw_calc_responsive()['avg_scale'])
        background Frame("#0d1117", 20, 20)
        xpadding int(25 * _urw_calc_responsive()['avg_scale'])
        ypadding int(20 * _urw_calc_responsive()['avg_scale'])
        
        vbox:
            spacing int(15 * _urw_calc_responsive()['avg_scale'])
            
            text "{color=#FF5722}{size=24}{b}🔍 URW 2.0 Debug Console{/b}{/size}{/color}":
                xalign 0.5
            
            add "#FF5722" xsize int(300 * _urw_calc_responsive()['avg_scale']) ysize 2 xalign 0.5
            
            # Log viewer
            viewport:
                scrollbars "vertical"
                mousewheel True
                xsize int(750 * _urw_calc_responsive()['avg_scale'])
                ysize int(400 * _urw_calc_responsive()['avg_scale'])
                
                vbox:
                    spacing int(5 * _urw_calc_responsive()['avg_scale'])
                    
                    python:
                        _logs = urw_log.get_logs(100)
                    
                    for _log_entry in _logs:
                        text "{color=#888}{size=11}[_log_entry]{/size}{/color}"
            
            hbox:
                spacing int(15 * _urw_calc_responsive()['avg_scale'])
                xalign 0.5
                
                textbutton "Clear Logs":
                    action Function(urw_log.clear)
                    xsize int(110 * _urw_calc_responsive()['avg_scale'])
                    ysize int(35 * _urw_calc_responsive()['avg_scale'])
                    text_size int(12 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background "#f44336"
                    hover_background "#ef5350"
                    text_color "#fff"
                
                textbutton "Copy Info":
                    action Function(urw_copy_debug_info)
                    xsize int(100 * _urw_calc_responsive()['avg_scale'])
                    ysize int(35 * _urw_calc_responsive()['avg_scale'])
                    text_size int(12 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background "#FF9800"
                    hover_background "#FFB74D"
                    text_color "#000"
                
                textbutton "Toggle Debug":
                    action ToggleField(urw_log, '_enabled')
                    xsize int(120 * _urw_calc_responsive()['avg_scale'])
                    ysize int(35 * _urw_calc_responsive()['avg_scale'])
                    text_size int(12 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    if urw_log._enabled:
                        background "#4CAF50"
                        text_color "#fff"
                    else:
                        background "#607D8B"
                        text_color "#aaa"
                    hover_background "#66BB6A"
                
                textbutton "Close":
                    action Hide("URW_debug", transition=dissolve)
                    xsize int(90 * _urw_calc_responsive()['avg_scale'])
                    ysize int(35 * _urw_calc_responsive()['avg_scale'])
                    text_size int(12 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background "#4fc3f7"
                    hover_background "#5fd3f7"
                    text_color "#000"

##################################################################
#                URW FULL VIEWER SCREEN                          #
##################################################################

screen URW_full_viewer():
    tag menu
    modal True
    zorder 200
    
    key "game_menu" action Hide("URW_full_viewer", transition=dissolve)
    key "K_ESCAPE" action Hide("URW_full_viewer", transition=dissolve)
    
    add "#000000cc"
    
    frame:
        background Frame("#0d1117", 20, 20)
        xalign 0.5
        yalign 0.5
        xsize int(900 * _urw_calc_responsive()['avg_scale'])
        ymaximum int(700 * _urw_calc_responsive()['avg_scale'])
        padding (int(30 * _urw_calc_responsive()['avg_scale']), int(25 * _urw_calc_responsive()['avg_scale']))
        
        vbox:
            spacing int(15 * _urw_calc_responsive()['avg_scale'])
            
            # Title
            text "{color=#4fc3f7}{size=24}{b}📋 Full Consequence Viewer{/b}{/size}{/color}":
                xalign 0.5
            
            add "#4fc3f7" xsize int(300 * _urw_calc_responsive()['avg_scale']) ysize 2 xalign 0.5
            
            text "{color=#888}{size=14}View complete consequence details for current menu choices{/size}{/color}":
                xalign 0.5
            
            null height int(10 * _urw_calc_responsive()['avg_scale'])
            
            # Get current menu data
            python:
                _viewer_data = urw_get_current_menu_consequences()
                _has_data = _viewer_data and len(_viewer_data) > 0
            
            if _has_data:
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    draggable True
                    ysize int(450 * _urw_calc_responsive()['avg_scale'])
                    xfill True
                    
                    vbox:
                        spacing int(20 * _urw_calc_responsive()['avg_scale'])
                        
                        for _choice_idx, _choice_data in enumerate(_viewer_data):
                            python:
                                _choice_num = _choice_idx + 1
                                _choice_caption = _choice_data.get('caption', 'Unknown')
                            
                            frame:
                                background "#16213e"
                                xfill True
                                padding (int(20 * _urw_calc_responsive()['avg_scale']), int(15 * _urw_calc_responsive()['avg_scale']))
                                
                                vbox:
                                    spacing int(10 * _urw_calc_responsive()['avg_scale'])
                                    
                                    # Choice caption
                                    text "{color=#4fc3f7}{size=16}{b}Choice [_choice_num]: [_choice_caption]{/b}{/size}{/color}"
                                    
                                    frame:
                                        background "#333"
                                        xfill True
                                        ysize 1
                                    
                                    if _choice_data['consequences']:
                                        for _cons in _choice_data['consequences']:
                                            python:
                                                _cons_type = _cons.type if hasattr(_cons, 'type') else 'unknown'
                                                _cons_var = str(_cons.variable) if hasattr(_cons, 'variable') else str(_cons)
                                                _cons_val = str(_cons.value) if hasattr(_cons, 'value') and _cons.value else ''
                                                _cons_color = urw_formatter.get_theme().get(_cons_type, '#888')
                                                _cons_meta = ConsequenceType.get_metadata(_cons_type)
                                                _cons_icon = _cons_meta.get('icon', '•')
                                                _cons_desc = _cons_meta.get('description', _cons_type)
                                                _has_branches = hasattr(_cons, 'branch_consequences') and _cons.branch_consequences
                                                _has_sub = hasattr(_cons, 'sub_consequences') and _cons.sub_consequences
                                            
                                            vbox:
                                                spacing 5
                                                
                                                hbox:
                                                    spacing 15
                                                    
                                                    text "{color=[_cons_color]}{size=14}[_cons_icon]{/size}{/color}":
                                                        yalign 0.0
                                                        xsize 25
                                                    
                                                    vbox:
                                                        spacing 3
                                                        
                                                        # Full variable name - no truncation
                                                        text "{color=#fff}{size=14}[_cons_var]{/size}{/color}"
                                                        
                                                        if _cons_val:
                                                            # Full value - no truncation
                                                            text "{color=#888}{size=12}Value: [_cons_val]{/size}{/color}"
                                                        
                                                        text "{color=#666}{size=11}Type: [_cons_desc]{/size}{/color}"
                                                
                                                # Show sub-consequences organized by branch for conditions
                                                if _cons_type == 'condition' and _has_branches:
                                                    python:
                                                        _branch_items = list(_cons.branch_consequences.items())
                                                    
                                                    for _branch_key, _branch_cons in _branch_items:
                                                        python:
                                                            # Determine branch color
                                                            if _branch_key.startswith("if "):
                                                                _branch_color = "#4fc3f7"  # cyan for if
                                                                _branch_icon = "▶"
                                                            elif _branch_key.startswith("elif "):
                                                                _branch_color = "#ffa726"  # orange for elif
                                                                _branch_icon = "▷"
                                                            else:  # else
                                                                _branch_color = "#ab47bc"  # purple for else
                                                                _branch_icon = "▹"
                                                            _branch_display = _branch_key
                                                        
                                                        frame:
                                                            background "#0d1520"
                                                            xfill True
                                                            left_margin 40
                                                            padding (15, 10)
                                                            
                                                            vbox:
                                                                spacing 8
                                                                
                                                                # Branch header
                                                                text "{color=[_branch_color]}{size=12}[_branch_icon] {b}[_branch_display]{/b}{/size}{/color}"
                                                                
                                                                if _branch_cons:
                                                                    for _sub_cons in _branch_cons:
                                                                        python:
                                                                            _sub_type = _sub_cons.type if hasattr(_sub_cons, 'type') else 'unknown'
                                                                            _sub_var = str(_sub_cons.variable) if hasattr(_sub_cons, 'variable') else str(_sub_cons)
                                                                            _sub_val = str(_sub_cons.value) if hasattr(_sub_cons, 'value') and _sub_cons.value else ''
                                                                            _sub_color = urw_formatter.get_theme().get(_sub_type, '#888')
                                                                            _sub_meta = ConsequenceType.get_metadata(_sub_type)
                                                                            _sub_icon = _sub_meta.get('icon', '•')
                                                                        
                                                                        hbox:
                                                                            spacing 10
                                                                            xpos 15
                                                                            
                                                                            text "{color=[_sub_color]}{size=12}[_sub_icon]{/size}{/color}":
                                                                                yalign 0.0
                                                                                xsize 20
                                                                            
                                                                            vbox:
                                                                                spacing 2
                                                                                text "{color=#ccc}{size=12}[_sub_var]{/size}{/color}"
                                                                                if _sub_val:
                                                                                    text "{color=#777}{size=11}= [_sub_val]{/size}{/color}"
                                                                else:
                                                                    text "{color=#555}{size=11}{i}(no consequences){/i}{/size}{/color}":
                                                                        xpos 15
                                                
                                                elif _cons_type == 'condition' and not _has_branches and not _has_sub:
                                                    frame:
                                                        background "#0d1520"
                                                        xfill True
                                                        left_margin 40
                                                        padding (15, 10)
                                                        
                                                        text "{color=#666}{size=12}{i}No consequences inside this condition{/i}{/size}{/color}"
                                    else:
                                        text "{color=#888}{size=14}No consequences detected{/size}{/color}"
            else:
                frame:
                    background "#16213e"
                    xfill True
                    padding (int(30 * _urw_calc_responsive()['avg_scale']), int(40 * _urw_calc_responsive()['avg_scale']))
                    
                    vbox:
                        spacing int(15 * _urw_calc_responsive()['avg_scale'])
                        xalign 0.5
                        
                        text "{color=#888}{size=18}No menu currently active{/size}{/color}":
                            xalign 0.5
                        
                        text "{color=#666}{size=14}Open this viewer during a menu choice to see full consequence details.{/size}{/color}":
                            xalign 0.5
                            text_align 0.5
            
            null height int(10 * _urw_calc_responsive()['avg_scale'])
            
            # Footer buttons
            hbox:
                spacing int(20 * _urw_calc_responsive()['avg_scale'])
                xalign 0.5
                
                textbutton "Refresh":
                    action NullAction()
                    xsize int(120 * _urw_calc_responsive()['avg_scale'])
                    ysize int(40 * _urw_calc_responsive()['avg_scale'])
                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background "#2196F3"
                    hover_background "#42A5F5"
                    text_color "#fff"
                
                textbutton "Close":
                    action Hide("URW_full_viewer", transition=dissolve)
                    xsize int(120 * _urw_calc_responsive()['avg_scale'])
                    ysize int(40 * _urw_calc_responsive()['avg_scale'])
                    text_size int(14 * _urw_calc_responsive()['avg_scale'])
                    text_xalign 0.5
                    background "#4fc3f7"
                    hover_background "#5fd3f7"
                    text_color "#000"


init 999 python:
    config.underlay.append(
        renpy.Keymap(
            alt_K_w = lambda: renpy.run(Show("URW_preferences"))
        )
    )
