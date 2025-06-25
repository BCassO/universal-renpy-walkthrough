####          Universal Walkthrough System v1.4            ####
####             (C) Knox Emberlyn 2025                    ####

# This file is part of the Universal Walkthrough System for Ren'Py created by Knox Emberlyn.

#########################################################################################

screen custom_prefix_input():
    modal True
    zorder 202
    
    add "#000" alpha 0.7
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 500
        background Frame("#111", 15, 15)
        padding (30, 25)
        
        vbox:
            spacing 20
            xalign 0.5
            
            text "{color=#4a9eff}{size=20}{b}Custom Prefix Filters{/b}{/size}{/color}":
                xalign 0.5
            
            text "{color=#ccc}{size=14}Enter prefixes separated by semicolons (;){/size}{/color}":
                xalign 0.5
                text_align 0.5
            
            python:
                current_prefix = persistent.universal_wt_name_filters.get('custom_prefix', '')
                if 'custom_prefix' not in persistent.universal_wt_name_filters:
                    persistent.universal_wt_name_filters['custom_prefix'] = ''
            
            input:
                default current_prefix
                length 60
                color "#fff"
                xalign 0.5
                xsize 400
                value DictInputValue(persistent.universal_wt_name_filters, 'custom_prefix')
                copypaste True
                allow "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_;_ "
            
            vbox:
                spacing 5
                xalign 0.5
                
                text "{color=#888}{size=12}Examples:{/size}{/color}":
                    xalign 0.5
                
                text "{color=#4a9eff}{size=11}elspeth; temp_; old_; debug_{/size}{/color}":
                    xalign 0.5
                
                text "{color=#4a9eff}{size=11}mc_; girl_; internal_{/size}{/color}":
                    xalign 0.5
            
            if persistent.universal_wt_name_filters.get('custom_prefix', ''):
                vbox:
                    spacing 5
                    xalign 0.5
                    
                    $ preview_prefixes = [p.strip() for p in persistent.universal_wt_name_filters.get('custom_prefix', '').split(';') if p.strip()]
                    
                    text "{color=#8cc8ff}{size=12}Preview (%s filters):{/size}{/color}"%(len(preview_prefixes)):
                        xalign 0.5
                    
                    for prefix in preview_prefixes[:5]:
                        text "{color=#fff}{size=10}• Will hide variables starting with '{b}[prefix]{/b}'{/size}{/color}":
                            xalign 0.5
                    
                    if len(preview_prefixes) > 5:
                        text "{color=#888}{size=10}... and %s more{/size}{/color}"%(len(preview_prefixes) - 5):
                            xalign 0.5
            
            hbox:
                spacing 15
                xalign 0.5
                
                textbutton "Cancel":
                    action Hide("custom_prefix_input")
                    style "wt_close_button"
                    xsize 100
                    ysize 30
                    background "#666"
                    hover_background "#888"
                    text_color "#fff"
                    text_size 14
                    text_xalign 0.5
                
                textbutton "Clear":
                    action [
                        SetDict(persistent.universal_wt_name_filters, 'custom_prefix', ''),
                        Hide("custom_prefix_input")
                    ]
                    style "wt_close_button"
                    xsize 100
                    ysize 30
                    background "#f44"
                    hover_background "#f66"
                    text_color "#fff"
                    text_size 14
                    text_xalign 0.5
                
                textbutton "Apply":
                    action Hide("custom_prefix_input")
                    style "wt_close_button"
                    xsize 100
                    ysize 30
                    background "#4a9eff"
                    hover_background "#6bb8ff"
                    text_color "#fff"
                    text_size 14
                    text_xalign 0.5


#########################################################################################

screen custom_contains_input():
    modal True
    zorder 202
    
    add "#000" alpha 0.7
    
    frame:
        xalign 0.5
        yalign 0.5
        xsize 500
        background Frame("#111", 15, 15)
        padding (30, 25)
        
        vbox:
            spacing 20
            xalign 0.5
            
            text "{color=#4a9eff}{size=20}{b}Custom Contains Filters{/b}{/size}{/color}":
                xalign 0.5
            
            text "{color=#ccc}{size=14}Enter text patterns separated by semicolons (;){/size}{/color}":
                xalign 0.5
                text_align 0.5
            
            python:
                current_contains = persistent.universal_wt_name_filters.get('custom_contains', '')
                if 'custom_contains' not in persistent.universal_wt_name_filters:
                    persistent.universal_wt_name_filters['custom_contains'] = ''
            
            input:
                default current_contains
                length 60
                color "#fff"
                xalign 0.5
                xsize 400
                value DictInputValue(persistent.universal_wt_name_filters, 'custom_contains')
                copypaste True
                allow "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789_;_ "
            
            vbox:
                spacing 5
                xalign 0.5
                
                text "{color=#888}{size=12}Examples:{/size}{/color}":
                    xalign 0.5
                
                text "{color=#4a9eff}{size=11}elspeth; fuck; temp; debug{/size}{/color}":
                    xalign 0.5
                
                text "{color=#4a9eff}{size=11}internal; test; temp{/size}{/color}":
                    xalign 0.5
            
            if persistent.universal_wt_name_filters.get('custom_contains', ''):
                vbox:
                    spacing 5
                    xalign 0.5
                    
                    $ preview_contains = [c.strip() for c in persistent.universal_wt_name_filters.get('custom_contains', '').split(';') if c.strip()]
                    
                    text "{color=#8cc8ff}{size=12}Preview (%s filters):{/size}{/color}"%(len(preview_contains)):
                        xalign 0.5
                    
                    for contains in preview_contains[:5]:
                        text "{color=#fff}{size=10}• Will hide variables containing '{b}[contains]{/b}'{/size}{/color}":
                            xalign 0.5
                    
                    if len(preview_contains) > 5:
                        text "{color=#888}{size=10}... and %s more{/size}{/color}"%(len(preview_contains) - 5):
                            xalign 0.5
            
            hbox:
                spacing 15
                xalign 0.5
                
                textbutton "Cancel":
                    action Hide("custom_contains_input")
                    style "wt_close_button"
                    xsize 100
                    ysize 30
                    background "#666"
                    hover_background "#888"
                    text_color "#fff"
                    text_size 14
                    text_xalign 0.5
                
                textbutton "Clear":
                    action [
                        SetDict(persistent.universal_wt_name_filters, 'custom_contains', ''),
                        Hide("custom_contains_input")
                    ]
                    style "wt_close_button"
                    xsize 100
                    ysize 30
                    background "#f44"
                    hover_background "#f66"
                    text_color "#fff"
                    text_size 14
                    text_xalign 0.5
                
                textbutton "Apply":
                    action Hide("custom_contains_input")
                    style "wt_close_button"
                    xsize 100
                    ysize 30
                    background "#4a9eff"
                    hover_background "#6bb8ff"
                    text_color "#fff"
                    text_size 14
                    text_xalign 0.5


