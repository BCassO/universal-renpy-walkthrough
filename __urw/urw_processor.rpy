####################################################################
####     Universal Ren'Py Walkthrough System v2.0 (Enhanced)    ####
####               (C) Knox Emberlyn 2025-2026                  ####
####               Processor & Menu Integration                 ####
####################################################################

init -997 python:
    ##################################################################
    #            URW CONSEQUENCE PROCESSOR                           #
    ##################################################################
    
    class URWProcessor:
        """Process and filter consequences for display"""
        
        # Keywords for detecting variable importance
        RELATIONSHIP_KEYWORDS = frozenset([
            'love', 'trust', 'affection', 'relationship', 'faith', 'friendship',
            'respect', 'loyalty', 'romance', 'intimacy', 'bond', 're_', 'rel_'
        ])
        
        STAT_KEYWORDS = frozenset([
            'points', 'money', 'health', 'reputation', 'score', 'stat',
            'strength', 'intelligence', 'charisma', 'wisdom', 'luck',
            'karma', 'morality', 'corruption', 'energy', 'stamina'
        ])
        
        FLAG_KEYWORDS = frozenset([
            'flag', 'seen', 'unlocked', 'completed', 'visited', 'discovered',
            'enabled', 'active', 'achieved', 'triggered', 'done'
        ])
        
        def __init__(self):
            self._runtime_captions = []
        
        def _is_ast_node_static(self, obj):
            """Check if an object is a Ren'Py AST node (static version for processor)"""
            if obj is None:
                return False
            try:
                module = getattr(obj.__class__, '__module__', '')
                if 'ast' in str(module):
                    return True
                class_name = obj.__class__.__name__
                if class_name in ('Menu', 'Say', 'Jump', 'Call', 'Python', 'If', 'Label'):
                    if hasattr(obj, 'linenumber') or hasattr(obj, 'filename'):
                        return True
            except:
                pass
            return False
            
        def set_runtime_captions(self, items):
            """Store runtime menu item captions for matching with AST"""
            self._runtime_captions = []
            for item in items:
                try:
                    # Check for AST nodes first
                    if self._is_ast_node_static(item):
                        self._runtime_captions.append(f"Choice {len(self._runtime_captions) + 1}")
                        continue
                    
                    if hasattr(item, 'caption'):
                        raw_caption = item.caption
                        if self._is_ast_node_static(raw_caption):
                            caption = f"Choice {len(self._runtime_captions) + 1}"
                        else:
                            caption = str(raw_caption)
                    elif isinstance(item, (list, tuple)) and len(item) > 0:
                        raw_caption = item[0]
                        if self._is_ast_node_static(raw_caption):
                            caption = f"Choice {len(self._runtime_captions) + 1}"
                        else:
                            caption = str(raw_caption)
                    else:
                        caption = str(item) if item is not None else ""
                    
                    clean = re.sub(r'\{[^}]*\}', '', caption).strip()
                    self._runtime_captions.append(clean)
                except Exception as e:
                    urw_log.warn(f"Error extracting caption: {e}", "PROCESSOR")
                    self._runtime_captions.append(f"Choice {len(self._runtime_captions) + 1}")
            
        def process_choice(self, menu_node, choice_index, info):
            """Extract and process consequences for a single choice"""
            
            cache_key = (id(menu_node), choice_index)
            cached = urw_consequence_cache.get(cache_key)
            if cached is not None:
                return cached
                
            consequences = []
            
            try:
                ast_items = menu_node.items if hasattr(menu_node, 'items') else []
                
                menu_item = None
                
                if choice_index < len(self._runtime_captions):
                    runtime_caption = self._runtime_captions[choice_index]
                    
                    for ast_item in ast_items:
                        if ast_item and len(ast_item) >= 1:
                            try:
                                raw_caption = ast_item[0]
                                # Skip if it's an AST node
                                if self._is_ast_node_static(raw_caption):
                                    continue
                                # Use repr for safety to avoid triggering __str__ side effects
                                ast_caption = str(raw_caption) if raw_caption is not None else ""
                                ast_caption_clean = re.sub(r'\{[^}]*\}', '', ast_caption).strip()
                                
                                if ast_caption_clean == runtime_caption:
                                    menu_item = ast_item
                                    break
                            except Exception:
                                continue
                
                if menu_item is None:
                    offset = info.get('offset', 0) if info else 0
                    actual_index = choice_index + offset
                    
                    if actual_index < len(ast_items):
                        menu_item = ast_items[actual_index]
                    else:
                        urw_log.warn(f"Choice index {actual_index} out of range (AST has {len(ast_items)} items)", "PROCESSOR")
                        return consequences
                
                if menu_item is None:
                    urw_log.warn(f"Could not find AST item for choice {choice_index}", "PROCESSOR")
                    return consequences
                
                # Menu item structure: (label, condition, block)
                if len(menu_item) >= 3 and menu_item[2]:
                    choice_block = menu_item[2]
                    consequences = urw_analyzer.analyze_block(choice_block)
                    
                # Filter consequences
                consequences = self._filter_consequences(consequences)
                
                # Deduplicate
                consequences = self._deduplicate(consequences)
                
                # Sort by priority
                consequences.sort(key=lambda c: -c.get_priority())
                
                # Cache the result
                urw_consequence_cache.set(cache_key, consequences)
                
            except Exception as e:
                urw_log.error(f"Error processing choice {choice_index}: {e}", "PROCESSOR")
                
            return consequences
            
        def _filter_consequences(self, consequences):
            """Apply all filters to consequences"""
            filtered = []
            
            filters = persistent.urw_filters
            name_filters = persistent.urw_name_filters
            
            for cons in consequences:
                # Type filter
                if not self._passes_type_filter(cons, filters):
                    continue
                    
                # Name filter
                if not self._passes_name_filter(cons, name_filters):
                    continue
                    
                filtered.append(cons)
                
            return filtered
            
        def _passes_type_filter(self, cons, filters):
            """Check if consequence passes type filters"""
            ctype = cons.type
            
            # Map consequence types to filter keys
            type_map = {
                ConsequenceType.INCREASE: 'variables',
                ConsequenceType.DECREASE: 'variables',
                ConsequenceType.ASSIGN: 'variables',
                ConsequenceType.BOOLEAN: 'flags',
                ConsequenceType.CONDITION: 'conditions',
                ConsequenceType.JUMP: 'flow',
                ConsequenceType.CALL: 'flow',
                ConsequenceType.RETURN: 'flow',
                ConsequenceType.FUNCTION: 'functions',
                ConsequenceType.RELATIONSHIP: 'relationships',
                ConsequenceType.STAT: 'stats',
                ConsequenceType.FLAG: 'flags',
                ConsequenceType.UNKNOWN: 'unknown'
            }
            
            filter_key = type_map.get(ctype, 'unknown')
            return filters.get(filter_key, True)
            
        def _passes_name_filter(self, cons, name_filters):
            """Check if consequence passes name-based filters"""
            var_name = str(cons.variable).lower()
            
            # Check custom show list first (priority)
            custom_show = name_filters.get('custom_show', [])
            for pattern in custom_show:
                if pattern.lower() in var_name:
                    return True  # Always show if in custom show list
                    
            # Check custom hide list
            custom_hide = name_filters.get('custom_hide', [])
            for pattern in custom_hide:
                if var_name.startswith(pattern.lower()):
                    return False
                    
            # Built-in filters
            if name_filters.get('hide_underscore', True) and var_name.startswith('_'):
                return False
                
            if name_filters.get('hide_renpy', True) and 'renpy.' in var_name:
                return False
                
            if name_filters.get('hide_config', False) and 'config.' in var_name:
                return False
                
            if name_filters.get('hide_store', True) and 'store.' in var_name:
                return False
                
            if name_filters.get('hide_internal', True):
                internal_prefixes = ['__', '_internal', '_temp', '_debug']
                for prefix in internal_prefixes:
                    if var_name.startswith(prefix):
                        return False
                        
            return True
            
        def _deduplicate(self, consequences):
            """Remove duplicate consequences"""
            seen = set()
            unique = []
            
            for cons in consequences:
                key = (cons.type, cons.variable, cons.value)
                if key not in seen:
                    seen.add(key)
                    unique.append(cons)
                    
            return unique
            
        def categorize_variable(self, var_name):
            """Categorize a variable based on naming patterns"""
            var_lower = var_name.lower()
            
            for kw in self.RELATIONSHIP_KEYWORDS:
                if kw in var_lower:
                    return ConsequenceType.RELATIONSHIP
                    
            for kw in self.STAT_KEYWORDS:
                if kw in var_lower:
                    return ConsequenceType.STAT
                    
            for kw in self.FLAG_KEYWORDS:
                if kw in var_lower:
                    return ConsequenceType.FLAG
                    
            return None
    
    urw_processor = URWProcessor()
    
    ##################################################################
    #                URW FORMATTER                                   #
    ##################################################################
    
    class URWFormatter:
        """Format consequences for display"""
        
        # Theme definitions
        THEMES = {
            'modern': {
                'increase': '#4CAF50',   # Green
                'decrease': '#F44336',   # Red
                'assign': '#2196F3',     # Blue
                'boolean': '#00BCD4',    # Cyan
                'jump': '#FF9800',       # Orange
                'call': '#8BC34A',       # Light Green
                'return': '#E91E63',     # Pink
                'condition': '#FFEB3B',  # Yellow
                'function': '#9C27B0',   # Purple
                'code': '#9E9E9E',       # Gray
                'relationship': '#FF4081',  # Pink accent
                'stat': '#FFD600',       # Amber
                'flag': '#00E676',       # Green accent
                'unknown': '#757575',    # Dark gray
                'separator': '#666',
                'more': '#888'
            },
            'classic': {
                'increase': '#4f4',
                'decrease': '#f44',
                'assign': '#44f',
                'boolean': '#4af',
                'jump': '#f84',
                'call': '#8f4',
                'return': '#f48',
                'condition': '#ff8',
                'function': '#af4',
                'code': '#ccc',
                'relationship': '#f4a',
                'stat': '#fa4',
                'flag': '#4fa',
                'unknown': '#888',
                'separator': '#666',
                'more': '#888'
            },
            'minimal': {
                'increase': '#8f8',
                'decrease': '#f88',
                'assign': '#88f',
                'boolean': '#8ff',
                'jump': '#fb8',
                'call': '#8f8',
                'return': '#f8f',
                'condition': '#ff8',
                'function': '#bf8',
                'code': '#ddd',
                'relationship': '#f8c',
                'stat': '#fc8',
                'flag': '#8fc',
                'unknown': '#aaa',
                'separator': '#888',
                'more': '#aaa'
            },
            'dark': {
                'increase': '#2E7D32',
                'decrease': '#C62828',
                'assign': '#1565C0',
                'boolean': '#00838F',
                'jump': '#EF6C00',
                'call': '#558B2F',
                'return': '#AD1457',
                'condition': '#F9A825',
                'function': '#6A1B9A',
                'code': '#616161',
                'relationship': '#C2185B',
                'stat': '#FF8F00',
                'flag': '#00695C',
                'unknown': '#424242',
                'separator': '#444',
                'more': '#555'
            }
        }
        
        def __init__(self):
            pass
            
        def get_theme(self):
            """Get current theme colors"""
            theme_name = persistent.urw_theme
            return self.THEMES.get(theme_name, self.THEMES['modern'])
            
        def format_consequences(self, consequences, max_display=None, show_all=None):
            """Format consequences list for display"""
            if not consequences:
                return ""
                
            if max_display is None:
                max_display = persistent.urw_max_consequences
            if show_all is None:
                show_all = persistent.urw_show_all
                
            theme = self.get_theme()
            
            # Apply display limit if not showing all
            display_consequences = consequences if show_all else consequences[:max_display]
            
            formatted_parts = []
            
            for cons in display_consequences:
                formatted = self._format_single(cons, theme)
                if formatted:
                    formatted_parts.append(formatted)
                    
            # Join with separator
            result = " | ".join(formatted_parts)
            
            # Add "more" indicator
            if not show_all and len(consequences) > max_display:
                remaining = len(consequences) - max_display
                more_color = theme.get('more', '#888')
                result += f" | {{color={more_color}}}+{remaining} more{{/color}}"
                
            return result
            
        def _format_single(self, cons, theme, full_text=None):
            """Format a single consequence"""
            if full_text is None:
                full_text = persistent.urw_full_text
                
            ctype = cons.type
            color = theme.get(ctype, theme.get('unknown', '#888'))
            
            # Get icon
            meta = ConsequenceType.get_metadata(ctype)
            icon = meta['icon']
            
            # Escape special characters
            var = self._escape_renpy(str(cons.variable))
            val = self._escape_renpy(str(cons.value)) if cons.value else ""
            
            # Truncation limits (only apply if not full_text mode)
            val_limit = 50 if full_text else 12
            cond_limit = 80 if full_text else 25
            func_limit = 60 if full_text else 20
            compact_limit = 80 if full_text else 30
            
            # Format based on type
            if ctype == ConsequenceType.INCREASE:
                if val and val != '1':
                    text = f"{icon}{var} (+{val})"
                else:
                    text = f"{icon}{var}"
                    
            elif ctype == ConsequenceType.DECREASE:
                if val and val != '1':
                    text = f"{icon}{var} (-{val})"
                else:
                    text = f"{icon}{var}"
                    
            elif ctype in [ConsequenceType.ASSIGN, ConsequenceType.BOOLEAN]:
                if len(val) > val_limit:
                    val = val[:val_limit-2] + ".."
                text = f"{var}={val}"
                
            elif ctype == ConsequenceType.JUMP:
                text = f"{icon} {var}"
                
            elif ctype == ConsequenceType.CALL:
                text = f"{icon} {var}"
                
            elif ctype == ConsequenceType.RETURN:
                text = f"{icon}"
                
            elif ctype == ConsequenceType.CONDITION:
                cond = var[:cond_limit-2] + ".." if len(var) > cond_limit else var
                text = f"{icon} {cond}"
                
            elif ctype == ConsequenceType.FUNCTION:
                func = var[:func_limit-2] + ".." if len(var) > func_limit else var
                text = f"{icon} {func}"
                
            else:
                compact = cons.format("compact")
                text = compact[:compact_limit-2] + ".." if len(compact) > compact_limit else compact
                
            return f"{{color={color}}}{text}{{/color}}"
            
        def _escape_renpy(self, text):
            """Escape Ren'Py formatting characters"""
            # Double up brackets to escape them
            text = text.replace('{', '{{').replace('}', '}}')
            text = text.replace('[', '[[').replace(']', ']]')
            return text
            
        def format_for_urw_tag(self, consequences, prefix="WT: "):
            """Format consequences for URW custom text tag"""
            if not consequences:
                return ""
                
            raw_text = self.format_consequences(consequences)
            # Strip color tags for URW tag (it handles coloring internally)
            raw_text = re.sub(r'\{color=[^}]+\}|\{/color\}', '', raw_text)
            
            return raw_text
    
    urw_formatter = URWFormatter()
    
    ##################################################################
    #                URW TEXT DISPLAYABLE                            #
    ##################################################################
    
    class URWTextDisplayable(renpy.Displayable):
        """Custom displayable for walkthrough text with smart coloring"""
        
        def __init__(self, text, size=25, base_color="#888", prefix="WT: ", **kwargs):
            super(URWTextDisplayable, self).__init__(**kwargs)
            self.text = text
            self.size = size
            self.base_color = base_color
            self.prefix = prefix
            
            # Create the colored text
            colored_text = self._create_colored_text()
            self.child = renpy.text.text.Text(
                colored_text,
                outlines=[(2, "#000", 0, 0)],
                font="DejaVuSans.ttf",
                **kwargs
            )
            
        def _create_colored_text(self):
            """Create text with color tags based on content"""
            theme = urw_formatter.get_theme()
            
            # Start with size and prefix
            result = f"{{size={self.size}}}{{color={self.base_color}}}{self.prefix}{{/color}}"
            
            # Split by separator
            parts = self.text.split(' | ')
            
            for i, part in enumerate(parts):
                if i > 0:
                    result += " | "
                    
                # Determine color based on content
                color = self._get_color_for_part(part, theme)
                result += f"{{color={color}}}{part}{{/color}}"
                
            result += "{/size}"
            return result
            
        def _get_color_for_part(self, part, theme):
            """Determine color for a consequence part"""
            part_lower = part.lower()
            
            if part.startswith('+'):
                return theme['increase']
            elif part.startswith('-') and 'more' not in part:
                return theme['decrease']
            elif '=' in part and '==' not in part:
                if 'true' in part_lower or 'false' in part_lower:
                    return theme['boolean']
                return theme['assign']
            elif part.startswith('→'):
                return theme['jump']
            elif part.startswith('⇒'):
                return theme['call']
            elif part.startswith('←'):
                return theme['return']
            elif part.startswith('?'):
                return theme['condition']
            elif part.startswith('ƒ'):
                return theme['function']
            elif 'more' in part:
                return theme['more']
            else:
                return self.base_color
                
        def render(self, width, height, st, at):
            return self.child.render(width, height, st, at)
            
        def visit(self):
            return [self.child]
    
    ##################################################################
    #                URW TEXT TAG HANDLER                            #
    ##################################################################
    
    def urw_tag_handler(tag, argument, contents):
        """
        Custom text tag handler for URW
        Usage: {urw=size:25,color:#888,prefix:WT: }consequences{/urw}
        """
        new_list = []
        
        size = persistent.urw_text_size
        color = "#888"
        prefix = "WT: "
        
        if argument:
            args = argument.lower().split(',')
            for arg in args:
                arg = arg.strip()
                if arg.startswith('size:'):
                    try:
                        size = int(arg.split(':')[1])
                    except:
                        pass
                elif arg.startswith('color:'):
                    color = arg.split(':', 1)[1]
                elif arg.startswith('prefix:'):
                    prefix = arg.split(':', 1)[1]
                    
        # Combine all text content
        full_text = ""
        for kind, text in contents:
            if kind == renpy.TEXT_TEXT:
                full_text += text
                
        if full_text:
            displayable = URWTextDisplayable(full_text, size, color, prefix)
            new_list.append((renpy.TEXT_DISPLAYABLE, displayable))
            
        return new_list
    
    def register_urw_tag():
        """Register URW text tag with all case variations"""
        base_tag = "urw"
        registered = []
        
        # Generate all 2^4 = 16 case combinations for "URW"
        for i in range(16):
            variant = ""
            for j, char in enumerate(base_tag):
                if (i >> j) & 1:
                    variant += char.upper()
                else:
                    variant += char.lower()
            config.custom_text_tags[variant] = urw_tag_handler
            registered.append(variant)
            
        urw_log.debug(f"Registered {len(registered)} tag variants for urw", "INIT")
        return registered
    
    # Register the tag
    _urw_tag_variants = register_urw_tag()
    
    ##################################################################
    #                URW MENU WRAPPER                                #
    ##################################################################
    
    class URWMenuWrapper:
        """Wraps the menu function to inject walkthrough hints"""
        
        def __init__(self):
            self._original_menu = None
            self._call_count = 0
            self._last_menu_node = None
            self._last_match_info = None
            
        def install(self):
            """Install the menu wrapper"""
            if self._original_menu is None:
                self._original_menu = renpy.exports.menu
                renpy.exports.menu = self._wrapped_menu
                urw_log.info("URW menu wrapper installed", "INIT")
                
        def uninstall(self):
            """Uninstall the menu wrapper"""
            if self._original_menu is not None:
                renpy.exports.menu = self._original_menu
                self._original_menu = None
                urw_log.info("URW menu wrapper uninstalled", "INIT")
        
        def _get_item_caption(self, item):
            """Extract caption from menu item (handles both tuple and object formats)"""
            if hasattr(item, 'caption'):
                return str(item.caption)
            elif isinstance(item, (list, tuple)) and len(item) > 0:
                return str(item[0]) if item[0] is not None else ""
            elif isinstance(item, str):
                return item
            else:
                return str(item) if item is not None else ""
                
        def _wrapped_menu(self, items, set_expr=None, args=None, kwargs=None, item_arguments=None, **extra_kwargs):
            """Wrapped menu function with walkthrough integration"""
            self._call_count += 1
            
            if items is None:
                return self._original_menu(items, set_expr, args, kwargs, item_arguments)
            
            try:
                if not isinstance(items, (list, tuple)):
                    items = list(items)
            except:
                urw_log.warn(f"Could not convert items to list: {type(items).__name__}", "MENU")
                return self._original_menu(items, set_expr, args, kwargs, item_arguments)
            
            if len(items) == 0:
                return self._original_menu(items, set_expr, args, kwargs, item_arguments)
            
            # Validate item formats - skip if any item is a raw AST node
            for check_item in items:
                # Check the item itself
                if hasattr(check_item, '__class__'):
                    module = getattr(check_item.__class__, '__module__', '')
                    if 'ast' in str(module):
                        urw_log.warn(f"Menu items contains AST node: {type(check_item).__name__}", "MENU")
                        return self._original_menu(items, set_expr, args, kwargs, item_arguments)
                # Check caption attribute if present
                if hasattr(check_item, 'caption'):
                    cap = check_item.caption
                    if hasattr(cap, '__class__'):
                        cap_module = getattr(cap.__class__, '__module__', '')
                        if 'ast' in str(cap_module):
                            urw_log.warn(f"Menu item caption is AST node: {type(cap).__name__}", "MENU")
                            return self._original_menu(items, set_expr, args, kwargs, item_arguments)
                # Check tuple/list items
                if isinstance(check_item, (list, tuple)) and len(check_item) > 0:
                    first_elem = check_item[0]
                    if hasattr(first_elem, '__class__'):
                        elem_module = getattr(first_elem.__class__, '__module__', '')
                        if 'ast' in str(elem_module):
                            urw_log.warn(f"Menu item tuple has AST node: {type(first_elem).__name__}", "MENU")
                            return self._original_menu(items, set_expr, args, kwargs, item_arguments)
            
            if not persistent.urw_enabled:
                return self._original_menu(items, set_expr, args, kwargs, item_arguments)
                
            urw_log.debug(f"Processing menu #{self._call_count} with {len(items)} items", "MENU")
            
            try:
                urw_processor.set_runtime_captions(items)
                
                menu_node, match_info = urw_menu_finder.find_menu_node(items)
                
                if menu_node is None:
                    urw_log.warn("Could not find menu node, showing original menu", "MENU")
                    self._last_menu_node = None
                    self._last_match_info = None
                    return self._original_menu(items, set_expr, args, kwargs, item_arguments)
                
                # Store for full viewer access
                self._last_menu_node = menu_node
                self._last_match_info = match_info
                    
                # Enhance each item with consequences
                enhanced_items = []
                
                for i, item in enumerate(items):
                    enhanced_item = self._enhance_item(item, i, menu_node, match_info)
                    enhanced_items.append(enhanced_item)
                    
                # Update statistics
                if persistent.urw_stats:
                    persistent.urw_stats['menus_analyzed'] = persistent.urw_stats.get('menus_analyzed', 0) + 1
                    
                return self._original_menu(enhanced_items, set_expr, args, kwargs, item_arguments)
                
            except URWAnalyzer.CONTROL_EXCEPTIONS:
                raise
            except Exception as e:
                urw_log.error(f"Error in wrapped menu: {e}", "MENU")
                return self._original_menu(items, set_expr, args, kwargs, item_arguments)
                
        def _is_ast_node(self, obj):
            """Check if an object is a Ren'Py AST node"""
            if obj is None:
                return False
            # Check module path for ast
            try:
                module = getattr(obj.__class__, '__module__', '')
                if 'ast' in str(module):
                    return True
                # Also check class name patterns
                class_name = obj.__class__.__name__
                if class_name in ('Menu', 'Say', 'Jump', 'Call', 'Python', 'If', 'Label', 'Scene', 'Show', 'Hide', 'With'):
                    if hasattr(obj, 'linenumber') or hasattr(obj, 'filename'):
                        return True
            except:
                pass
            return False
        
        def _enhance_item(self, item, index, menu_node, match_info):
            """Add consequence hints to a menu item"""
            try:
                # Early check: if item itself is an AST node, skip processing
                if self._is_ast_node(item):
                    urw_log.warn(f"Item is AST node, skipping: {type(item).__name__}", "MENU")
                    return item
                
                if hasattr(item, 'caption'):
                    raw_caption = item.caption
                    if self._is_ast_node(raw_caption):
                        urw_log.warn(f"Caption is AST node, skipping: {type(raw_caption).__name__}", "MENU")
                        return item
                    caption = str(raw_caption)
                    is_object_style = True

                elif isinstance(item, (list, tuple)) and len(item) >= 1:
                    raw_caption = item[0]

                    if self._is_ast_node(raw_caption):
                        urw_log.warn(f"Caption in tuple is AST node, skipping: {type(raw_caption).__name__}", "MENU")
                        return item
                    caption = raw_caption
                    rest = item[1:] if len(item) > 1 else ()
                    is_object_style = False
                    
                    if not isinstance(caption, str):
                        if hasattr(caption, '__str__'):
                            caption = str(caption)
                        else:
                            urw_log.warn(f"Caption is not a string: {type(caption).__name__}", "MENU")
                            return item
                else:
                    if self._is_ast_node(item):
                        return item
                    caption = str(item) if item is not None else ""
                    rest = ()
                    is_object_style = False
                
                if not isinstance(caption, str):
                    urw_log.warn(f"Caption conversion failed, type: {type(caption).__name__}", "MENU")
                    return item
                
                try:
                    caption = renpy.substitute(caption)
                except:
                    pass
                
                consequences = urw_processor.process_choice(menu_node, index, match_info)
                
                if consequences:
                    # Format consequences
                    formatted = urw_formatter.format_for_urw_tag(consequences)
                    
                    if formatted:
                        size = persistent.urw_text_size
                        # Add walkthrough hint using urw tag
                        new_caption = caption + f"\n{{urw=size:{size},color:#888,prefix:WT: }}{formatted}{{/urw}}"
                        
                        # Update statistics
                        if persistent.urw_stats:
                            persistent.urw_stats['consequences_shown'] = persistent.urw_stats.get('consequences_shown', 0) + len(consequences)
                        
                        # For object-style items, we need to modify the caption attribute
                        if is_object_style:
                            # Try to modify the caption directly
                            try:
                                item.caption = new_caption
                                return item
                            except AttributeError:
                                # Caption is read-only, can't modify object-style items
                                urw_log.debug("Cannot modify object-style menu item caption", "MENU")
                                return item
                        else:
                            # Reconstruct tuple-style item
                            if rest:
                                return (new_caption,) + tuple(rest)
                            else:
                                return new_caption
                
                # No consequences or no formatting - return original
                return item
                    
            except Exception as e:
                urw_log.error(f"Error enhancing item: {e}", "MENU")
                return item  # Return original item unchanged
    
    urw_menu_wrapper = URWMenuWrapper()
    
    ##################################################################
    #                URW INITIALIZATION                              #
    ##################################################################
    
    def urw_init():
        """Initialize URW"""
        urw_log.info(f"Initializing URW v{urw_config.VERSION}", "INIT")
        
        urw_menu_wrapper.install()
        
        if persistent.urw_stats:
            persistent.urw_stats['session_start'] = _time.strftime("%Y-%m-%d %H:%M:%S")
            
        def on_quit():
            urw_menu_cache.clear()
            urw_consequence_cache.clear()
            urw_node_cache.clear()
            if hasattr(urw_menu_finder, 'reset_sequence'):
                urw_menu_finder.reset_sequence()
            urw_log.info("URW 2.0 caches cleared on quit", "CLEANUP")
            
        config.quit_callbacks.append(on_quit)
        
        urw_log.info("URW initialization complete", "INIT")
        print(f"[URW] Universal Ren'Py Walkthrough System v{urw_config.VERSION} loaded")
        
    def urw_clear_caches():
        """Clear all URW caches"""
        urw_menu_cache.clear()
        urw_consequence_cache.clear()
        urw_node_cache.clear()
        # Reset sequence tracking
        if hasattr(urw_menu_finder, 'reset_sequence'):
            urw_menu_finder.reset_sequence()
        urw_log.info("All caches cleared", "CACHE")
        
    def urw_get_stats():
        """Get URW statistics"""
        return {
            'version': urw_config.VERSION,
            'menu_cache': urw_menu_cache.stats(),
            'consequence_cache': urw_consequence_cache.stats(),
            'node_cache': urw_node_cache.stats(),
            'menus_analyzed': persistent.urw_stats.get('menus_analyzed', 0),
            'consequences_shown': persistent.urw_stats.get('consequences_shown', 0),
            'session_start': persistent.urw_stats.get('session_start', 'N/A')
        }
    
    def urw_get_current_menu_consequences():
        """Get consequences for all choices in the current menu (for full viewer)"""
        result = []
        
        try:
            # Get the last processed menu from the wrapper
            if not hasattr(urw_menu_wrapper, '_last_menu_node') or not urw_menu_wrapper._last_menu_node:
                return result
                
            menu_node = urw_menu_wrapper._last_menu_node
            match_info = urw_menu_wrapper._last_match_info or {'offset': 0}
            
            if not hasattr(menu_node, 'items'):
                return result
            
            # Use runtime captions if available for proper matching
            runtime_captions = urw_processor._runtime_captions if hasattr(urw_processor, '_runtime_captions') else []
            
            # Helper to check for AST nodes
            def is_ast_node(obj):
                if obj is None:
                    return False
                try:
                    module = getattr(obj.__class__, '__module__', '')
                    return 'ast' in str(module)
                except:
                    return False
            
            # Iterate over runtime captions (what the player sees) not AST items
            if runtime_captions:
                for idx, runtime_caption in enumerate(runtime_captions):
                    try:
                        # Skip if caption is somehow an AST node
                        if is_ast_node(runtime_caption):
                            urw_log.warn(f"Runtime caption is AST node, skipping: {type(runtime_caption).__name__}", "VIEWER")
                            result.append({
                                'index': idx,
                                'caption': f"Choice {idx + 1}",
                                'consequences': []
                            })
                            continue
                        
                        # Find matching AST item
                        menu_item = None
                        for ast_item in menu_node.items:
                            if ast_item and len(ast_item) >= 1:
                                raw_caption = ast_item[0]
                                # Skip if this AST caption is itself an AST node
                                if is_ast_node(raw_caption):
                                    continue
                                ast_caption = str(raw_caption) if raw_caption else ""
                                ast_caption_clean = re.sub(r'\{[^}]*\}', '', ast_caption).strip()
                                
                                if ast_caption_clean == runtime_caption:
                                    menu_item = ast_item
                                    break
                        
                        # Get consequences using caption matching
                        consequences = urw_processor.process_choice(menu_node, idx, match_info)
                        
                        result.append({
                            'index': idx,
                            'caption': str(runtime_caption),  # Use runtime caption as string
                            'consequences': consequences
                        })
                    except Exception as item_error:
                        urw_log.error(f"Error processing menu item {idx}: {item_error}", "VIEWER")
                        result.append({
                            'index': idx,
                            'caption': str(runtime_caption) if runtime_caption else f"Choice {idx + 1}",
                            'consequences': []
                        })
            else:
                # Fallback: iterate AST items directly
                for idx, item in enumerate(menu_node.items):
                    try:
                        # Get caption - handle various item formats
                        if isinstance(item, (list, tuple)) and len(item) > 0:
                            raw_caption = item[0]
                            # Check for AST node
                            if is_ast_node(raw_caption):
                                caption = f"Choice {idx + 1}"
                            else:
                                caption = str(raw_caption) if raw_caption else f"Choice {idx + 1}"
                        else:
                            if is_ast_node(item):
                                caption = f"Choice {idx + 1}"
                            else:
                                caption = str(item) if item else f"Choice {idx + 1}"
                        
                        # Ensure caption is a string and not too weird
                        if not isinstance(caption, str) or 'ast.' in caption.lower():
                            caption = f"Choice {idx + 1}"
                        
                        # Strip Ren'Py formatting from caption for display
                        clean_caption = re.sub(r'\{[^}]+\}', '', caption)
                        
                        consequences = urw_processor.process_choice(menu_node, idx, match_info)
                        
                        result.append({
                            'index': idx,
                            'caption': clean_caption,
                            'consequences': consequences
                        })
                    except Exception as item_error:
                        urw_log.error(f"Error processing menu item {idx}: {item_error}", "VIEWER")
                        result.append({
                            'index': idx,
                            'caption': f"Choice {idx + 1}",
                            'consequences': []
                        })
                
        except Exception as e:
            urw_log.error(f"Error getting menu consequences: {e}", "VIEWER")
            
        return result
    
    def urw_copy_debug_info():
        """Copy debug info to clipboard for bug reporting"""
        import pygame
        
        try:
            # Get game info
            game_name = config.name if hasattr(config, 'name') and config.name else "Unknown Game"
            game_version = config.version if hasattr(config, 'version') and config.version else "Unknown"
            
            # Get Ren'Py version
            renpy_version = renpy.version_string if hasattr(renpy, 'version_string') else "Unknown"
            
            # Get URW version
            urw_version = urw_config.VERSION
            
            # Get system info
            import platform
            os_info = platform.platform()
            
            # Helper to get node location from node name
            def get_node_info(node_name):
                """Get filename:linenumber from a node name"""
                try:
                    if node_name is None:
                        return "None"
                    node = renpy.game.script.lookup(node_name)
                    if node and hasattr(node, 'filename') and hasattr(node, 'linenumber'):
                        return f"{node.filename}:{node.linenumber}"
                    return f"(node: {node_name})"
                except Exception:
                    return f"(lookup failed: {node_name})"
            
            # Get current context - multiple methods
            context_info = "N/A"
            context_details = []
            try:
                ctx = renpy.game.context()
                if ctx:
                    # Method 1
                    if hasattr(ctx, 'current') and ctx.current:
                        loc_info = get_node_info(ctx.current)
                        context_details.append(f"current: {loc_info}")
                    
                    # Method 2
                    if hasattr(ctx, 'call_location_stack'):
                        stack = ctx.call_location_stack
                        if isinstance(stack, (list, tuple)) and stack:
                            for i, node_name in enumerate(list(stack)[-3:]):  # Last 3 entries
                                loc_info = get_node_info(node_name)
                                context_details.append(f"call_stack[{i}]: {loc_info}")
                    
                    # Method 3
                    if hasattr(ctx, 'return_stack'):
                        stack = ctx.return_stack
                        if isinstance(stack, (list, tuple)) and stack:
                            for i, node_name in enumerate(list(stack)[-3:]):  # Last 3 entries
                                loc_info = get_node_info(node_name)
                                context_details.append(f"return_stack[{i}]: {loc_info}")
                
                context_info = "\n  ".join(context_details) if context_details else "N/A"
            except Exception as e:
                context_info = f"Error: {e}"
            
            # Get last runtime captions
            last_captions = "N/A"
            try:
                if hasattr(urw_processor, '_runtime_captions') and urw_processor._runtime_captions:
                    last_captions = "\n  ".join([f"- {c}" for c in urw_processor._runtime_captions[:10]])
            except:
                pass
            
            # Get sequence tracking info
            sequence_info = "N/A"
            try:
                if hasattr(urw_menu_finder, '_global_menu_index'):
                    global_idx = urw_menu_finder._global_menu_index
                    global_history = urw_menu_finder._global_menu_history
                    label_idx = getattr(urw_menu_finder, '_menu_index_in_label', 0)
                    last_label = urw_menu_finder._last_label or "None"
                    # Show last 10 seen menu lines
                    recent = global_history[-10:] if len(global_history) > 10 else global_history
                    sequence_info = f"Global Index: {global_idx}, Recent Lines: {recent}\n  Label: {last_label}, Label Index: {label_idx}"
            except:
                pass
            
            logs = urw_log.get_logs(50)
            logs_text = "\n".join(logs) if logs else "No logs available"
            
            # Build report
            report = f"""=== URW 2.0 Debug Report ===
Generated: {_time.strftime("%Y-%m-%d %H:%M:%S")}

[Game Information]
Game: {game_name}
Game Version: {game_version}
Ren'Py Version: {renpy_version}

[URW Information]
URW Version: {urw_version}
URW Enabled: {persistent.urw_enabled}
Text Size: {persistent.urw_text_size}
Max Consequences: {persistent.urw_max_consequences}

[System Information]
OS: {os_info}

[Current Context]
  {context_info}

[Last Menu Captions]
  {last_captions}

[Sequence Tracking]
  {sequence_info}

[Debug Logs (Last 50)]
{logs_text}

=== End of Report ==="""

            pygame.scrap.init()
            pygame.scrap.put(pygame.SCRAP_TEXT, report.encode('utf-8'))
            
            renpy.notify("Debug info copied to clipboard!")
            urw_log.info("Debug info copied to clipboard", "DEBUG")
            
        except Exception as e:
            urw_log.error(f"Failed to copy debug info: {e}", "DEBUG")
            renpy.notify(f"Failed to copy: {e}")
    
    urw_init()


## Styles for URW ##
style URW_toggle_button:
    background "#333"
    hover_background "#555"
    selected_background "#4a9eff"
    
style URW_size_button:
    background "#444"
    hover_background "#666"
    
style URW_preset_button:
    background "#333"
    hover_background "#6bb8ff"
    
style URW_close_button:
    background "#4a9eff"
    hover_background "#6bb8ff"
    
style URW_danger_button:
    background "#f44"
    hover_background "#f66"

transform URW_fade_in:
    alpha 0.0
    ease 0.4 alpha 1.0

transform URW_slide_in_left:
    alpha 0.0 xoffset -50
    ease 0.4 alpha 1.0 xoffset 0

transform URW_slide_in_right:
    alpha 0.0 xoffset 50
    ease 0.4 alpha 1.0 xoffset 0

transform URW_slide_in_up:
    alpha 0.0 yoffset -30
    ease 0.4 alpha 1.0 yoffset 0
