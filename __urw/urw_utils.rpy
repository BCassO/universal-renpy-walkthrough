####################################################################
####     Universal Ren'Py Walkthrough System v2.0 (Enhanced)    ####
####               (C) Knox Emberlyn 2025-2026                  ####
####            Utilities, Compatibility & Extensions           ####
####################################################################

init -996 python:
    ##################################################################
    #                URW COMPATIBILITY LAYER                         #
    ##################################################################
    
    class URWCompatibility:
        """Provides compatibility with URW 1.x persistent settings"""
        
        @staticmethod
        def migrate_settings():
            """Migrate settings from URW 1.x"""
            
            # Check if old settings exist
            if hasattr(persistent, 'universal_walkthrough_enabled'):
                persistent.urw_enabled = persistent.universal_walkthrough_enabled
                urw_log.info("Migrated: universal_walkthrough_enabled", "COMPAT")
                
            if hasattr(persistent, 'universal_wt_text_size'):
                persistent.urw_text_size = persistent.universal_wt_text_size
                urw_log.info("Migrated: universal_wt_text_size", "COMPAT")
                
            if hasattr(persistent, 'universal_wt_max_consequences'):
                persistent.urw_max_consequences = persistent.universal_wt_max_consequences
                urw_log.info("Migrated: universal_wt_max_consequences", "COMPAT")
                
            if hasattr(persistent, 'universal_wt_show_all_available'):
                persistent.urw_show_all = persistent.universal_wt_show_all_available
                urw_log.info("Migrated: universal_wt_show_all_available", "COMPAT")
                
            # Migrate filters
            if hasattr(persistent, 'universal_wt_filters'):
                old_filters = persistent.universal_wt_filters
                
                if old_filters is None:
                    old_filters = {}
                
                # Map old filter names to new ones
                filter_map = {
                    'conditions': 'conditions',
                    'jumps': 'flow',
                    'calls': 'flow',
                    'returns': 'flow',
                    'increases': 'variables',
                    'decreases': 'variables',
                    'assignments': 'variables',
                    'booleans': 'flags',
                    'functions': 'functions',
                    'code': 'variables',
                    'unknown': 'unknown'
                }
                
                for old_key, new_key in filter_map.items():
                    if old_key in old_filters:
                        # OR with existing value since multiple old keys map to same new key
                        current = persistent.urw_filters.get(new_key, True)
                        persistent.urw_filters[new_key] = current or old_filters[old_key]
                        
                urw_log.info("Migrated: filter settings", "COMPAT")
                
            if hasattr(persistent, 'universal_wt_name_filters'):
                old_name_filters = persistent.universal_wt_name_filters
                
                if old_name_filters is None:
                    old_name_filters = {}
                
                direct_map = {
                    'hide_underscore': 'hide_underscore',
                    'hide_renpy': 'hide_renpy',
                    'hide_config': 'hide_config',
                    'hide_store': 'hide_store'
                }
                
                for old_key, new_key in direct_map.items():
                    if old_key in old_name_filters:
                        persistent.urw_name_filters[new_key] = old_name_filters[old_key]
                        
                # Handle custom filters
                if 'custom_prefix' in old_name_filters and old_name_filters['custom_prefix']:
                    prefixes = [p.strip() for p in old_name_filters['custom_prefix'].split(';') if p.strip()]
                    persistent.urw_name_filters['custom_hide'] = prefixes
                    
                urw_log.info("Migrated: name filter settings", "COMPAT")
        
        @staticmethod
        def ensure_defaults():
            """Ensure all critical persistent values have valid defaults (handles None cases)"""
            if persistent.urw_text_size is None:
                persistent.urw_text_size = 25
            if persistent.urw_max_consequences is None:
                persistent.urw_max_consequences = 3
            if persistent.urw_enabled is None:
                persistent.urw_enabled = True
            if persistent.urw_show_all is None:
                persistent.urw_show_all = True
            if persistent.urw_spoiler_mode is None:
                persistent.urw_spoiler_mode = False
            if persistent.urw_highlight_best is None:
                persistent.urw_highlight_best = True
            if persistent.urw_theme is None:
                persistent.urw_theme = "modern"
            if persistent.urw_full_text is None:
                persistent.urw_full_text = False
            if persistent.urw_hide_dialogue is None:
                persistent.urw_hide_dialogue = True
    
    URWCompatibility.migrate_settings()
    URWCompatibility.ensure_defaults()
    
    ##################################################################
    #                URW VARIABLE TRACKER                            #
    ##################################################################
    
    class URWVariableTracker:
        """Track variable changes during gameplay"""
        
        def __init__(self):
            self._tracked_vars = set()
            self._history = []
            self._max_history = 1000
            self._snapshot = {}
            
        def track(self, var_name):
            """Add a variable to tracking"""
            self._tracked_vars.add(var_name)
            
        def untrack(self, var_name):
            """Remove a variable from tracking"""
            self._tracked_vars.discard(var_name)
            
        def take_snapshot(self):
            """Take a snapshot of tracked variables"""
            store = renpy.store
            self._snapshot = {}
            
            for var in self._tracked_vars:
                if hasattr(store, var):
                    self._snapshot[var] = getattr(store, var)
                    
        def get_changes(self):
            """Get changes since last snapshot"""
            changes = []
            store = renpy.store
            
            for var in self._tracked_vars:
                if hasattr(store, var):
                    current = getattr(store, var)
                    old = self._snapshot.get(var)
                    
                    if old != current:
                        changes.append({
                            'variable': var,
                            'old': old,
                            'new': current,
                            'timestamp': _time.time()
                        })
                        
            return changes
            
        def record_change(self, var_name, old_value, new_value):
            """Record a variable change"""
            self._history.append({
                'variable': var_name,
                'old': old_value,
                'new': new_value,
                'timestamp': _time.time()
            })
            
            # Trim history
            if len(self._history) > self._max_history:
                self._history = self._history[-self._max_history//2:]
                
        def get_history(self, var_name=None, count=50):
            """Get change history"""
            if var_name:
                return [h for h in self._history if h['variable'] == var_name][-count:]
            return self._history[-count:]
            
        def clear_history(self):
            """Clear change history"""
            self._history.clear()
    
    urw_var_tracker = URWVariableTracker()
    
    ##################################################################
    #                URW CHOICE HISTORY                              #
    ##################################################################
    
    class URWChoiceHistory:
        """Track player choices for statistics and analysis"""
        
        def __init__(self):
            self._session_choices = []
            
        def record_choice(self, menu_label, choice_text, choice_index, consequences):
            """Record a player's choice"""
            entry = {
                'menu_label': menu_label,
                'choice_text': choice_text[:100],  # Truncate long text
                'choice_index': choice_index,
                'consequence_count': len(consequences),
                'timestamp': _time.strftime("%Y-%m-%d %H:%M:%S")
            }
            
            self._session_choices.append(entry)
            
            if not persistent.urw_choice_history:
                persistent.urw_choice_history = []
                
            persistent.urw_choice_history.append(entry)
            
            max_history = persistent.urw_max_history
            if len(persistent.urw_choice_history) > max_history:
                persistent.urw_choice_history = persistent.urw_choice_history[-max_history:]
                
        def get_session_choices(self):
            """Get choices from current session"""
            return self._session_choices
            
        def get_all_choices(self):
            """Get all recorded choices"""
            return persistent.urw_choice_history or []
            
        def get_choice_stats(self):
            """Get statistics about choices"""
            choices = self.get_all_choices()
            
            if not choices:
                return {'total': 0}
                
            return {
                'total': len(choices),
                'session': len(self._session_choices),
                'avg_consequences': sum(c['consequence_count'] for c in choices) / len(choices)
            }
            
        def clear_history(self):
            """Clear all choice history"""
            self._session_choices.clear()
            persistent.urw_choice_history = []
    
    urw_choice_history = URWChoiceHistory()
    
    ##################################################################
    #                URW SPOILER PROTECTION                          #
    ##################################################################
    
    class URWSpoilerGuard:
        """Protect against spoilers in walkthrough hints"""
        
        # Keywords that might indicate spoilers
        SPOILER_KEYWORDS = frozenset([
            'death', 'dies', 'dead', 'kill', 'murder', 'ending', 'finale',
            'secret', 'hidden', 'reveal', 'twist', 'surprise', 'betray',
            'pregnant', 'wedding', 'marriage', 'divorce'
        ])
        
        def __init__(self):
            self._enabled = False
            
        def enable(self):
            self._enabled = True
            
        def disable(self):
            self._enabled = False
            
        def is_enabled(self):
            return self._enabled
            
        def filter_consequence(self, consequence):
            """Check if consequence should be hidden due to spoilers"""
            if not self._enabled:
                return False  # Not filtered
                
            var_lower = str(consequence.variable).lower()
            val_lower = str(consequence.value).lower()
            
            for keyword in self.SPOILER_KEYWORDS:
                if keyword in var_lower or keyword in val_lower:
                    return True  # Filter this consequence
                    
            return False
            
        def censor_text(self, text):
            """Censor potentially spoilery text"""
            if not self._enabled:
                return text
                
            text_lower = text.lower()
            
            for keyword in self.SPOILER_KEYWORDS:
                if keyword in text_lower:
                    return "[Spoiler Hidden]"
                    
            return text
    
    urw_spoiler_guard = URWSpoilerGuard()
    
    ##################################################################
    #                URW BEST CHOICE HIGHLIGHTER                     #
    ##################################################################
    
    class URWBestChoiceAnalyzer:
        """Analyze choices to suggest the 'best' one (optional feature)"""
        
        # Positive variable patterns
        POSITIVE_PATTERNS = [
            'love', 'trust', 'affection', 'relationship', 'friendship',
            'respect', 'loyalty', 'points', 'money', 'health', 'reputation'
        ]
        
        def __init__(self):
            self._enabled = False
            
        def enable(self):
            self._enabled = True
            
        def disable(self):
            self._enabled = False
            
        def analyze_choices(self, menu_node, match_info):
            """Analyze all choices and return best choice index"""
            if not self._enabled:
                return None
                
            scores = []
            
            for i in range(len(menu_node.items)):
                try:
                    consequences = urw_processor.process_choice(menu_node, i, match_info)
                    score = self._score_consequences(consequences)
                    scores.append((i, score))
                except:
                    scores.append((i, 0))
                    
            if not scores:
                return None
                
            # Return index with highest score
            best = max(scores, key=lambda x: x[1])
            return best[0] if best[1] > 0 else None
            
        def _score_consequences(self, consequences):
            """Score a set of consequences"""
            score = 0
            
            for cons in consequences:
                var_lower = str(cons.variable).lower()
                
                # Check for positive patterns
                is_positive = any(p in var_lower for p in self.POSITIVE_PATTERNS)
                
                if cons.type == ConsequenceType.INCREASE:
                    score += 10 if is_positive else 5
                elif cons.type == ConsequenceType.DECREASE:
                    score -= 10 if is_positive else 5
                elif cons.type == ConsequenceType.BOOLEAN:
                    if str(cons.value).lower() == 'true' and is_positive:
                        score += 5
                        
            return score
    
    urw_best_analyzer = URWBestChoiceAnalyzer()
    
    ##################################################################
    #                URW EXPORT/IMPORT                               #
    ##################################################################
    
    class URWDataManager:
        """Export and import URW settings"""
        
        @staticmethod
        def export_settings():
            """Export all settings as a dictionary"""
            return {
                'version': urw_config.VERSION,
                'enabled': persistent.urw_enabled,
                'text_size': persistent.urw_text_size,
                'max_consequences': persistent.urw_max_consequences,
                'show_all': persistent.urw_show_all,
                'theme': persistent.urw_theme,
                'filters': dict(persistent.urw_filters),
                'name_filters': dict(persistent.urw_name_filters)
            }
            
        @staticmethod
        def import_settings(data):
            """Import settings from a dictionary"""
            if 'enabled' in data:
                persistent.urw_enabled = data['enabled']
            if 'text_size' in data:
                persistent.urw_text_size = data['text_size']
            if 'max_consequences' in data:
                persistent.urw_max_consequences = data['max_consequences']
            if 'show_all' in data:
                persistent.urw_show_all = data['show_all']
            if 'theme' in data:
                persistent.urw_theme = data['theme']
            if 'filters' in data:
                persistent.urw_filters.update(data['filters'])
            if 'name_filters' in data:
                persistent.urw_name_filters.update(data['name_filters'])
                
            urw_log.info("Settings imported successfully", "DATA")
            
        @staticmethod
        def reset_all():
            """Reset all settings to defaults"""
            persistent.urw_enabled = True
            persistent.urw_text_size = 25
            persistent.urw_max_consequences = 3
            persistent.urw_show_all = True
            persistent.urw_theme = "modern"
            persistent.urw_spoiler_mode = False
            persistent.urw_highlight_best = True
            
            persistent.urw_filters = {
                'variables': True,
                'conditions': True,
                'flow': True,
                'functions': True,
                'flags': True,
                'relationships': True,
                'stats': True,
                'unknown': False
            }
            
            persistent.urw_name_filters = {
                'hide_underscore': True,
                'hide_renpy': True,
                'hide_config': False,
                'hide_store': True,
                'hide_internal': True,
                'custom_hide': [],
                'custom_show': [],
                'important_vars': []
            }
            
            urw_clear_caches()
            urw_log.info("All settings reset to defaults", "DATA")
    
    urw_data = URWDataManager()
    
    ##################################################################
    #                URW DEVELOPER TOOLS                             #
    ##################################################################
    
    class URWDevTools:
        """Developer tools for testing and debugging"""
        
        @staticmethod
        def dump_menu_info(items):
            """Dump detailed menu information"""
            menu_node, match_info = urw_menu_finder.find_menu_node(items)
            
            info = {
                'found': menu_node is not None,
                'match_info': match_info,
                'item_count': len(items),
            }
            
            if menu_node:
                info['node_info'] = {
                    'filename': getattr(menu_node, 'filename', 'N/A'),
                    'linenumber': getattr(menu_node, 'linenumber', 0),
                    'menu_item_count': len(menu_node.items) if hasattr(menu_node, 'items') else 0
                }
                
            return info
            
        @staticmethod
        def test_consequence_extraction(menu_node, choice_index):
            """Test consequence extraction for a specific choice"""
            if not menu_node:
                return {'error': 'No menu node provided'}
                
            try:
                consequences = urw_processor.process_choice(menu_node, choice_index, {'offset': 0})
                
                return {
                    'count': len(consequences),
                    'consequences': [
                        {
                            'type': c.type,
                            'variable': c.variable,
                            'value': c.value,
                            'priority': c.get_priority()
                        }
                        for c in consequences
                    ]
                }
            except Exception as e:
                return {'error': str(e)}
                
        @staticmethod
        def benchmark_menu_finding(iterations=100):
            """Benchmark menu finding performance"""
            import time
            
            # This would need actual menu items to test
            return {
                'message': 'Benchmark requires active menu context',
                'iterations': iterations
            }
    
    urw_dev = URWDevTools()
    
    ##################################################################
    #                URW PUBLIC API                                  #
    ##################################################################
    
    # Public API functions for game developers to use
    
    def urw_enable():
        """Enable URW"""
        persistent.urw_enabled = True
        urw_log.info("URW enabled via API", "API")
        
    def urw_disable():
        """Disable URW"""
        persistent.urw_enabled = False
        urw_log.info("URW disabled via API", "API")
        
    def urw_toggle():
        """Toggle URW on/off"""
        persistent.urw_enabled = not persistent.urw_enabled
        state = "enabled" if persistent.urw_enabled else "disabled"
        urw_log.info(f"URW {state} via API", "API")
        
    def urw_set_theme(theme_name):
        """Set the display theme"""
        if theme_name in urw_formatter.THEMES:
            persistent.urw_theme = theme_name
            urw_log.info(f"Theme set to '{theme_name}'", "API")
        else:
            urw_log.warn(f"Unknown theme: {theme_name}", "API")
            
    def urw_add_important_var(var_name):
        """Mark a variable as important (always show)"""
        if var_name not in persistent.urw_name_filters['important_vars']:
            persistent.urw_name_filters['important_vars'].append(var_name)
            
    def urw_hide_prefix(prefix):
        """Add a prefix to hide"""
        if prefix not in persistent.urw_name_filters['custom_hide']:
            persistent.urw_name_filters['custom_hide'].append(prefix)
            
    def urw_show_prefix(prefix):
        """Add a prefix to always show"""
        if prefix not in persistent.urw_name_filters['custom_show']:
            persistent.urw_name_filters['custom_show'].append(prefix)

    ##################################################################
    #                URW FINAL INITIALIZATION                        #
    ##################################################################
    
    urw_log.info("URW utilities and extensions loaded", "INIT")
    print(f"[URW] All modules loaded successfully - Ready to assist!")
    
init python:
    def urw_after_load():
        if hasattr(store, 'urw_menu_finder') and hasattr(urw_menu_finder, 'reset_sequence'):
            urw_menu_finder.reset_sequence()
            urw_log.info("Menu sequence reset after load", "LOAD")
    
    config.after_load_callbacks.append(urw_after_load)