#########################################################################################

screen universal_walkthrough_filters():
    modal True
    zorder 201
    
    add "#000" alpha 0.0:
        at transform:
            alpha 0.0
            ease 0.3 alpha 0.9
    
    key "game_menu" action Hide("universal_walkthrough_filters", transition=dissolve)
    key "K_ESCAPE" action Hide("universal_walkthrough_filters", transition=dissolve)
    
    frame:
        xalign 0.5
        yalign 0.5
        xmaximum 800
        ymaximum 700
        background Frame("#000", 20, 20)
        xpadding 40
        ypadding 30
        
        at transform:
            yoffset -100
            alpha 0.0
            ease 0.4 yoffset 0 alpha 1.0
        
        vbox:
            spacing 20
            xalign 0.5
            
            vbox:
                spacing 10
                xalign 0.5
                
                text "{color=#4a9eff}{size=28}{b}Consequence Filters{/b}{/size}{/color}":
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        pause 0.2
                        ease 0.5 alpha 1.0
                
                text "{color=#8cc8ff}{size=16}Customize what types of consequences to display{/size}{/color}":
                    xalign 0.5
                    text_align 0.5
                    at transform:
                        alpha 0.0
                        pause 0.4
                        ease 0.5 alpha 1.0
                
                add "#4a9eff" xsize 500 ysize 2 xalign 0.5:
                    at transform:
                        xsize 0
                        pause 0.6
                        ease 0.8 xsize 500
            
            viewport:
                scrollbars "vertical"
                mousewheel True
                xsize 720
                ysize 500
                
                vbox:
                    spacing 25
                    xsize 700
                    
                    # Statement Type Filters
                    vbox:
                        spacing 15
                        xalign 0.5
                        at transform:
                            alpha 0.0
                            xoffset -50
                            pause 0.8
                            ease 0.4 alpha 1.0 xoffset 0
                        
                        text "{color=#fff}{size=20}{b}Statement Types{/b}{/size}{/color}":
                            xalign 0.5
                        
                        text "{color=#ccc}{size=14}Choose which types of code statements to show{/size}{/color}":
                            xalign 0.5
                            text_align 0.5
                        
                        grid 3 4:
                            spacing 20
                            xalign 0.5
                            
                            # Row 1
                            hbox:
                                spacing 8
                                textbutton "❓":
                                    action ToggleDict(persistent.universal_wt_filters, 'conditions')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 14
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('conditions', True):
                                        background "#ff8"
                                        text_color "#000"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#ffaa00"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}If Statements{/size}{/color}"
                            
                            hbox:
                                spacing 8
                                textbutton "+":
                                    action ToggleDict(persistent.universal_wt_filters, 'increases')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 16
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('increases', True):
                                        background "#4f4"
                                        text_color "#000"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#44ff44"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}Variable +={/size}{/color}"
                            
                            hbox:
                                spacing 8
                                textbutton "🔧":
                                    action ToggleDict(persistent.universal_wt_filters, 'functions')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 10
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('functions', True):
                                        background "#af4"
                                        text_color "#000"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#aaff44"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}Functions{/size}{/color}"
                            
                            # Row 2
                            hbox:
                                spacing 8
                                textbutton "🦘":
                                    action ToggleDict(persistent.universal_wt_filters, 'jumps')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 14
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('jumps', True):
                                        background "#f84"
                                        text_color "#000"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#ff9944"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}Jumps{/size}{/color}"
                            
                            hbox:
                                spacing 8
                                textbutton "−":
                                    action ToggleDict(persistent.universal_wt_filters, 'decreases')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 16
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('decreases', True):
                                        background "#f44"
                                        text_color "#000"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#ff4444"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}Variable -={/size}{/color}"
                            
                            hbox:
                                spacing 8
                                textbutton "⚙":
                                    action ToggleDict(persistent.universal_wt_filters, 'code')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 14
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('code', True):
                                        background "#ccc"
                                        text_color "#000"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#dddddd"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}Code{/size}{/color}"
                            
                            # Row 3
                            hbox:
                                spacing 8
                                textbutton "📞":
                                    action ToggleDict(persistent.universal_wt_filters, 'calls')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 10
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('calls', True):
                                        background "#8f4"
                                        text_color "#000"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#99ff44"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}Calls{/size}{/color}"
                            
                            hbox:
                                spacing 8
                                textbutton "=":
                                    action ToggleDict(persistent.universal_wt_filters, 'assignments')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 16
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('assignments', True):
                                        background "#44f"
                                        text_color "#fff"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#4444ff"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}Assignments{/size}{/color}"
                            
                            null # Empty space for alignment
                            
                            # Row 4
                            hbox:
                                spacing 8
                                textbutton "↩":
                                    action ToggleDict(persistent.universal_wt_filters, 'returns')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 14
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('returns', True):
                                        background "#f48"
                                        text_color "#000"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#ff4488"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}Returns{/size}{/color}"
                            
                            hbox:
                                spacing 8
                                textbutton "B":
                                    action ToggleDict(persistent.universal_wt_filters, 'booleans')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 14
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('booleans', True):
                                        background "#4af"
                                        text_color "#000"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#44aaff"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}Booleans{/size}{/color}"
                            
                            hbox:
                                spacing 8
                                textbutton "?":
                                    action ToggleDict(persistent.universal_wt_filters, 'unknown')
                                    style "wt_toggle_button"
                                    text_outlines [ ( 0, "#000", 0, 0) ]
                                    text_size 14
                                    xsize 30
                                    ysize 30
                                    if persistent.universal_wt_filters.get('unknown', False):
                                        background "#f8f"
                                        text_color "#000"
                                    else:
                                        background "#444"
                                        text_color "#888"
                                    hover_background "#ff88ff"
                                    text_xalign 0.5
                                    text_yalign 0.5
                                text "{color=#ccc}{size=14}Unknown{/size}{/color}"
                    
                    # Name-based Filters
                    vbox:
                        spacing 15
                        xalign 0.5
                        at transform:
                            alpha 0.0
                            xoffset 50
                            pause 1.0
                            ease 0.4 alpha 1.0 xoffset 0
                        
                        text "{color=#fff}{size=20}{b}Name Filters{/b}{/size}{/color}":
                            xalign 0.5
                        
                        text "{color=#ccc}{size=14}Hide variables and functions based on naming patterns{/size}{/color}":
                            xalign 0.5
                            text_align 0.5
                        
                        # Built-in filters
                        grid 2 2:
                            spacing 30
                            xalign 0.5
                            
                            vbox:
                                spacing 8
                                
                                hbox:
                                    spacing 8
                                    textbutton (_("ON") if persistent.universal_wt_name_filters.get('hide_underscore', True) else _("OFF")):
                                        action ToggleDict(persistent.universal_wt_name_filters, 'hide_underscore')
                                        style "wt_toggle_button"
                                        text_outlines [(2, "#000", 0, 0)]
                                        text_size 10
                                        xsize 40
                                        ysize 25
                                        if persistent.universal_wt_name_filters.get('hide_underscore', True):
                                            background "#4a9eff"
                                            text_color "#fff"
                                        else:
                                            background "#666"
                                            text_color "#ccc"
                                        hover_background "#6bb8ff"
                                        text_xalign 0.5
                                    text "{color=#ccc}{size=14}Hide _variables{/size}{/color}"
                                
                                hbox:
                                    spacing 8
                                    textbutton (_("ON") if persistent.universal_wt_name_filters.get('hide_renpy', True) else _("OFF")):
                                        action ToggleDict(persistent.universal_wt_name_filters, 'hide_renpy')
                                        style "wt_toggle_button"
                                        text_outlines [(2, "#000", 0, 0)]
                                        text_size 10
                                        xsize 40
                                        ysize 25
                                        if persistent.universal_wt_name_filters.get('hide_renpy', True):
                                            background "#4a9eff"
                                            text_color "#fff"
                                        else:
                                            background "#666"
                                            text_color "#ccc"
                                        hover_background "#6bb8ff"
                                        text_xalign 0.5
                                    text "{color=#ccc}{size=14}Hide renpy.* calls{/size}{/color}"
                            
                            vbox:
                                spacing 8
                                
                                hbox:
                                    spacing 8
                                    textbutton (_("ON") if persistent.universal_wt_name_filters.get('hide_config', False) else _("OFF")):
                                        action ToggleDict(persistent.universal_wt_name_filters, 'hide_config')
                                        style "wt_toggle_button"
                                        text_outlines [(2, "#000", 0, 0)]
                                        text_size 10
                                        xsize 40
                                        ysize 25
                                        if persistent.universal_wt_name_filters.get('hide_config', False):
                                            background "#4a9eff"
                                            text_color "#fff"
                                        else:
                                            background "#666"
                                            text_color "#ccc"
                                        hover_background "#6bb8ff"
                                        text_xalign 0.5
                                    text "{color=#ccc}{size=14}Hide config.* vars{/size}{/color}"
                                
                                hbox:
                                    spacing 8
                                    textbutton (_("ON") if persistent.universal_wt_name_filters.get('hide_store', True) else _("OFF")):
                                        action ToggleDict(persistent.universal_wt_name_filters, 'hide_store')
                                        style "wt_toggle_button"
                                        text_outlines [(2, "#000", 0, 0)]
                                        text_size 10
                                        xsize 40
                                        ysize 25
                                        if persistent.universal_wt_name_filters.get('hide_store', True):
                                            background "#4a9eff"
                                            text_color "#fff"
                                        else:
                                            background "#666"
                                            text_color "#ccc"
                                        hover_background "#6bb8ff"
                                        text_xalign 0.5
                                    text "{color=#ccc}{size=14}Hide store.* vars{/size}{/color}"
                        
                        null height 10

                    # Custom filter inputs
                    vbox:
                        spacing 15
                        xalign 0.5
                        
                        text "{color=#fff}{size=18}{b}Custom Filters{/b}{/size}{/color}":
                            xalign 0.5
                        
                        text "{color=#ccc}{size=12}Use semicolons (;) to separate multiple filters{/size}{/color}":
                            xalign 0.5
                            text_align 0.5
                        
                        # Custom Prefix Filter with auto-parsing
                        vbox:
                            spacing 8
                            xalign 0.5
                            
                            hbox:
                                spacing 10
                                xalign 0.5
                                
                                text "{color=#fff}{size=14}Hide variables starting with:{/size}{/color}":
                                    yalign 0.5
                                
                                textbutton (_("ON") if persistent.universal_wt_name_filters.get('custom_prefix', '') else _("OFF")):
                                    action [
                                        If(persistent.universal_wt_name_filters.get('custom_prefix', ''),
                                        SetDict(persistent.universal_wt_name_filters, 'custom_prefix', ''),
                                        Show("custom_prefix_input"))
                                    ]
                                    style "wt_toggle_button"
                                    text_outlines [(2, "#000", 0, 0)]
                                    text_size 10
                                    xsize 40
                                    ysize 25
                                    if persistent.universal_wt_name_filters.get('custom_prefix', ''):
                                        background "#4a9eff"
                                        text_color "#fff"
                                    else:
                                        background "#666"
                                        text_color "#ccc"
                                    hover_background "#6bb8ff"
                                    text_xalign 0.5
                                    yalign 0.5
                            
                            # Display current custom prefix filters (parsed)
                            if persistent.universal_wt_name_filters.get('custom_prefix', ''):
                                vbox:
                                    spacing 5
                                    xalign 0.5
                                    
                                    $ prefix_str = persistent.universal_wt_name_filters.get('custom_prefix', '')
                                    $ parsed_prefixes = [p.strip() for p in prefix_str.split(';') if p.strip()]
                                    
                                    text "{color=#8cc8ff}{size=12}Active prefix filters ([len(parsed_prefixes)] total):{/size}{/color}":
                                        xalign 0.5
                                    
                                    # Show up to 3 filters in a line, then wrap
                                    $ display_prefixes = parsed_prefixes[:6]  # Show max 6 filters
                                    
                                    if len(display_prefixes) <= 3:
                                        hbox:
                                            spacing 5
                                            xalign 0.5
                                            for prefix in display_prefixes:
                                                text "{color=#fff}{size=11}'{b}[prefix]{/b}'{/size}{/color}"
                                    else:
                                        vbox:
                                            spacing 3
                                            xalign 0.5
                                            
                                            # First row (up to 3 filters)
                                            hbox:
                                                spacing 5
                                                xalign 0.5
                                                for prefix in display_prefixes[:3]:
                                                    text "{color=#fff}{size=11}'{b}[prefix]{/b}'{/size}{/color}"
                                            
                                            # Second row (remaining filters)
                                            if len(display_prefixes) > 3:
                                                hbox:
                                                    spacing 5
                                                    xalign 0.5
                                                    for prefix in display_prefixes[3:6]:
                                                        text "{color=#fff}{size=11}'{b}[prefix]{/b}'{/size}{/color}"
                                    
                                    if len(parsed_prefixes) > 6:
                                        text "{color=#888}{size=10}... and %s more{/size}{/color}"%(len(parsed_prefixes) - 6):
                                            xalign 0.5
                                    
                                    hbox:
                                        spacing 10
                                        xalign 0.5
                                        
                                        textbutton "</> Edit":
                                            action Show("custom_prefix_input")
                                            style "wt_toggle_button"
                                            text_size 10
                                            xsize 50
                                            ysize 20
                                            background "#666"
                                            hover_background "#888"
                                            text_color "#fff"
                                            text_xalign 0.5
                                        
                                        textbutton "X Clear":
                                            action SetDict(persistent.universal_wt_name_filters, 'custom_prefix', '')
                                            style "wt_toggle_button"
                                            text_size 10
                                            xsize 50
                                            ysize 20
                                            background "#f44"
                                            hover_background "#f66"
                                            text_color "#fff"
                                            text_xalign 0.5
                       
                        # Custom Contains Filter with auto-parsing
                        vbox:
                            spacing 8
                            xalign 0.5
                            
                            hbox:
                                spacing 10
                                xalign 0.5
                                
                                text "{color=#fff}{size=14}Hide variables containing:{/size}{/color}":
                                    yalign 0.5
                                
                                # Toggle for custom contains filter
                                textbutton (_("ON") if persistent.universal_wt_name_filters.get('custom_contains', '') else _("OFF")):
                                    action [
                                        If(persistent.universal_wt_name_filters.get('custom_contains', ''),
                                        SetDict(persistent.universal_wt_name_filters, 'custom_contains', ''),
                                        Show("custom_contains_input"))
                                    ]
                                    style "wt_toggle_button"
                                    text_outlines [(2, "#000", 0, 0)]
                                    text_size 10
                                    xsize 40
                                    ysize 25
                                    if persistent.universal_wt_name_filters.get('custom_contains', ''):
                                        background "#4a9eff"
                                        text_color "#fff"
                                    else:
                                        background "#666"
                                        text_color "#ccc"
                                    hover_background "#6bb8ff"
                                    text_xalign 0.5
                                    yalign 0.5
                            
                            # Display current custom contains filters (parsed)
                            if persistent.universal_wt_name_filters.get('custom_contains', ''):
                                vbox:
                                    spacing 5
                                    xalign 0.5
                                    
                                    $ contains_str = persistent.universal_wt_name_filters.get('custom_contains', '')
                                    $ parsed_contains = [c.strip() for c in contains_str.split(';') if c.strip()]
                                    
                                    text "{color=#8cc8ff}{size=12}Active contains filters (%s total):{/size}{/color}"%(len(parsed_contains)):
                                        xalign 0.5
                                    
                                    # Show up to 3 filters in a line, then wrap
                                    $ display_contains = parsed_contains[:6]  # Show max 6 filters
                                    
                                    if len(display_contains) <= 3:
                                        hbox:
                                            spacing 5
                                            xalign 0.5
                                            for contains in display_contains:
                                                text "{color=#fff}{size=11}'{b}[contains]{/b}'{/size}{/color}"
                                    else:
                                        vbox:
                                            spacing 3
                                            xalign 0.5
                                            
                                            # First row (up to 3 filters)
                                            hbox:
                                                spacing 5
                                                xalign 0.5
                                                for contains in display_contains[:3]:
                                                    text "{color=#fff}{size=11}'{b}[contains]{/b}'{/size}{/color}"
                                            
                                            # Second row (remaining filters)
                                            if len(display_contains) > 3:
                                                hbox:
                                                    spacing 5
                                                    xalign 0.5
                                                    for contains in display_contains[3:6]:
                                                        text "{color=#fff}{size=11}'{b}[contains]{/b}'{/size}{/color}"
                                    
                                    if len(parsed_contains) > 6:
                                        text "{color=#888}{size=10}... and %s more{/size}{/color}"%(len(parsed_contains) - 6):
                                            xalign 0.5
                                    
                                    hbox:
                                        spacing 10
                                        xalign 0.5
                                        
                                        textbutton "</> Edit":
                                            action Show("custom_contains_input")
                                            style "wt_toggle_button"
                                            text_size 10
                                            xsize 50
                                            ysize 20
                                            background "#666"
                                            hover_background "#888"
                                            text_color "#fff"
                                            text_xalign 0.5
                                        
                                        textbutton "X Clear":
                                            action SetDict(persistent.universal_wt_name_filters, 'custom_contains', '')
                                            style "wt_toggle_button"
                                            text_size 10
                                            xsize 50
                                            ysize 20
                                            background "#f44"
                                            hover_background "#f66"
                                            text_color "#fff"
                                            text_xalign 0.5
                        
                        # Examples
                        vbox:
                            spacing 5
                            xalign 0.5
                            
                            text "{color=#888}{size=12}{b}Examples (semicolon-separated):{/b}{/size}{/color}":
                                xalign 0.5
                            
                            text "{color=#888}{size=11}• Prefix: '_prefix1; temp_; old_; debug_'{/size}{/color}":
                                xalign 0.5
                            
                            text "{color=#888}{size=11}• Contains: 'renpy; config; temp; debug; internal'{/size}{/color}":
                                xalign 0.5
                            
                            text "{color=#4a9eff}{size=10}💡 Tip: Spaces around semicolons are automatically trimmed{/size}{/color}":
                                xalign 0.5
                    
                    # Quick filter presets
                    vbox:
                        spacing 15
                        xalign 0.5
                        at transform:
                            alpha 0.0
                            pause 1.2
                            ease 0.4 alpha 1.0
                        
                        text "{color=#fff}{size=20}{b}Quick Presets{/b}{/size}{/color}":
                            xalign 0.5
                        
                        text "{color=#ccc}{size=14}Quickly configure common filter combinations{/size}{/color}":
                            xalign 0.5
                            text_align 0.5
                        
                        hbox:
                            spacing 15
                            xalign 0.5
                            
                            textbutton "Everything":
                                action [
                                    SetDict(persistent.universal_wt_filters, 'conditions', True),
                                    SetDict(persistent.universal_wt_filters, 'jumps', True),
                                    SetDict(persistent.universal_wt_filters, 'calls', True),
                                    SetDict(persistent.universal_wt_filters, 'returns', True),
                                    SetDict(persistent.universal_wt_filters, 'increases', True),
                                    SetDict(persistent.universal_wt_filters, 'decreases', True),
                                    SetDict(persistent.universal_wt_filters, 'assignments', True),
                                    SetDict(persistent.universal_wt_filters, 'booleans', True),
                                    SetDict(persistent.universal_wt_filters, 'functions', True),
                                    SetDict(persistent.universal_wt_filters, 'code', True),
                                    SetDict(persistent.universal_wt_filters, 'unknown', True),
                                ]
                                style "wt_preset_button"
                                text_outlines [(2, "#000", 0, 0)]
                                text_size 12
                                xsize 100
                                ysize 30
                                background "#4a9eff"
                                hover_background "#6bb8ff"
                                text_color "#fff"
                                text_xalign 0.5
                            
                            textbutton "Variables Only":
                                action [
                                    SetDict(persistent.universal_wt_filters, 'conditions', False),
                                    SetDict(persistent.universal_wt_filters, 'jumps', False),
                                    SetDict(persistent.universal_wt_filters, 'calls', False),
                                    SetDict(persistent.universal_wt_filters, 'returns', False),
                                    SetDict(persistent.universal_wt_filters, 'increases', True),
                                    SetDict(persistent.universal_wt_filters, 'decreases', True),
                                    SetDict(persistent.universal_wt_filters, 'assignments', True),
                                    SetDict(persistent.universal_wt_filters, 'booleans', True),
                                    SetDict(persistent.universal_wt_filters, 'functions', False),
                                    SetDict(persistent.universal_wt_filters, 'code', False),
                                    SetDict(persistent.universal_wt_filters, 'unknown', False),
                                ]
                                style "wt_preset_button"
                                text_outlines [(0, "#000", 0, 0)]
                                text_size 12
                                xsize 120
                                ysize 30
                                background "#4f4"
                                hover_background "#6f6"
                                text_color "#000"
                                text_xalign 0.5
                            
                            textbutton "Story Flow":
                                action [
                                    SetDict(persistent.universal_wt_filters, 'conditions', True),
                                    SetDict(persistent.universal_wt_filters, 'jumps', True),
                                    SetDict(persistent.universal_wt_filters, 'calls', True),
                                    SetDict(persistent.universal_wt_filters, 'returns', True),
                                    SetDict(persistent.universal_wt_filters, 'increases', False),
                                    SetDict(persistent.universal_wt_filters, 'decreases', False),
                                    SetDict(persistent.universal_wt_filters, 'assignments', False),
                                    SetDict(persistent.universal_wt_filters, 'booleans', False),
                                    SetDict(persistent.universal_wt_filters, 'functions', False),
                                    SetDict(persistent.universal_wt_filters, 'code', False),
                                    SetDict(persistent.universal_wt_filters, 'unknown', False),
                                ]
                                style "wt_preset_button"
                                text_outlines [(0, "#000", 0, 0)]
                                text_size 12
                                xsize 100
                                ysize 30
                                background "#ff8"
                                hover_background "#ffa"
                                text_color "#000"
                                text_xalign 0.5
                            
                            textbutton "Minimal":
                                action [
                                    SetDict(persistent.universal_wt_filters, 'conditions', False),
                                    SetDict(persistent.universal_wt_filters, 'jumps', True),
                                    SetDict(persistent.universal_wt_filters, 'calls', False),
                                    SetDict(persistent.universal_wt_filters, 'returns', False),
                                    SetDict(persistent.universal_wt_filters, 'increases', True),
                                    SetDict(persistent.universal_wt_filters, 'decreases', True),
                                    SetDict(persistent.universal_wt_filters, 'assignments', False),
                                    SetDict(persistent.universal_wt_filters, 'booleans', False),
                                    SetDict(persistent.universal_wt_filters, 'functions', False),
                                    SetDict(persistent.universal_wt_filters, 'code', False),
                                    SetDict(persistent.universal_wt_filters, 'unknown', False),
                                ]
                                style "wt_preset_button"
                                text_outlines [(2, "#000", 0, 0)]
                                text_size 12
                                xsize 80
                                ysize 30
                                background "#f48"
                                hover_background "#f68"
                                text_color "#fff"
                                text_xalign 0.5
            
            # Footer buttons
            hbox:
                spacing 20
                xalign 0.5
                at transform:
                    alpha 0.0
                    pause 1.4
                    ease 0.4 alpha 1.0
                
                textbutton "{size=16}<- Back to Main{/size}":
                    action Hide("universal_walkthrough_filters", transition=dissolve)
                    style "wt_close_button"
                    text_outlines [(2, "#000", 0, 0)]
                    xsize 150
                    ysize 35
                    background "#666"
                    hover_background "#888"
                    text_color "#fff"
                    text_xalign 0.5
                
                textbutton "{size=16}Reset All{/size}":
                    action [
                        SetDict(persistent.universal_wt_filters, 'conditions', True),
                        SetDict(persistent.universal_wt_filters, 'jumps', True),
                        SetDict(persistent.universal_wt_filters, 'calls', True),
                        SetDict(persistent.universal_wt_filters, 'returns', True),
                        SetDict(persistent.universal_wt_filters, 'increases', True),
                        SetDict(persistent.universal_wt_filters, 'decreases', True),
                        SetDict(persistent.universal_wt_filters, 'assignments', True),
                        SetDict(persistent.universal_wt_filters, 'booleans', True),
                        SetDict(persistent.universal_wt_filters, 'functions', True),
                        SetDict(persistent.universal_wt_filters, 'code', True),
                        SetDict(persistent.universal_wt_filters, 'unknown', False),
                        SetDict(persistent.universal_wt_name_filters, 'hide_underscore', True),
                        SetDict(persistent.universal_wt_name_filters, 'hide_renpy', True),
                        SetDict(persistent.universal_wt_name_filters, 'hide_config', False),
                        SetDict(persistent.universal_wt_name_filters, 'hide_store', True),
                    ]
                    style "wt_debug_button"
                    text_outlines [(2, "#000", 0, 0)]
                    xsize 120
                    ysize 35
                    text_xalign 0.5

screen universal_walkthrough_preferences():
    modal True
    zorder 200
    
    add "#000" alpha 0.0:
        at transform:
            alpha 0.0
            ease 0.3 alpha 0.8
    
    key "game_menu" action Hide("universal_walkthrough_preferences", transition=dissolve)
    key "K_ESCAPE" action Hide("universal_walkthrough_preferences", transition=dissolve)
    
    frame:
        xalign 0.5
        yalign 0.5
        xmaximum 700
        # ymaximum 500
        background Frame("#000a", 20, 20)
        xpadding 40
        ypadding 30
        
        at transform:
            yoffset -100
            alpha 0.0
            ease 0.4 yoffset 0 alpha 1.0
        
        vbox:
            spacing 25
            xalign 0.5
            
            vbox:
                spacing 10
                xalign 0.5
                
                text "{color=#4a9eff}{size=32}{b}Universal Walkthrough System v1.4{/b}{/size}{/color}":
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        pause 0.2
                        ease 0.5 alpha 1.0
                
                text "{color=#8cc8ff}{size=18}{i}Enhanced with execution context tracking{/i}{/size}{/color}":
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        pause 0.4
                        ease 0.5 alpha 1.0
                
                add "#4a9eff" xsize 400 ysize 2 xalign 0.5:
                    at transform:
                        xsize 0
                        pause 0.6
                        ease 0.8 xsize 400
            
            null height 10
            
            vbox:
                spacing 20
                xalign 0.5
                
                hbox:
                    spacing 15
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        xoffset -50
                        pause 0.8
                        ease 0.4 alpha 1.0 xoffset 0
                    
                    text "{color=#fff}{size=20}Enable Walkthrough:{/size}{/color}"
                    
                    textbutton (_("ON") if persistent.universal_walkthrough_enabled else _("OFF")):
                        action ToggleVariable("persistent.universal_walkthrough_enabled")
                        style "wt_toggle_button"
                        text_outlines [ ( 0, "#000", 0, 0) ]
                        text_size 18
                        xsize 80
                        ysize 35
                        if persistent.universal_walkthrough_enabled:
                            background Frame("gui/button/choice_idle_background.png", 10, 10)
                            text_color "#4a9eff"
                        else:
                            background Frame("gui/button/choice_hover_background.png", 10, 10)
                            text_color "#ff6b6b"
                        hover_background Frame("gui/button/choice_hover_background.png", 10, 10)
                        text_hover_color "#fff"
                        text_xalign 0.5
                
                vbox:
                    spacing 10
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        xoffset 50
                        pause 1.0
                        ease 0.4 alpha 1.0 xoffset 0
                    
                    text "{color=#fff}{size=18}Text Size: {color=#4a9eff}{size=22}{b}[persistent.universal_wt_text_size]{/b}{/size}{/color}{/size}":
                        xalign 0.5
                    
                    hbox:
                        spacing 10
                        xalign 0.5
                        
                        textbutton "−":
                            action If(persistent.universal_wt_text_size > 12, SetVariable("persistent.universal_wt_text_size", persistent.universal_wt_text_size - 2), None)
                            style "wt_size_button"
                            text_outlines [(0, "#000", 0, 0)]
                            text_size 24
                            xsize 40
                            ysize 40
                            text_xalign 0.5
                        
                        frame:
                            background "#2a2a2a"
                            xsize 300
                            ysize 20
                            yalign 0.5
                            
                            bar:
                                value AnimatedValue(persistent.universal_wt_text_size, 40, delay=0.2, old_value=12)
                                left_bar Frame("#4a9eff", 5, 5) 
                                right_bar Frame("#444", 5, 5)
                                thumb None
                                xsize 280
                                ysize 16
                                xalign 0.5
                                yalign 0.5
                        
                        textbutton "+":
                            action If(persistent.universal_wt_text_size < 40, SetVariable("persistent.universal_wt_text_size", persistent.universal_wt_text_size + 2), None)
                            style "wt_size_button"
                            text_outlines [(0, "#000", 0, 0)]
                            text_size 24
                            xsize 40
                            ysize 40
                            text_xalign 0.5

                vbox:
                    spacing 10
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        xoffset 50
                        pause 1.2
                        ease 0.4 alpha 1.0 xoffset 0
                    
                    text "{color=#fff}{size=18}Max Consequences: {color=#4a9eff}{size=22}{b}[persistent.universal_wt_max_consequences]{/b}{/size}{/color}{/size}":
                        xalign 0.5
                    
                    hbox:
                        spacing 10
                        xalign 0.5
                        
                        textbutton "−":
                            action If(persistent.universal_wt_max_consequences > 1, SetVariable("persistent.universal_wt_max_consequences", persistent.universal_wt_max_consequences - 1), None)
                            style "wt_size_button"
                            text_outlines [(0, "#000", 0, 0)]
                            text_size 24
                            xsize 40
                            ysize 40
                            text_xalign 0.5
                        
                        frame:
                            background "#2a2a2a"
                            xsize 200
                            ysize 20
                            yalign 0.5
                            
                            bar:
                                value AnimatedValue(persistent.universal_wt_max_consequences, 8, delay=0.2, old_value=1)
                                left_bar Frame("#4a9eff", 5, 5) 
                                right_bar Frame("#444", 5, 5)
                                thumb None
                                xsize 180
                                ysize 16
                                xalign 0.5
                                yalign 0.5
                        
                        textbutton "+":
                            action If(persistent.universal_wt_max_consequences < 8, SetVariable("persistent.universal_wt_max_consequences", persistent.universal_wt_max_consequences + 1), None)
                            style "wt_size_button"
                            text_outlines [(0, "#000", 0, 0)]
                            text_size 24
                            xsize 40
                            ysize 40
                            text_xalign 0.5


                vbox:
                    spacing 10
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        xoffset -50
                        pause 1.4
                        ease 0.4 alpha 1.0 xoffset 0
                    
                    hbox:
                        spacing 15
                        xalign 0.5
                        
                        text "{color=#fff}{size=18}Show All Available:{/size}{/color}"
                        
                        textbutton (_("ON") if persistent.universal_wt_show_all_available else _("OFF")):
                            action ToggleVariable("persistent.universal_wt_show_all_available")
                            style "wt_toggle_button"
                            text_outlines [ ( 0, "#000", 0, 0) ]
                            text_size 16
                            xsize 70
                            ysize 30
                            if persistent.universal_wt_show_all_available:
                                background "#4a9eff"
                                text_color "#fff"
                            else:
                                background "#666"
                                text_color "#ccc"
                            hover_background "#6bb8ff"
                            text_hover_color "#fff"
                            text_xalign 0.5
                    
                    text "{color=#888}{size=12}When enabled, shows all consequences if more than limit available{/size}{/color}":
                        xalign 0.5
                        text_align 0.5
                        xsize 400

                vbox:
                    spacing 10
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        xoffset -50
                        pause 1.6
                        ease 0.4 alpha 1.0 xoffset 0
                    
                    textbutton "{size=18}🔧 Filter Settings{/size}":
                        action Show("universal_walkthrough_filters", transition=dissolve)
                        style "wt_close_button"
                        text_outlines [(2, "#000", 0, 0)]
                        xalign 0.5
                        xsize 200
                        ysize 40
                        background "#4a9eff"
                        hover_background "#6bb8ff"
                        text_color "#fff"
                        text_xalign 0.5
                    
                    text "{color=#888}{size=12}Configure which types of consequences to display{/size}{/color}":
                        xalign 0.5
                        text_align 0.5
                        xsize 400

                hbox:
                    spacing 8
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        pause 1.4
                        ease 0.4 alpha 1.0
                    
                    text "{color=#bbb}{size=14}Quick presets:{/size}{/color}"
                    
                    for count in [1, 2, 3, 4, 5]:
                        textbutton "[count]":
                            action SetVariable("persistent.universal_wt_max_consequences", count)
                            style "wt_preset_button"
                            text_size 14
                            xsize 25
                            ysize 25
                            if persistent.universal_wt_max_consequences == count:
                                background "#4a9eff"
                                text_color "#fff"
                            else:
                                background "#333"
                                text_color "#bbb"
                            hover_background "#6bb8ff"
                            text_hover_color "#fff"
                            text_xalign 0.5
                
                hbox:
                    spacing 8
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        pause 1.2
                        ease 0.4 alpha 1.0
                    
                    text "{color=#bbb}{size=14}Quick sizes:{/size}{/color}"
                    
                    for size in [12, 16, 20, 25, 30, 35, 40]:
                        textbutton "[size]":
                            action SetVariable("persistent.universal_wt_text_size", size)
                            style "wt_preset_button"
                            text_size 14
                            xsize 35
                            ysize 25
                            if persistent.universal_wt_text_size == size:
                                background "#4a9eff"
                                text_color "#fff"
                            else:
                                background "#333"
                                text_color "#bbb"
                            hover_background "#6bb8ff"
                            text_hover_color "#fff"
                            text_xalign 0.5
            
            if dukeconfig.developer:
                vbox:
                    spacing 10
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        pause 1.4
                        ease 0.4 alpha 1.0
                    
                    text "{color=#ffaa00}{size=16}{b}Debug Information{/b}{/size}{/color}":
                        xalign 0.5
                    
                    text "{color=#ccc}{size=14}Registry: "+ f"{len(menu_registry)} | Cache: {len(consequence_cache)} " + "entries{/size}{/color}":
                        xalign 0.5
                    
                    hbox:
                        spacing 15
                        xalign 0.5

                        if not renpy.get_screen("choice"):
                            textbutton "Clear Cache":
                                action Function(clear_walkthrough_caches)
                                style "wt_debug_button"
                                text_size 14
                                text_xalign 0.5
                            
                        textbutton "Show Memory":
                            action Function(log_memory_usage)
                            style "wt_debug_button"
                            text_size 14
                            text_xalign 0.5
            
            null height 10
            
            textbutton "{size=18}Close{/size}":
                action Hide("universal_walkthrough_preferences", transition=dissolve)
                style "wt_close_button"
                xalign 0.5
                xsize 120
                ysize 40
                at transform:
                    alpha 0.0
                    pause 1.6
                    ease 0.4 alpha 1.0
                text_xalign 0.5

init 999 python:
    config.underlay.append(
        renpy.Keymap(
            alt_K_w = lambda: renpy.run(Show("universal_walkthrough_preferences"))
        )
    )