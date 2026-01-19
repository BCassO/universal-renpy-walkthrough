####################################################################
####     Universal Ren'Py Walkthrough System v2.0 (Enhanced)    ####
####               (C) Knox Emberlyn 2025-2026                  ####
####          Consolidated for Ren'Py 7.x.x Compatibility       ####
####################################################################

init -1000 python:
    # URW Configuration namespace
    class URWConfig(object):
        """URW Configuration Container"""
        VERSION = "2.0.0"
        DEBUG = False  # Changed from True to False - reduces console spam
        DEVELOPER = True  # Changed from True to False - hides debug button
        
        # Cache settings
        MAX_MENU_CACHE = 500
        MAX_CONSEQUENCE_CACHE = 300
        CACHE_CLEANUP_THRESHOLD = 0.8
        
        # Analysis settings
        MAX_RECURSION_DEPTH = 10
        MAX_CONSEQUENCES_PER_CHOICE = 50
        ANALYZE_NESTED_CONDITIONALS = True
        
        # Display settings
        DEFAULT_TEXT_SIZE = 18
        DEFAULT_MAX_DISPLAY = 3
        
    urw_config = URWConfig()

init -999:
    # CRITICAL: Define persistent variables - set to None initially
    # This allows saved values to be loaded without being overwritten
    default persistent.urw_enabled = None
    default persistent.urw_text_size = None
    default persistent.urw_max_consequences = None
    default persistent.urw_show_all = None
    default persistent.urw_spoiler_mode = None
    default persistent.urw_highlight_best = None
    default persistent.urw_theme = None
    default persistent.urw_full_text = None
    default persistent.urw_hide_dialogue = None
    default persistent.urw_logs_cleared = None 
    
    # Type filters
    default persistent.urw_filters = None
    
    # Name-based filters
    default persistent.urw_name_filters = None
    
    # Choice history
    default persistent.urw_choice_history = None
    
    # Statistics
    default persistent.urw_stats = None
    
    # Maximum history
    default persistent.urw_max_history = 100

init -998 python:
    # This runs BEFORE persistent values are loaded from disk!
    # So we can't use persistent values here yet
    import collections
    import weakref
    import time as _time
    import re
    import ast
    import hashlib
    
    ##################################################################
    #                    ENHANCED DEBUG LOGGING                     #
    ##################################################################
    
    class URWLogger(object):
        """Enhanced logging system for URW with persistent debugging"""
        
        _instance = None
        
        def __new__(cls, *args, **kwargs):
            if not cls._instance:
                cls._instance = super(URWLogger, cls).__new__(cls, *args, **kwargs)
            return cls._instance
        
        def __init__(self):
            if getattr(self, '_initialized', False):
                return
            self._initialized = True
            self._log_buffer = []
            self._max_buffer = 2000
            self._enabled = True
            self._persistent_debug = True
            
            # Don't check persistent here - it's handled in urw_init()
            # Startup logging will be done after persistent values are loaded
    
        def clear(self):
            """Clear logs and mark as cleared in persistent storage"""
            self._log_buffer = []
            persistent.urw_logs_cleared = True
            urw_force_save()  # Save immediately
        
        def log(self, message, level="INFO", category="GENERAL"):
            """Log a message with level and category"""
            # Always log PERSISTENT category messages
            if not self._enabled and level != "ERROR" and category != "PERSISTENT":
                return
                
            timestamp = _time.strftime("%H:%M:%S")
            entry = "[URW {0}] [{1}] [{2}] {3}".format(timestamp, level, category, message)
            
            self._log_buffer.append(entry)
            if len(self._log_buffer) > self._max_buffer:
                self._log_buffer = self._log_buffer[-self._max_buffer//2:]
            
            # Always print persistent debug messages
            if category == "PERSISTENT" or urw_config.DEBUG:
                print(entry)
        
        def debug(self, message, category="DEBUG"):
            self.log(message, "DEBUG", category)
            
        def info(self, message, category="INFO"):
            self.log(message, "INFO", category)
            
        def warn(self, message, category="WARN"):
            self.log(message, "WARN", category)
            
        def error(self, message, category="ERROR"):
            self.log(message, "ERROR", category)
            
        def persistent_debug(self, message):
            """Special debug for persistent issues"""
            self.log(message, "DEBUG", "PERSISTENT")
            
        def get_logs(self, count=100):
            return self._log_buffer[-count:]
            
        def dump_to_file(self, filename="urw_log_dump.txt"):
            """Dump all logs to file for debugging"""
            try:
                with open(filename, "w") as f:
                    f.write("\n".join(self._log_buffer))
                self.persistent_debug("Logs dumped to {0}".format(filename))
            except Exception as e:
                self.error("Failed to dump logs: {0}".format(e))
    
    urw_log = URWLogger()
    
    ##################################################################
    #                    URW PERSISTENT SETTINGS FIX                #
    ##################################################################
    
    def urw_ensure_persistent_defaults():
        """Ensure all persistent settings have valid defaults with minimal logging"""
        defaults_set = []
        
        # Check if persistent attributes exist and are not None
        if not hasattr(persistent, 'urw_enabled') or persistent.urw_enabled is None:
            persistent.urw_enabled = True
            defaults_set.append('urw_enabled')
        
        if not hasattr(persistent, 'urw_text_size') or persistent.urw_text_size is None:
            persistent.urw_text_size = urw_config.DEFAULT_TEXT_SIZE
            defaults_set.append('urw_text_size')
        
        if not hasattr(persistent, 'urw_max_consequences') or persistent.urw_max_consequences is None:
            persistent.urw_max_consequences = urw_config.DEFAULT_MAX_DISPLAY
            defaults_set.append('urw_max_consequences')
        
        if not hasattr(persistent, 'urw_show_all') or persistent.urw_show_all is None:
            persistent.urw_show_all = True
            defaults_set.append('urw_show_all')
        
        if not hasattr(persistent, 'urw_spoiler_mode') or persistent.urw_spoiler_mode is None:
            persistent.urw_spoiler_mode = False
            defaults_set.append('urw_spoiler_mode')
        
        if not hasattr(persistent, 'urw_highlight_best') or persistent.urw_highlight_best is None:
            persistent.urw_highlight_best = True
            defaults_set.append('urw_highlight_best')
        
        if not hasattr(persistent, 'urw_theme') or persistent.urw_theme is None:
            persistent.urw_theme = "modern"
            defaults_set.append('urw_theme')
        
        if not hasattr(persistent, 'urw_full_text') or persistent.urw_full_text is None:
            persistent.urw_full_text = False
            defaults_set.append('urw_full_text')
        
        if not hasattr(persistent, 'urw_hide_dialogue') or persistent.urw_hide_dialogue is None:
            persistent.urw_hide_dialogue = True
            defaults_set.append('urw_hide_dialogue')
        
        if not hasattr(persistent, 'urw_logs_cleared') or persistent.urw_logs_cleared is None:
            persistent.urw_logs_cleared = False
            defaults_set.append('urw_logs_cleared')
        
        # Ensure dictionaries exist
        if not hasattr(persistent, 'urw_filters') or persistent.urw_filters is None:
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
            defaults_set.append('urw_filters')
        
        if not hasattr(persistent, 'urw_name_filters') or persistent.urw_name_filters is None:
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
            defaults_set.append('urw_name_filters')
        
        if not hasattr(persistent, 'urw_stats') or persistent.urw_stats is None:
            persistent.urw_stats = {
                'menus_analyzed': 0,
                'choices_made': 0,
                'consequences_shown': 0,
                'session_start': None
            }
            defaults_set.append('urw_stats')
        
        if not hasattr(persistent, 'urw_choice_history') or persistent.urw_choice_history is None:
            persistent.urw_choice_history = []
            defaults_set.append('urw_choice_history')
        
        if defaults_set and urw_config.DEBUG:
            urw_log.persistent_debug("Set defaults for: {0}".format(", ".join(defaults_set)))
        
        return defaults_set
        
    def urw_force_save():
        """Force save persistent data immediately with minimal logging"""
        try:
            renpy.save_persistent()
            return True
        except Exception as e:
            # Only log errors if debug is enabled
            if urw_config.DEBUG:
                urw_log.error("Failed to save persistent data: {0}".format(e), "PERSISTENT")
            return False
    
    def urw_log_persistent_changes(action, variable_name, old_value, new_value):
        """Log changes to persistent variables with safe escaping"""
        # Escape dictionary values
        if isinstance(old_value, dict):
            old_str = "dict with {0} items".format(len(old_value))
        else:
            old_str = repr(old_value)
            
        if isinstance(new_value, dict):
            new_str = "dict with {0} items".format(len(new_value))
        else:
            new_str = repr(new_value)
        
        urw_log.persistent_debug("PERSISTENT CHANGE: {0} '{1}' from {2} to {3}".format(
            action, variable_name, old_str, new_str))
    
    # Don't call urw_ensure_persistent_defaults() here anymore!
    # We'll call it later after persistent values are loaded
    
    ##################################################################
    #                    URW CACHE SYSTEM                            #
    ##################################################################
    
    class URWCache(object):
        """LRU Cache with automatic cleanup and statistics"""
        
        def __init__(self, max_size=500, name="cache"):
            self.name = name
            self.max_size = max_size
            self._cache = {}
            self._access_times = {}
            self._hit_count = 0
            self._miss_count = 0
            
        def get(self, key, default=None):
            """Get item from cache"""
            if key in self._cache:
                self._access_times[key] = _time.time()
                self._hit_count += 1
                return self._cache[key]
            self._miss_count += 1
            return default
            
        def set(self, key, value):
            """Set item in cache with automatic cleanup"""
            if len(self._cache) >= self.max_size * urw_config.CACHE_CLEANUP_THRESHOLD:
                self._cleanup()
            
            self._cache[key] = value
            self._access_times[key] = _time.time()
            
        def has(self, key):
            return key in self._cache
            
        def remove(self, key):
            if key in self._cache:
                del self._cache[key]
                del self._access_times[key]
                
        def _cleanup(self):
            """Remove oldest entries"""
            if len(self._cache) < self.max_size // 2:
                return
                
            sorted_items = sorted(self._access_times.items(), key=lambda x: x[1])
            remove_count = len(self._cache) // 4
            
            for i in range(min(remove_count, len(sorted_items))):
                key = sorted_items[i][0]
                if key in self._cache:
                    del self._cache[key]
                if key in self._access_times:
                    del self._access_times[key]
                    
            urw_log.debug("Cache '{0}' cleaned: removed {1} entries".format(self.name, remove_count), "CACHE")
            
        def clear(self):
            self._cache = {}
            self._access_times = {}
            
        def stats(self):
            total = self._hit_count + self._miss_count
            hit_rate = (self._hit_count / total * 100) if total > 0 else 0
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hit_count,
                'misses': self._miss_count,
                'hit_rate': "{0:.1f}%".format(hit_rate)
            }
    
    # Global caches
    urw_menu_cache = URWCache(urw_config.MAX_MENU_CACHE, "menu")
    urw_consequence_cache = URWCache(urw_config.MAX_CONSEQUENCE_CACHE, "consequence")
    urw_node_cache = URWCache(200, "node")
    
    ##################################################################
    #                URW CONSEQUENCE TYPES                           #
    ##################################################################
    
    class ConsequenceType(object):
        """Enumeration of consequence types with metadata"""
        
        INCREASE = "increase"
        DECREASE = "decrease"
        ASSIGN = "assign"
        BOOLEAN = "boolean"
        JUMP = "jump"
        CALL = "call"
        RETURN = "return"
        CONDITION = "condition"
        FUNCTION = "function"
        CODE = "code"
        RELATIONSHIP = "relationship"
        STAT = "stat"
        FLAG = "flag"
        UNKNOWN = "unknown"
        
        # Metadata for each type
        METADATA = {
            "increase": {"icon": "+", "color": "#4f4", "priority": 10},
            "decrease": {"icon": "-", "color": "#f44", "priority": 10},
            "assign": {"icon": "=", "color": "#44f", "priority": 5},
            "boolean": {"icon": "●", "color": "#4af", "priority": 6},
            "jump": {"icon": "→", "color": "#f84", "priority": 3},
            "call": {"icon": "⇒", "color": "#8f4", "priority": 4},
            "return": {"icon": "←", "color": "#f48", "priority": 2},
            "condition": {"icon": "?", "color": "#ff8", "priority": 1},
            "function": {"icon": "ƒ", "color": "#af4", "priority": 5},
            "code": {"icon": "◇", "color": "#ccc", "priority": 0},
            "relationship": {"icon": "♥", "color": "#f4a", "priority": 15},
            "stat": {"icon": "★", "color": "#fa4", "priority": 12},
            "flag": {"icon": "◆", "color": "#4fa", "priority": 8},
            "unknown": {"icon": "?", "color": "#888", "priority": -1}
        }
        
        @classmethod
        def get_metadata(cls, type_name):
            return cls.METADATA.get(type_name, cls.METADATA["unknown"])
    
    ##################################################################
    #                URW CONSEQUENCE CLASS                           #
    ##################################################################
    
    class URWConsequence(object):
        """Represents a single consequence from a choice"""
        
        def __init__(self, ctype, variable, value="", display="", source_line=0, confidence=1.0, sub_consequences=None, branch_consequences=None):
            self.type = ctype
            self.variable = variable
            self.value = value
            self.display = display or "{0}".format(variable)
            self.source_line = source_line
            self.confidence = confidence
            self.metadata = ConsequenceType.get_metadata(ctype)
            self.sub_consequences = sub_consequences or []
            self.branch_consequences = branch_consequences or {}
            
        def __repr__(self):
            return "<Consequence {0}: {1}={2}>".format(self.type, self.variable, self.value)
            
        def __eq__(self, other):
            if not isinstance(other, URWConsequence):
                return False
            return (self.type == other.type and 
                    self.variable == other.variable and 
                    self.value == other.value)
                    
        def __hash__(self):
            return hash((self.type, self.variable, self.value))
            
        def format(self, style="compact"):
            """Format consequence for display"""
            meta = self.metadata
            icon = meta["icon"]
            
            if style == "compact":
                if self.type in ["increase", "decrease"]:
                    if self.value and self.value != "1":
                        return "{0}{1} ({2})".format(icon, self.variable, self.value)
                    return "{0}{1}".format(icon, self.variable)
                elif self.type == "assign":
                    val = self.value[:15] + "..." if len(str(self.value)) > 15 else self.value
                    return "{0}={1}".format(self.variable, val)
                elif self.type == "boolean":
                    return "{0}={1}".format(self.variable, self.value)
                elif self.type in ["jump", "call"]:
                    return "{0} {1}".format(icon, self.variable)
                elif self.type == "return":
                    return "{0}".format(icon)
                elif self.type == "condition":
                    cond = str(self.variable)[:25]
                    return "{0} {1}".format(icon, cond)
                else:
                    return self.display[:30]
            
            elif style == "detailed":
                return "{0} {1}: {2} = {3}".format(icon, self.type.upper(), self.variable, self.value)
            
            return self.display
            
        def get_priority(self):
            """Get display priority (higher = more important)"""
            base_priority = self.metadata["priority"]
            
            var_lower = str(self.variable).lower()
            relationship_keywords = ['love', 'trust', 'affection', 'relationship', 'faith', 
                                'friendship', 'respect', 'loyalty', 're_']
            stat_keywords = ['points', 'money', 'health', 'reputation', 'stat', 'score',
                        'strength', 'intelligence', 'charisma']
            
            for kw in relationship_keywords:
                if kw in var_lower:
                    return base_priority + 20
                    
            for kw in stat_keywords:
                if kw in var_lower:
                    return base_priority + 15
                    
            return base_priority
    
    ##################################################################
    #                URW AST ANALYZER                                #
    ##################################################################
    
    class URWAnalyzer(object):
        """AST analyzer for extracting consequences - Python 2.7 compatible"""
        
        CONTROL_EXCEPTIONS = (
            renpy.game.FullRestartException,
            renpy.game.UtterRestartException,
            renpy.game.QuitException,
            renpy.game.JumpException,
            renpy.game.JumpOutException,
            renpy.game.CallException,
            renpy.game.EndReplay,
            renpy.game.ParseErrorException,
            KeyboardInterrupt
        )
        
        SKIP_STATEMENTS = (
            'Say', 'Scene', 'Show', 'Hide', 'With', 'ShowLayer', 
            'Camera', 'Transform', 'Pass', 'Label', 'Play', 'Stop',
            'Queue', 'Voice', 'Sound', 'Music', 'Pause', 'Comment',
            'Translate', 'TranslateBlock', 'EndTranslate', 'TranslateString',
            'TranslatePython', 'TranslateEarlyPython', 'TranslateSay'
        )
        
        def __init__(self):
            self._depth = 0
            self._max_depth = urw_config.MAX_RECURSION_DEPTH
        
        def analyze_block(self, block, depth=0):
            if depth > self._max_depth:
                urw_log.warn("Max recursion depth reached at {0}".format(depth), "ANALYZER")
                return []
                
            consequences = []
            
            if block is None:
                return consequences
                
            if isinstance(block, (list, tuple)):
                statements = block
            elif hasattr(block, 'children'):
                statements = block.children
            elif hasattr(block, '__iter__'):
                statements = list(block)
            else:
                return consequences
                
            for stmt in statements:
                try:
                    stmt_consequences = self._analyze_statement(stmt, depth)
                    consequences.extend(stmt_consequences)
                except self.CONTROL_EXCEPTIONS:
                    raise
                except Exception as e:
                    urw_log.error("Error analyzing statement: {0}".format(e), "ANALYZER")
                    continue
                    
            return consequences
            
        def _analyze_statement(self, stmt, depth):
            consequences = []
            
            if stmt is None:
                return consequences
                
            stmt_class = stmt.__class__.__name__
            
            if stmt_class in self.SKIP_STATEMENTS:
                return consequences
                
            if stmt_class == 'Python':
                consequences.extend(self._analyze_python(stmt, depth))
                
            elif stmt_class == 'Jump':
                target = getattr(stmt, 'target', '?')
                consequences.append(URWConsequence(
                    ConsequenceType.JUMP, target, '', "→ {0}".format(target),
                    getattr(stmt, 'linenumber', 0)
                ))
                
            elif stmt_class == 'Call':
                label = getattr(stmt, 'label', '?')
                consequences.append(URWConsequence(
                    ConsequenceType.CALL, label, '', "⇒ {0}".format(label),
                    getattr(stmt, 'linenumber', 0)
                ))
                
            elif stmt_class == 'Return':
                expr = getattr(stmt, 'expression', None)
                val = str(expr) if expr else 'end'
                consequences.append(URWConsequence(
                    ConsequenceType.RETURN, 'return', val, "← {0}".format(val),
                    getattr(stmt, 'linenumber', 0)
                ))
                
            elif stmt_class == 'If':
                consequences.extend(self._analyze_conditional(stmt, depth))
                
            elif stmt_class == 'While':
                consequences.extend(self._analyze_while(stmt, depth))
                
            elif stmt_class == 'Menu':
                pass
                
            elif stmt_class == 'UserStatement':
                pass
                
            else:
                for attr in ['target', 'label', 'expression', 'name', 'value']:
                    if hasattr(stmt, attr):
                        value = getattr(stmt, attr)
                        if value and not str(value).startswith('_'):
                            consequences.append(URWConsequence(
                                ConsequenceType.UNKNOWN,
                                "{0}.{1}".format(stmt_class, attr), str(value)[:30], '',
                                getattr(stmt, 'linenumber', 0),
                                confidence=0.5
                            ))
                            break
                            
            return consequences
            
        def _analyze_python(self, stmt, depth):
            consequences = []
            source = None
            
            if hasattr(stmt, 'code'):
                code_obj = stmt.code
                if hasattr(code_obj, 'source'):
                    source = code_obj.source
                elif hasattr(code_obj, 'py'):
                    source = code_obj.py
                    
            if not source:
                return consequences
                
            try:
                consequences.extend(self._parse_python_ast(source, depth))
            except:
                consequences.extend(self._parse_python_regex(source))
                
            return consequences
            
        def _parse_python_ast(self, source, depth):
            consequences = []
            
            try:
                tree = ast.parse(source)
                
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        for target in node.targets:
                            if isinstance(target, ast.Name):
                                var_name = target.id
                                try:
                                    if isinstance(node.value, ast.Num):
                                        value = str(node.value.n)
                                    elif isinstance(node.value, ast.Str):
                                        value = node.value.s
                                    elif hasattr(ast, 'NameConstant') and isinstance(node.value, ast.NameConstant):
                                        value = str(node.value.value)
                                    elif isinstance(node.value, ast.Name):
                                        value = node.value.id
                                    else:
                                        value = "?"
                                        
                                    ctype = ConsequenceType.ASSIGN
                                    if str(value).lower() in ['true', 'false']:
                                        ctype = ConsequenceType.BOOLEAN
                                        
                                    consequences.append(URWConsequence(
                                        ctype, var_name, value[:50]
                                    ))
                                except:
                                    consequences.append(URWConsequence(
                                        ConsequenceType.ASSIGN, var_name, "?"
                                    ))
                    
                    elif isinstance(node, ast.AugAssign):
                        if isinstance(node.target, ast.Name):
                            var_name = node.target.id
                            op = node.op.__class__.__name__
                            
                            try:
                                if isinstance(node.value, ast.Num):
                                    value = str(node.value.n)
                                elif isinstance(node.value, ast.Str):
                                    value = node.value.s
                                elif hasattr(ast, 'NameConstant') and isinstance(node.value, ast.NameConstant):
                                    value = str(node.value.value)
                                else:
                                    value = "?"
                            except:
                                value = "?"
                                
                            if op == 'Add':
                                consequences.append(URWConsequence(
                                    ConsequenceType.INCREASE, var_name, value
                                ))
                            elif op == 'Sub':
                                consequences.append(URWConsequence(
                                    ConsequenceType.DECREASE, var_name, value
                                ))
                    
                    elif isinstance(node, ast.If):
                        try:
                            condition_text = "unknown_condition"
                            
                            try:
                                condition_text = ast.dump(node.test)
                                if 'config.developer' in condition_text:
                                    condition_text = condition_text.replace('config.developer', 'developer_mode')
                                if '_in_replay' in condition_text:
                                    condition_text = condition_text.replace('_in_replay', 'in_replay')
                                    
                                if hasattr(node.test, 'id'):
                                    condition_text = node.test.id
                                elif hasattr(node.test, 'attr'):
                                    condition_text = "*.{0}".format(node.test.attr)
                            except:
                                pass
                            
                            has_else = node.orelse is not None and len(node.orelse) > 0
                            has_elif = has_else and any(isinstance(n, ast.If) for n in node.orelse)
                            
                            if has_elif:
                                condition_text += " (+elif)"
                            elif has_else:
                                condition_text += "-else"
                            
                            if len(condition_text) > 35:
                                condition_text = condition_text[:32] + "..."
                                
                            consequences.append(URWConsequence(
                                ConsequenceType.CONDITION, "if {0}".format(condition_text), ""
                            ))
                        except:
                            pass
                    
                    elif isinstance(node, ast.Call):
                        try:
                            if isinstance(node.func, ast.Name):
                                call_text = node.func.id
                            elif isinstance(node.func, ast.Attribute):
                                call_text = "*.{0}".format(node.func.attr)
                            else:
                                call_text = "function"
                                
                            if not any(skip in call_text for skip in 
                                    ['renpy.pause', 'renpy.sound', 'renpy.music', 
                                    'renpy.scene', 'renpy.show', 'renpy.hide']):
                                consequences.append(URWConsequence(
                                    ConsequenceType.FUNCTION, call_text[:40], ""
                                ))
                        except:
                            pass
                            
            except SyntaxError:
                pass
            except Exception as e:
                urw_log.debug("AST parse error: {0}".format(e), "ANALYZER")
                
            return consequences
            
        def _parse_python_regex(self, source):
            consequences = []
            
            lines = source.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                if line.startswith('if ') and ':' in line:
                    try:
                        condition_part = line.split('if ')[1].split(':')[0].strip()
                        
                        if 'config.developer' in condition_part:
                            condition_part = condition_part.replace('config.developer', 'developer_mode')
                        if '_in_replay' in condition_part:
                            condition_part = condition_part.replace('_in_replay', 'in_replay')
                        
                        if len(condition_part) > 35:
                            condition_part = condition_part[:32] + "..."
                        
                        consequences.append(URWConsequence(
                            ConsequenceType.CONDITION, "if {0}".format(condition_part), "1"
                        ))
                    except:
                        consequences.append(URWConsequence(
                            ConsequenceType.CONDITION, "if condition", "1"
                        ))
                
                elif line.startswith('elif ') and ':' in line:
                    try:
                        condition_part = line.split('elif ')[1].split(':')[0].strip()
                        
                        if 'config.developer' in condition_part:
                            condition_part = condition_part.replace('config.developer', 'developer_mode')
                        if '_in_replay' in condition_part:
                            condition_part = condition_part.replace('_in_replay', 'in_replay')
                        
                        if len(condition_part) > 35:
                            condition_part = condition_part[:32] + "..."
                        
                        consequences.append(URWConsequence(
                            ConsequenceType.CONDITION, "elif {0}".format(condition_part), "1"
                        ))
                    except:
                        consequences.append(URWConsequence(
                            ConsequenceType.CONDITION, "elif condition", "1"
                        ))
                
                elif line.strip() == 'else:':
                    consequences.append(URWConsequence(
                        ConsequenceType.CONDITION, "else", "1"
                    ))
                    
                elif '+=' in line:
                    try:
                        var, val = line.split('+=', 1)
                        var = re.sub(r'\[.*?\]', '', var.strip())
                        val = val.strip()
                        
                        try:
                            if val.isdigit():
                                actual_value = val
                            elif val.replace('.', '').isdigit():
                                actual_value = val
                            elif val.startswith('-') and val[1:].isdigit():
                                actual_value = val
                            else:
                                actual_value = val
                        except:
                            actual_value = val
                            
                        consequences.append(URWConsequence(
                            ConsequenceType.INCREASE, var, actual_value[:20]
                        ))
                    except:
                        pass
                        
                elif '-=' in line:
                    try:
                        var, val = line.split('-=', 1)
                        var = re.sub(r'\[.*?\]', '', var.strip())
                        val = val.strip()
                        
                        try:
                            if val.isdigit():
                                actual_value = val
                            elif val.replace('.', '').isdigit():
                                actual_value = val
                            elif val.startswith('-') and val[1:].isdigit():
                                actual_value = val
                            else:
                                actual_value = val
                        except:
                            actual_value = val
                            
                        consequences.append(URWConsequence(
                            ConsequenceType.DECREASE, var, actual_value[:20]
                        ))
                    except:
                        pass
                        
                elif '=' in line and '==' not in line and '!=' not in line and '<=' not in line and '>=' not in line:
                    if not any(line.startswith(x) for x in ['if ', 'elif ', 'for ', 'while ', 'def ', 'class ']):
                        try:
                            var, val = line.split('=', 1)
                            var = re.sub(r'\[.*?\]', '', var.strip())
                            val = val.strip()
                            
                            if not var.startswith('_') and len(var) > 1:
                                ctype = ConsequenceType.ASSIGN
                                if val.lower() in ['true', 'false']:
                                    ctype = ConsequenceType.BOOLEAN
                                    
                                consequences.append(URWConsequence(
                                    ctype, var, val[:20]
                                ))
                        except:
                            pass
                            
                elif any(keyword in line.lower() for keyword in [' = true', ' = false']):
                    try:
                        var, val = line.split('=', 1)
                        var = re.sub(r'\[.*?\]', '', var.strip())
                        val = val.strip()
                        consequences.append(URWConsequence(
                            ConsequenceType.BOOLEAN, var, val
                        ))
                    except:
                        pass
                        
                elif '(' in line and ')' in line:
                    ignore_functions = [
                        'renpy.pause', 'renpy.sound', 'renpy.music', 'renpy.with_statement',
                        'renpy.scene', 'renpy.show', 'renpy.hide', 'renpy.say',
                        'renpy.call_screen', 'renpy.transition', 'renpy.end_replay'
                    ]
                    
                    should_ignore = False
                    for ignore_func in ignore_functions:
                        if ignore_func in line:
                            should_ignore = True
                            break
                    
                    if not should_ignore:
                        consequences.append(URWConsequence(
                            ConsequenceType.FUNCTION, 'Function call', line[:30], line
                        ))
                
                elif len(line) > 3 and not line.startswith('#') and not line.strip().startswith('renpy.'):
                    consequences.append(URWConsequence(
                        ConsequenceType.CODE, 'Python code', line[:30], line
                    ))
                        
            return consequences
            
        def _analyze_conditional(self, stmt, depth):
            consequences = []
            
            if not hasattr(stmt, 'entries'):
                return consequences
                
            branch_info = []
            all_sub_consequences = []
            branch_consequences = {}
            
            num_entries = len(stmt.entries) if hasattr(stmt.entries, '__len__') else 0
            
            for idx, (condition, block) in enumerate(stmt.entries):
                is_last = (idx == num_entries - 1)
                
                if condition is not None:
                    cond_str = str(condition).strip()
                    if cond_str.startswith('store.'):
                        cond_str = cond_str[6:]
                    
                    if 'config.developer' in cond_str:
                        cond_str = cond_str.replace('config.developer', 'developer_mode')
                    if '_in_replay' in cond_str:
                        cond_str = cond_str.replace('_in_replay', 'in_replay')
                    
                    try:
                        if cond_str.lower() in ('true', '1'):
                            is_else_branch = True
                        else:
                            is_else_branch = False
                    except:
                        is_else_branch = False
                    
                    if is_else_branch and is_last:
                        branch_label = "else"
                        branch_key = "else"
                    else:
                        full_cond_str = cond_str
                        if len(cond_str) > 35:
                            cond_str = cond_str[:32] + "..."
                            
                        if idx == 0:
                            branch_label = "if {0}".format(cond_str)
                            branch_key = "if {0}".format(full_cond_str)
                        else:
                            branch_label = "elif {0}".format(cond_str)
                            branch_key = "elif {0}".format(full_cond_str)
                else:
                    branch_label = "else"
                    branch_key = "else"
                    
                branch_info.append(branch_label)
                    
                if block and depth < self._max_depth:
                    sub_cons = self.analyze_block(block, depth + 1)
                    all_sub_consequences.extend(sub_cons)
                    branch_consequences[branch_key] = sub_cons
                else:
                    branch_consequences[branch_key] = []
                    
            if branch_info:
                if len(branch_info) == 1:
                    cond_text = branch_info[0]
                elif len(branch_info) == 2 and branch_info[1] == "else":
                    cond_text = "{0}/else".format(branch_info[0])
                else:
                    cond_text = "{0} (+{1})".format(branch_info[0], len(branch_info)-1)
                    
                consequences.append(URWConsequence(
                    ConsequenceType.CONDITION, cond_text, str(len(all_sub_consequences)),
                    source_line=getattr(stmt, 'linenumber', 0),
                    sub_consequences=all_sub_consequences,
                    branch_consequences=branch_consequences
                ))
                
            important_types = [ConsequenceType.INCREASE, ConsequenceType.DECREASE,
                            ConsequenceType.JUMP, ConsequenceType.CALL]
            for sub in all_sub_consequences:
                if sub.type in important_types:
                    consequences.append(sub)
                    
            return consequences
            
        def _analyze_while(self, stmt, depth):
            consequences = []
            
            if hasattr(stmt, 'condition'):
                cond_str = str(stmt.condition)[:30]
                consequences.append(URWConsequence(
                    ConsequenceType.CONDITION, "while {0}".format(cond_str), ""
                ))
                
            if hasattr(stmt, 'block') and depth < self._max_depth:
                consequences.extend(self.analyze_block(stmt.block, depth + 1))
                
            return consequences
    
    urw_analyzer = URWAnalyzer()
    
    ##################################################################
    #                URW MENU FINDER                                 #
    ##################################################################
    
    class URWMenuFinder(object):
        """Menu detection using multiple strategies"""
        
        def __init__(self):
            self._strategy_scores = {}
            self._seen_menus_by_label = {}
            self._last_label = None
            self._menu_index_in_label = 0
            self._global_menu_history = []
            self._global_menu_index = 0
            
        def reset_sequence(self, label=None):
            if label:
                self._seen_menus_by_label[label] = []
            else:
                self._seen_menus_by_label = {}
            self._menu_index_in_label = 0
            self._global_menu_history = []
            self._global_menu_index = 0
            
        def find_menu_node(self, items):
            urw_log.debug("Finding menu with {0} items".format(len(items)), "MENU_FINDER")
            
            context = self._get_execution_context()
            if not context:
                urw_log.warn("No execution context available", "MENU_FINDER")
                return None, None
            
            current_label = context.get('label')
            if current_label != self._last_label:
                self._last_label = current_label
                self._menu_index_in_label = 0
                urw_log.debug("Label changed to: {0}".format(current_label), "MENU_FINDER")
                
            cache_key = self._create_cache_key(items, context)
            
            cached = urw_menu_cache.get(cache_key)
            if cached:
                urw_log.debug("Menu found in cache (index {0})".format(self._menu_index_in_label), "MENU_FINDER")
                self._menu_index_in_label += 1
                return cached
                
            result = self._find_via_execution_stack(items, context)
            if result[0]:
                self._record_seen_menu(result[0], context)
                urw_menu_cache.set(cache_key, result)
                return result
                
            result = self._find_via_sequence(items, context)
            if result[0]:
                self._record_seen_menu(result[0], context)
                urw_menu_cache.set(cache_key, result)
                return result
                
            result = self._find_via_proximity(items, context)
            if result[0]:
                self._record_seen_menu(result[0], context)
                urw_menu_cache.set(cache_key, result)
                return result
                
            result = self._find_via_text_match(items, context)
            if result[0]:
                self._record_seen_menu(result[0], context)
                urw_menu_cache.set(cache_key, result)
                return result
                
            urw_log.warn("Could not find matching menu node", "MENU_FINDER")
            self._menu_index_in_label += 1
            return None, None
        
        def _record_seen_menu(self, menu_node, context):
            label = context.get('label', '__global__')
            if label not in self._seen_menus_by_label:
                self._seen_menus_by_label[label] = []
            if hasattr(menu_node, 'linenumber'):
                self._seen_menus_by_label[label].append(menu_node.linenumber)
                self._global_menu_history.append(menu_node.linenumber)
            self._menu_index_in_label += 1
            self._global_menu_index += 1
            
        def _get_caption_signature(self, items):
            captions = []
            for item in items:
                if hasattr(item, 'caption'):
                    text = str(item.caption)
                elif isinstance(item, (list, tuple)) and len(item) > 0:
                    text = str(item[0])
                else:
                    text = str(item)
                clean = re.sub(r'\{[^}]*\}', '', text).strip().lower()
                captions.append(clean)
            return "|".join(sorted(captions))
            
        def _find_via_sequence(self, items, context):
            try:
                script = renpy.game.script
                
                caption_sig = self._get_caption_signature(items)
                
                matching_menus = []
                
                for node_name, node in script.namemap.items():
                    if not isinstance(node, renpy.ast.Menu):
                        continue
                    if not hasattr(node, 'items') or not hasattr(node, 'linenumber'):
                        continue
                    
                    if self._items_match(node.items, items):
                        matching_menus.append(node)
                
                if not matching_menus:
                    return None, None
                
                matching_menus.sort(key=lambda n: (n.filename or '', n.linenumber))
                
                urw_log.debug("Found {0} menus matching '{1}...'".format(len(matching_menus), caption_sig[:30]), "MENU_FINDER")
                
                if len(matching_menus) == 1:
                    return matching_menus[0], {'strategy': 'sequence_single', 'offset': 0}
                
                seen_lines = set(self._global_menu_history)
                
                for menu in matching_menus:
                    if menu.linenumber not in seen_lines:
                        urw_log.debug("Sequence match: line {0} (unseen, global idx {1})".format(menu.linenumber, self._global_menu_index), "MENU_FINDER")
                        return menu, {'strategy': 'sequence_global', 'offset': 0}
                
                idx = self._global_menu_index % len(matching_menus)
                menu = matching_menus[idx]
                urw_log.debug("Sequence match: line {0} (by global index {1} -> {2})".format(menu.linenumber, self._global_menu_index, idx), "MENU_FINDER")
                return menu, {'strategy': 'sequence_index', 'offset': 0}
                
            except Exception as e:
                urw_log.error("Error in sequence search: {0}".format(e), "MENU_FINDER")
                return None, None
            
        def _get_execution_context(self):
            try:
                ctx = renpy.game.context()
                if not ctx:
                    return None
                
                context = {
                    'filename': None,
                    'linenumber': 0,
                    'label': None,
                    'call_stack': [],
                    'menu_node': None
                }
                
                script = renpy.game.script
                
                def get_node_location(node_name):
                    try:
                        if node_name is None:
                            return None, 0
                        node = script.lookup(node_name)
                        if node and hasattr(node, 'filename') and hasattr(node, 'linenumber'):
                            return node.filename, node.linenumber
                    except Exception:
                        pass
                    return None, 0
                
                if hasattr(ctx, 'current') and ctx.current:
                    node_name = ctx.current
                    try:
                        node = script.lookup(node_name)
                        if node:
                            if hasattr(node, 'filename') and hasattr(node, 'linenumber'):
                                context['filename'] = node.filename
                                context['linenumber'] = node.linenumber
                            if isinstance(node, renpy.ast.Menu):
                                context['menu_node'] = node
                    except Exception as e:
                        urw_log.debug("Could not lookup current node: {0}".format(e), "MENU_FINDER")
                
                if not context['filename'] and hasattr(ctx, 'call_location_stack'):
                    stack = ctx.call_location_stack
                    if isinstance(stack, (list, tuple)) and stack:
                        for node_name in reversed(list(stack)):
                            filename, linenumber = get_node_location(node_name)
                            if filename:
                                context['filename'] = filename
                                context['linenumber'] = linenumber
                                break
                
                if not context['filename'] and hasattr(ctx, 'return_stack'):
                    stack = ctx.return_stack
                    if isinstance(stack, (list, tuple)) and stack:
                        for node_name in reversed(list(stack)):
                            filename, linenumber = get_node_location(node_name)
                            if filename:
                                context['filename'] = filename
                                context['linenumber'] = linenumber
                                break
                
                if context['filename']:
                    context['filename'] = context['filename'].replace('.rpyc', '.rpy')
                
                if context['filename'] and hasattr(renpy.game, 'script'):
                    script = renpy.game.script
                    best_label = None
                    best_line = -1
                    
                    for node_name, node in script.namemap.items():
                        if (isinstance(node, renpy.ast.Label) and
                            hasattr(node, 'filename') and hasattr(node, 'linenumber') and
                            node.filename == context['filename'] and
                            node.linenumber <= context['linenumber'] and
                            node.linenumber > best_line):
                            best_label = node.name
                            best_line = node.linenumber
                            
                    context['label'] = best_label
                    
                if hasattr(ctx, 'return_stack'):
                    stack = ctx.return_stack
                    if isinstance(stack, (list, tuple)):
                        context['call_stack'] = list(stack[-5:])
                    
                return context
                
            except Exception as e:
                urw_log.error("Error getting execution context: {0}".format(e), "MENU_FINDER")
                return None
                
        def _create_cache_key(self, items, context):
            item_texts = []
            for item in items:
                if hasattr(item, 'caption'):
                    item_texts.append(str(item.caption))
                elif isinstance(item, (list, tuple)) and len(item) > 0:
                    item_texts.append(str(item[0]))
                else:
                    item_texts.append(str(item))
            
            return (
                context.get('filename', ''),
                self._global_menu_index,
                tuple(item_texts)
            )
            
        def _find_via_execution_stack(self, items, context):
            try:
                if context.get('menu_node'):
                    return context['menu_node'], {'strategy': 'context_node', 'offset': 0}
                
                ctx = renpy.game.context()
                script = renpy.game.script
                
                if hasattr(ctx, 'current') and ctx.current:
                    try:
                        node = script.lookup(ctx.current)
                        if isinstance(node, renpy.ast.Menu):
                            return node, {'strategy': 'execution_stack', 'offset': 0}
                    except Exception:
                        pass
                
                if hasattr(renpy.game, 'script'):
                    for node_name, node in script.namemap.items():
                        if isinstance(node, renpy.ast.Menu) and hasattr(node, 'items'):
                            if self._items_match(node.items, items):
                                return node, {'strategy': 'item_match', 'offset': 0}
                        
                return None, None
            except:
                return None, None
        
        def _items_match(self, ast_items, runtime_items):
            runtime_captions = []
            for item in runtime_items:
                if hasattr(item, 'caption'):
                    caption = str(item.caption)
                elif isinstance(item, (list, tuple)) and len(item) > 0:
                    caption = str(item[0])
                else:
                    caption = str(item)
                clean = re.sub(r'\{[^}]*\}', '', caption).strip()
                runtime_captions.append(clean)
            
            ast_captions = []
            for item in ast_items:
                if item and len(item) >= 1:
                    caption = str(item[0]) if item[0] else ""
                    clean = re.sub(r'\{[^}]*\}', '', caption).strip()
                    ast_captions.append(clean)
            
            matches = 0
            for rc in runtime_captions:
                if rc in ast_captions:
                    matches += 1
            
            return matches >= len(runtime_captions) * 0.8
                
        def _find_via_proximity(self, items, context):
            try:
                script = renpy.game.script
                filename = context['filename']
                linenumber = context['linenumber']
                
                filename_base = filename.replace('.rpyc', '.rpy') if filename else ''
                
                candidates = []
                
                for node_name, node in script.namemap.items():
                    if not isinstance(node, renpy.ast.Menu):
                        continue
                    if not hasattr(node, 'filename') or not hasattr(node, 'items'):
                        continue
                        
                    node_file = node.filename.replace('.rpyc', '.rpy') if node.filename else ''
                    
                    if node_file != filename_base and not node_file.endswith(filename_base.split('/')[-1]):
                        continue
                        
                    score, info = self._calculate_match_score(node, items, linenumber)
                    if score > 0:
                        candidates.append((node, score, info))
                        
                if not candidates:
                    return None, None
                    
                candidates.sort(key=lambda x: -x[1])
                
                best_node, best_score, best_info = candidates[0]
                urw_log.debug("Found menu at line {0} (score: {1})".format(best_node.linenumber, best_score), "MENU_FINDER")
                
                return best_node, best_info
                
            except Exception as e:
                urw_log.error("Error in proximity search: {0}".format(e), "MENU_FINDER")
                return None, None
                
        def _find_via_text_match(self, items, context):
            try:
                script = renpy.game.script
                item_texts = []
                for item in items:
                    if hasattr(item, 'caption'):
                        text = str(item.caption)
                    elif isinstance(item, (list, tuple)) and len(item) > 0:
                        text = str(item[0])
                    else:
                        text = str(item)
                    item_texts.append(re.sub(r'\{[^}]*\}', '', text).strip())
                
                best_match = None
                best_score = 0
                best_info = None
                
                for node_name, node in script.namemap.items():
                    if not isinstance(node, renpy.ast.Menu) or not hasattr(node, 'items'):
                        continue
                        
                    score, info = self._text_match_score(node, item_texts)
                    if score > best_score:
                        best_score = score
                        best_match = node
                        best_info = info
                        
                if best_match and best_score >= len(items) * 8:
                    return best_match, best_info
                    
                return None, None
                
            except Exception as e:
                urw_log.error("Error in text match search: {0}".format(e), "MENU_FINDER")
                return None, None
                
        def _calculate_match_score(self, node, items, target_line):
            score = 0
            info = {'strategy': 'proximity', 'offset': 0}
            
            node_items = node.items
            distance = abs(node.linenumber - target_line)
            
            text_matches = self._count_text_matches(node_items, items)
            text_match_ratio = text_matches / max(len(items), 1)
            
            if text_match_ratio >= 1.0:
                score += 200
                info['strategy'] = 'text_match'
            elif text_match_ratio >= 0.8:
                score += 150
                info['strategy'] = 'text_match'
            elif text_match_ratio >= 0.5:
                score += 100
            else:
                score += int(text_match_ratio * 50)
            
            if distance <= 5:
                score += 50
            elif distance <= 20:
                score += 40
            elif distance <= 50:
                score += 30
            elif distance <= 100:
                score += 20
            elif distance <= 500:
                score += 10
            else:
                score += 5
                
            if len(node_items) == len(items):
                score += 30
                if info['strategy'] == 'proximity':
                    info['strategy'] = 'exact'
            elif len(node_items) == len(items) + 1:
                score += 15
                if info['strategy'] == 'proximity':
                    info['strategy'] = 'skip_first'
                    info['offset'] = 1
            elif len(node_items) + 1 == len(items):
                score += 10
                if info['strategy'] == 'proximity':
                    info['strategy'] = 'partial'
            
            return score, info
        
        def _count_text_matches(self, node_items, runtime_items):
            node_texts = set()
            for item in node_items:
                if item and len(item) > 0:
                    text = str(item[0]) if item[0] else ""
                    clean = re.sub(r'\{[^}]*\}', '', text).strip().lower()
                    if clean:
                        node_texts.add(clean)
            
            matches = 0
            for item in runtime_items:
                if hasattr(item, 'caption'):
                    text = str(item.caption)
                elif isinstance(item, (list, tuple)) and len(item) > 0:
                    text = str(item[0])
                else:
                    text = str(item)
                clean = re.sub(r'\{[^}]*\}', '', text).strip().lower()
                if clean in node_texts:
                    matches += 1
            
            return matches
            
        def _text_match_score(self, node, item_texts):
            score = 0
            info = {'strategy': 'text_match', 'offset': 0}
            
            node_texts = []
            for item in node.items:
                if item and len(item) > 0:
                    text = str(item[0]) if item[0] else ""
                    clean = re.sub(r'\{[^}]*\}', '', text).strip()
                    node_texts.append(clean)
                    
            for offset in range(min(2, len(node_texts))):
                aligned_score = 0
                for i, item_text in enumerate(item_texts):
                    node_idx = i + offset
                    if node_idx < len(node_texts):
                        if node_texts[node_idx] == item_text:
                            aligned_score += 10
                        elif node_texts[node_idx].lower() == item_text.lower():
                            aligned_score += 8
                        elif item_text in node_texts[node_idx] or node_texts[node_idx] in item_text:
                            aligned_score += 4
                            
                if aligned_score > score:
                    score = aligned_score
                    info['offset'] = offset
                    
            return score, info
    
    urw_menu_finder = URWMenuFinder()
    
    ##################################################################
    #            URW CONSEQUENCE PROCESSOR                           #
    ##################################################################
    
    class URWProcessor(object):
        """Process and filter consequences for display"""
        
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
            self._runtime_captions = []
            for item in items:
                try:
                    if self._is_ast_node_static(item):
                        self._runtime_captions.append("Choice {0}".format(len(self._runtime_captions) + 1))
                        continue
                    
                    if hasattr(item, 'caption'):
                        raw_caption = item.caption
                        if self._is_ast_node_static(raw_caption):
                            caption = "Choice {0}".format(len(self._runtime_captions) + 1)
                        else:
                            caption = str(raw_caption)
                    elif isinstance(item, (list, tuple)) and len(item) > 0:
                        raw_caption = item[0]
                        if self._is_ast_node_static(raw_caption):
                            caption = "Choice {0}".format(len(self._runtime_captions) + 1)
                        else:
                            caption = str(raw_caption)
                    else:
                        caption = str(item) if item is not None else ""
                    
                    clean = re.sub(r'\{[^}]*\}', '', caption).strip()
                    self._runtime_captions.append(clean)
                except Exception as e:
                    urw_log.warn("Error extracting caption: {0}".format(e), "PROCESSOR")
                    self._runtime_captions.append("Choice {0}".format(len(self._runtime_captions) + 1))
            
        def process_choice(self, menu_node, choice_index, info):
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
                                if self._is_ast_node_static(raw_caption):
                                    continue
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
                        urw_log.warn("Choice index {0} out of range (AST has {1} items)".format(actual_index, len(ast_items)), "PROCESSOR")
                        return consequences
                
                if menu_item is None:
                    urw_log.warn("Could not find AST item for choice {0}".format(choice_index), "PROCESSOR")
                    return consequences
                
                if len(menu_item) >= 3 and menu_item[2]:
                    choice_block = menu_item[2]
                    consequences = urw_analyzer.analyze_block(choice_block)
                    
                consequences = self._filter_consequences(consequences)
                consequences = self._deduplicate(consequences)
                consequences.sort(key=lambda c: -c.get_priority())
                
                urw_consequence_cache.set(cache_key, consequences)
                
            except Exception as e:
                urw_log.error("Error processing choice {0}: {1}".format(choice_index, e), "PROCESSOR")
                
            return consequences
            
        def _filter_consequences(self, consequences):
            filtered = []
            
            filters = persistent.urw_filters
            name_filters = persistent.urw_name_filters
            
            for cons in consequences:
                if not self._passes_type_filter(cons, filters):
                    continue
                    
                if not self._passes_name_filter(cons, name_filters):
                    continue
                    
                filtered.append(cons)
                
            return filtered
            
        def _passes_type_filter(self, cons, filters):
            ctype = cons.type
            
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
            var_name = str(cons.variable).lower()
            
            custom_show = name_filters.get('custom_show', [])
            for pattern in custom_show:
                if pattern.lower() in var_name:
                    return True
                    
            custom_hide = name_filters.get('custom_hide', [])
            for pattern in custom_hide:
                if var_name.startswith(pattern.lower()):
                    return False
                    
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
            seen = set()
            unique = []
            
            for cons in consequences:
                key = (cons.type, cons.variable, cons.value)
                if key not in seen:
                    seen.add(key)
                    unique.append(cons)
                    
            return unique
            
        def categorize_variable(self, var_name):
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
    
    class URWFormatter(object):
        """Format consequences for display"""
        
        THEMES = {
            'modern': {
                'increase': '#4CAF50',
                'decrease': '#F44336',
                'assign': '#2196F3',
                'boolean': '#00BCD4',
                'jump': '#FF9800',
                'call': '#8BC34A',
                'return': '#E91E63',
                'condition': '#FFEB3B',
                'function': '#9C27B0',
                'code': '#9E9E9E',
                'relationship': '#FF4081',
                'stat': '#FFD600',
                'flag': '#00E676',
                'unknown': '#757575',
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
            theme_name = persistent.urw_theme
            return self.THEMES.get(theme_name, self.THEMES['modern'])
            
        def format_consequences(self, consequences, max_display=None, show_all=None):
            if not consequences:
                return ""
                
            if max_display is None:
                max_display = persistent.urw_max_consequences
            if show_all is None:
                show_all = persistent.urw_show_all
                
            theme = self.get_theme()
            
            display_consequences = consequences if show_all else consequences[:max_display]
            
            formatted_parts = []
            
            for cons in display_consequences:
                formatted = self._format_single(cons, theme)
                if formatted:
                    formatted_parts.append(formatted)
                    
            result = " | ".join(formatted_parts)
            
            if not show_all and len(consequences) > max_display:
                remaining = len(consequences) - max_display
                more_color = theme.get('more', '#888')
                result += " | {{color={0}}}+{1} more{{/color}}".format(more_color, remaining)
                
            return result
            
        def _format_single(self, cons, theme, full_text=None):
            if full_text is None:
                full_text = persistent.urw_full_text
                
            ctype = cons.type
            color = theme.get(ctype, theme.get('unknown', '#888'))
            
            meta = ConsequenceType.get_metadata(ctype)
            icon = meta['icon']
            
            var = self._escape_renpy(str(cons.variable))
            val = self._escape_renpy(str(cons.value)) if cons.value else ""
            
            val_limit = 50 if full_text else 12
            cond_limit = 80 if full_text else 25
            func_limit = 60 if full_text else 20
            compact_limit = 80 if full_text else 30
            
            if ctype == ConsequenceType.INCREASE:
                if val and val != '1':
                    text = "{0}{1} (+{2})".format(icon, var, val)
                else:
                    text = "{0}{1}".format(icon, var)
                    
            elif ctype == ConsequenceType.DECREASE:
                if val and val != '1':
                    text = "{0}{1} (-{2})".format(icon, var, val)
                else:
                    text = "{0}{1}".format(icon, var)
                    
            elif ctype in [ConsequenceType.ASSIGN, ConsequenceType.BOOLEAN]:
                if len(val) > val_limit:
                    val = val[:val_limit-2] + ".."
                text = "{0}={1}".format(var, val)
                
            elif ctype == ConsequenceType.JUMP:
                text = "{0} {1}".format(icon, var)
                
            elif ctype == ConsequenceType.CALL:
                text = "{0} {1}".format(icon, var)
                
            elif ctype == ConsequenceType.RETURN:
                text = "{0}".format(icon)
                
            elif ctype == ConsequenceType.CONDITION:
                cond = var[:cond_limit-2] + ".." if len(var) > cond_limit else var
                text = "{0} {1}".format(icon, cond)
                
            elif ctype == ConsequenceType.FUNCTION:
                func = var[:func_limit-2] + ".." if len(var) > func_limit else var
                text = "{0} {1}".format(icon, func)
                
            else:
                compact = cons.format("compact")
                text = compact[:compact_limit-2] + ".." if len(compact) > compact_limit else compact
                
            return "{{color={0}}}{1}{{/color}}".format(color, text)
            
        def _escape_renpy(self, text):
            text = text.replace('{', '{{').replace('}', '}}')
            text = text.replace('[', '[[').replace(']', ']]')
            return text
            
        def format_for_urw_tag(self, consequences, prefix="WT: "):
            if not consequences:
                return ""
                
            raw_text = self.format_consequences(consequences)
            raw_text = re.sub(r'\{color=[^}]+\}|\{/color\}', '', raw_text)
            
            return raw_text
    
    urw_formatter = URWFormatter()
    
    ##################################################################
    #                URW TEXT DISPLAYABLE (FIXED)                    #
    ##################################################################
    
    class URWTextDisplayable(renpy.Displayable):
        """Custom displayable for walkthrough text with smart coloring"""
        
        def __init__(self, text, size=None, base_color="#888", prefix="WT: ", **kwargs):
            super(URWTextDisplayable, self).__init__(**kwargs)
            self.text = text
            # CRITICAL FIX: Use persistent.urw_text_size as default, not hardcoded 25
            self.size = size or persistent.urw_text_size
            self.base_color = base_color
            self.prefix = prefix
            
            colored_text = self._create_colored_text()
            self.child = renpy.text.text.Text(
                colored_text,
                outlines=[(2, "#000", 0, 0)],
                font="DejaVuSans.ttf",
                **kwargs
            )
            
        def _create_colored_text(self):
            theme = urw_formatter.get_theme()
            
            result = "{{size={0}}}{{color={1}}}{2}{{/color}}".format(self.size, self.base_color, self.prefix)
            
            parts = self.text.split(' | ')
            
            for i, part in enumerate(parts):
                if i > 0:
                    result += " | "
                    
                color = self._get_color_for_part(part, theme)
                result += "{{color={0}}}{1}{{/color}}".format(color, part)
                
            result += "{/size}"
            return result
            
        def _get_color_for_part(self, part, theme):
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
    #                URW TEXT TAG HANDLER (FIXED)                    #
    ##################################################################
    
    def urw_tag_handler(tag, argument, contents):
        """
        Custom text tag handler for URW
        Usage: {urw=size:25,color:#888,prefix:WT: }consequences{/urw}
        """
        new_list = []
        
        # CRITICAL FIX: Use persistent.urw_text_size as default, not hardcoded 25
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
        
        for i in range(16):
            variant = ""
            for j, char in enumerate(base_tag):
                if (i >> j) & 1:
                    variant += char.upper()
                else:
                    variant += char.lower()
            config.custom_text_tags[variant] = urw_tag_handler
            registered.append(variant)
            
        urw_log.debug("Registered {0} tag variants for urw".format(len(registered)), "INIT")
        return registered
    
    _urw_tag_variants = register_urw_tag()
    
    ##################################################################
    #                URW MENU WRAPPER (FIXED VERSION)                #
    ##################################################################

    class URWMenuWrapper(object):
        """Wraps the menu function to inject walkthrough hints - FIXED VERSION"""
        
        def __init__(self):
            self._original_menu = None
            self._call_count = 0
            self._last_menu_node = None
            self._last_match_info = None
            self._processing_menu = False
            
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
        
        def _wrapped_menu(self, items, set_expr=None, args=None, kwargs=None, item_arguments=None, **extra_kwargs):
            """Wrapped menu function - FIXED VERSION with widget stack protection"""
            if self._processing_menu:
                return self._original_menu(items, set_expr, args, kwargs, item_arguments)
            
            self._call_count += 1
            self._processing_menu = True
            
            try:
                if not persistent.urw_enabled:
                    result = self._original_menu(items, set_expr, args, kwargs, item_arguments)
                    self._processing_menu = False
                    return result
                    
                if items is None:
                    result = self._original_menu(items, set_expr, args, kwargs, item_arguments)
                    self._processing_menu = False
                    return result
                
                try:
                    if not isinstance(items, (list, tuple)):
                        items = list(items)
                except:
                    result = self._original_menu(items, set_expr, args, kwargs, item_arguments)
                    self._processing_menu = False
                    return result
                
                if len(items) == 0:
                    result = self._original_menu(items, set_expr, args, kwargs, item_arguments)
                    self._processing_menu = False
                    return result
                
                urw_log.debug("Processing menu #{0} with {1} items".format(self._call_count, len(items)), "MENU")
                
                self._force_clean_widget_state()
                
                urw_processor.set_runtime_captions(items)
                
                menu_node, match_info = urw_menu_finder.find_menu_node(items)
                
                if menu_node is None:
                    urw_log.warn("Could not find menu node", "MENU")
                    result = self._original_menu(items, set_expr, args, kwargs, item_arguments)
                    self._processing_menu = False
                    return result
                
                self._last_menu_node = menu_node
                self._last_match_info = match_info
                
                if persistent.urw_stats:
                    persistent.urw_stats['menus_analyzed'] = persistent.urw_stats.get('menus_analyzed', 0) + 1
                
                choice_consequences = []
                for i in range(len(items)):
                    cons = urw_processor.process_choice(menu_node, i, match_info)
                    choice_consequences.append(cons)
                
                enhanced_items = self._create_enhanced_items(items, choice_consequences)
                
                self._force_clean_widget_state()
                
                result = self._original_menu(enhanced_items, set_expr, args, kwargs, item_arguments)
                
                if result is not None and result < len(choice_consequences):
                    cons = choice_consequences[result]
                    if cons and persistent.urw_stats:
                        persistent.urw_stats['choices_made'] = persistent.urw_stats.get('choices_made', 0) + 1
                        persistent.urw_stats['consequences_shown'] = persistent.urw_stats.get('consequences_shown', 0) + len(cons)
                
                self._processing_menu = False
                return result
                
            except Exception as e:
                urw_log.error("Error in wrapped menu: {0}".format(e), "MENU")
                self._processing_menu = False
                self._force_clean_widget_state()
                return self._original_menu(items, set_expr, args, kwargs, item_arguments)
        
        def _force_clean_widget_state(self):
            """Force clean widget state to prevent stack issues"""
            try:
                if hasattr(renpy, 'ui') and hasattr(renpy.ui, 'reset'):
                    renpy.ui.reset()
                    urw_log.debug("Widget state reset via renpy.ui.reset()", "MENU")
                
                if hasattr(renpy, 'game') and renpy.game.context():
                    context = renpy.game.context()
                    if hasattr(context, 'scene_lists'):
                        pass
                
                try:
                    renpy.hide_screen("_not_a_real_screen_just_a_cleanup_attempt")
                except:
                    pass
                    
            except Exception as e:
                urw_log.debug("Widget cleanup error (non-critical): {0}".format(e), "MENU")
        
        def _create_enhanced_items(self, items, consequences):
            """Create enhanced menu items with consequence hints"""
            enhanced_items = []
            
            for i, item in enumerate(items):
                try:
                    if isinstance(item, (list, tuple)):
                        if len(item) >= 1:
                            caption = item[0]
                            rest = item[1:] if len(item) > 1 else ()
                            
                            if self._is_ast_node(caption):
                                urw_log.warn("Caption is AST node, using original item", "MENU")
                                enhanced_items.append(item)
                                continue
                            
                            cons = consequences[i] if i < len(consequences) else []
                            
                            if cons:
                                formatted = urw_formatter.format_for_urw_tag(cons)
                                if formatted:
                                    # CRITICAL FIX: Use persistent.urw_text_size here
                                    size = persistent.urw_text_size
                                    new_caption = caption + "\n{{urw=size:{0},color:#888,prefix:WT: }}{1}{{/urw}}".format(size, formatted)
                                    
                                    if persistent.urw_stats:
                                        persistent.urw_stats['consequences_shown'] = persistent.urw_stats.get('consequences_shown', 0) + len(cons)
                                    
                                    if rest:
                                        enhanced_items.append((new_caption,) + tuple(rest))
                                    else:
                                        enhanced_items.append(new_caption)
                                else:
                                    enhanced_items.append(item)
                            else:
                                enhanced_items.append(item)
                        else:
                            enhanced_items.append(item)
                            
                    elif hasattr(item, 'caption'):
                        caption = item.caption
                        
                        if self._is_ast_node(caption):
                            urw_log.warn("Object caption is AST node, using original item", "MENU")
                            enhanced_items.append(item)
                            continue
                        
                        cons = consequences[i] if i < len(consequences) else []
                        
                        if cons:
                            formatted = urw_formatter.format_for_urw_tag(cons)
                            if formatted:
                                # CRITICAL FIX: Use persistent.urw_text_size here
                                size = persistent.urw_text_size
                                new_caption = caption + "\n{{urw=size:{0},color:#888,prefix:WT: }}{1}{{/urw}}".format(size, formatted)
                                
                                if persistent.urw_stats:
                                    persistent.urw_stats['consequences_shown'] = persistent.urw_stats.get('consequences_shown', 0) + len(cons)
                                
                                try:
                                    import copy
                                    new_item = copy.copy(item)
                                    new_item.caption = new_caption
                                    enhanced_items.append(new_item)
                                except:
                                    enhanced_items.append(new_caption)
                            else:
                                enhanced_items.append(item)
                        else:
                            enhanced_items.append(item)
                            
                    else:
                        caption = str(item) if item is not None else ""
                        
                        cons = consequences[i] if i < len(consequences) else []
                        
                        if cons:
                            formatted = urw_formatter.format_for_urw_tag(cons)
                            if formatted:
                                # CRITICAL FIX: Use persistent.urw_text_size here
                                size = persistent.urw_text_size
                                new_caption = caption + "\n{{urw=size:{0},color:#888,prefix:WT: }}{1}{{/urw}}".format(size, formatted)
                                
                                if persistent.urw_stats:
                                    persistent.urw_stats['consequences_shown'] = persistent.urw_stats.get('consequences_shown', 0) + len(cons)
                                    
                                enhanced_items.append(new_caption)
                            else:
                                enhanced_items.append(item)
                        else:
                            enhanced_items.append(item)
                            
                except Exception as e:
                    urw_log.error("Error enhancing item {0}: {1}".format(i, e), "MENU")
                    enhanced_items.append(item)
            
            return enhanced_items
        
        def _is_ast_node(self, obj):
            if obj is None:
                return False
            try:
                module = getattr(obj.__class__, '__module__', '')
                if 'ast' in str(module):
                    return True
                class_name = obj.__class__.__name__
                if class_name in ('Menu', 'Say', 'Jump', 'Call', 'Python', 'If', 'Label', 'Scene', 'Show', 'Hide', 'With'):
                    if hasattr(obj, 'linenumber') or hasattr(obj, 'filename'):
                        return True
            except:
                pass
            return False

    urw_menu_wrapper = URWMenuWrapper()
    
    ##################################################################
    #                URW COMPATIBILITY LAYER (FIXED)                 #
    ##################################################################
    
    class URWCompatibility(object):
        """Provides compatibility with URW 1.x persistent settings - FIXED VERSION"""
        
        @staticmethod
        def migrate_settings():
            """Migrate settings from URW 1.x - FIXED to not overwrite current values"""
            urw_log.persistent_debug("=== START MIGRATION ===")
            
            # Log current state before migration
            urw_log.persistent_debug("BEFORE MIGRATION - urw_text_size: {0}".format(
                persistent.urw_text_size if hasattr(persistent, 'urw_text_size') else "NOT SET"))
            
            # Only migrate if the new setting doesn't exist or is None
            # Check urw_text_size FIRST
            if not hasattr(persistent, 'urw_text_size') or persistent.urw_text_size is None:
                if hasattr(persistent, 'universal_wt_text_size'):
                    # Only migrate if the new value is not set
                    old_value = persistent.universal_wt_text_size
                    persistent.urw_text_size = old_value
                    urw_log.info("Migrated: universal_wt_text_size = {0}".format(old_value), "COMPAT")
                else:
                    urw_log.info("No old universal_wt_text_size to migrate", "COMPAT")
            else:
                current_value = persistent.urw_text_size
                urw_log.info("urw_text_size already set to {0}, skipping migration".format(current_value), "COMPAT")
            
            # Only migrate other settings if they don't exist or are None
            if not hasattr(persistent, 'urw_enabled') or persistent.urw_enabled is None:
                if hasattr(persistent, 'universal_walkthrough_enabled'):
                    persistent.urw_enabled = persistent.universal_walkthrough_enabled
                    urw_log.info("Migrated: universal_walkthrough_enabled", "COMPAT")
                    
            if not hasattr(persistent, 'urw_max_consequences') or persistent.urw_max_consequences is None:
                if hasattr(persistent, 'universal_wt_max_consequences'):
                    persistent.urw_max_consequences = persistent.universal_wt_max_consequences
                    urw_log.info("Migrated: universal_wt_max_consequences", "COMPAT")
                    
            if not hasattr(persistent, 'urw_show_all') or persistent.urw_show_all is None:
                if hasattr(persistent, 'universal_wt_show_all_available'):
                    persistent.urw_show_all = persistent.universal_wt_show_all_available
                    urw_log.info("Migrated: universal_wt_show_all_available", "COMPAT")
            
            urw_log.persistent_debug("=== END MIGRATION ===")
            urw_log.persistent_debug("AFTER MIGRATION - urw_text_size: {0}".format(persistent.urw_text_size))
        
        @staticmethod
        def ensure_defaults():
            """Ensure all critical persistent values have valid defaults (handles None cases)"""
            urw_log.persistent_debug("=== START ENSURE DEFAULTS ===")
            
            # FIXED: Only set defaults if value is None or doesn't exist
            defaults_set = []
            
            if not hasattr(persistent, 'urw_text_size') or persistent.urw_text_size is None:
                persistent.urw_text_size = urw_config.DEFAULT_TEXT_SIZE
                defaults_set.append('urw_text_size')
                urw_log.info("Set default urw_text_size to {0}".format(urw_config.DEFAULT_TEXT_SIZE), "COMPAT")
            else:
                urw_log.persistent_debug("urw_text_size already has value: {0}".format(persistent.urw_text_size))
            
            if not hasattr(persistent, 'urw_max_consequences') or persistent.urw_max_consequences is None:
                persistent.urw_max_consequences = urw_config.DEFAULT_MAX_DISPLAY
                defaults_set.append('urw_max_consequences')
            
            if not hasattr(persistent, 'urw_enabled') or persistent.urw_enabled is None:
                persistent.urw_enabled = True
                defaults_set.append('urw_enabled')
            
            if not hasattr(persistent, 'urw_show_all') or persistent.urw_show_all is None:
                persistent.urw_show_all = True
                defaults_set.append('urw_show_all')
            
            if not hasattr(persistent, 'urw_spoiler_mode') or persistent.urw_spoiler_mode is None:
                persistent.urw_spoiler_mode = False
                defaults_set.append('urw_spoiler_mode')
            
            if not hasattr(persistent, 'urw_highlight_best') or persistent.urw_highlight_best is None:
                persistent.urw_highlight_best = True
                defaults_set.append('urw_highlight_best')
            
            if not hasattr(persistent, 'urw_theme') or persistent.urw_theme is None:
                persistent.urw_theme = "modern"
                defaults_set.append('urw_theme')
            
            if not hasattr(persistent, 'urw_full_text') or persistent.urw_full_text is None:
                persistent.urw_full_text = False
                defaults_set.append('urw_full_text')
            
            if not hasattr(persistent, 'urw_hide_dialogue') or persistent.urw_hide_dialogue is None:
                persistent.urw_hide_dialogue = True
                defaults_set.append('urw_hide_dialogue')
            
            if defaults_set:
                urw_log.persistent_debug("Set defaults for: {0}".format(", ".join(defaults_set)))
            
            urw_log.persistent_debug("=== END ENSURE DEFAULTS ===")
    
    # DON'T call compatibility methods here! Wait until after persistent loads
    
    ##################################################################
    #                URW INITIALIZATION (MOVED LATER)                #
    ##################################################################
    
    def urw_init():
        """Initialize URW with minimal logging"""
        urw_log.info("Initializing URW v{0}".format(urw_config.VERSION), "INIT")
        
        # Now run compatibility checks AFTER persistent is loaded
        URWCompatibility.migrate_settings()
        URWCompatibility.ensure_defaults()
        
        # Ensure all defaults are set
        urw_ensure_persistent_defaults()
        
        # Only add startup logs if they haven't been cleared
        if not persistent.urw_logs_cleared:
            urw_log.log("URW Logger initialized", "INIT", "PERSISTENT")
            urw_log.log("Debug mode: {0}".format(urw_config.DEBUG), "DEBUG", "PERSISTENT")
        
        urw_menu_wrapper.install()
        
        if persistent.urw_stats:
            persistent.urw_stats['session_start'] = _time.strftime("%Y-%m-%d %H:%M:%S")
            
        urw_log.info("URW initialization complete", "INIT")
        print("[URW] Universal Ren'Py Walkthrough System v{0} loaded".format(urw_config.VERSION))
    
    def urw_clear_caches():
        """Clear all URW caches"""
        urw_menu_cache.clear()
        urw_consequence_cache.clear()
        urw_node_cache.clear()
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
            if not hasattr(urw_menu_wrapper, '_last_menu_node') or not urw_menu_wrapper._last_menu_node:
                return result
                
            menu_node = urw_menu_wrapper._last_menu_node
            match_info = urw_menu_wrapper._last_match_info or {'offset': 0}
            
            if not hasattr(menu_node, 'items'):
                return result
            
            runtime_captions = urw_processor._runtime_captions if hasattr(urw_processor, '_runtime_captions') else []
            
            def is_ast_node(obj):
                if obj is None:
                    return False
                try:
                    module = getattr(obj.__class__, '__module__', '')
                    return 'ast' in str(module)
                except:
                    return False
            
            if runtime_captions:
                for idx, runtime_caption in enumerate(runtime_captions):
                    try:
                        if is_ast_node(runtime_caption):
                            urw_log.warn("Runtime caption is AST node, skipping: {0}".format(type(runtime_caption).__name__), "VIEWER")
                            result.append({
                                'index': idx,
                                'caption': "Choice {0}".format(idx + 1),
                                'consequences': []
                            })
                            continue
                        
                        menu_item = None
                        for ast_item in menu_node.items:
                            if ast_item and len(ast_item) >= 1:
                                raw_caption = ast_item[0]
                                if is_ast_node(raw_caption):
                                    continue
                                ast_caption = str(raw_caption) if raw_caption else ""
                                ast_caption_clean = re.sub(r'\{[^}]*\}', '', ast_caption).strip()
                                
                                if ast_caption_clean == runtime_caption:
                                    menu_item = ast_item
                                    break
                        
                        consequences = urw_processor.process_choice(menu_node, idx, match_info)
                        
                        result.append({
                            'index': idx,
                            'caption': str(runtime_caption),
                            'consequences': consequences
                        })
                    except Exception as item_error:
                        urw_log.error("Error processing menu item {0}: {1}".format(idx, item_error), "VIEWER")
                        result.append({
                            'index': idx,
                            'caption': str(runtime_caption) if runtime_caption else "Choice {0}".format(idx + 1),
                            'consequences': []
                        })
            else:
                for idx, item in enumerate(menu_node.items):
                    try:
                        if isinstance(item, (list, tuple)) and len(item) > 0:
                            raw_caption = item[0]
                            if is_ast_node(raw_caption):
                                caption = "Choice {0}".format(idx + 1)
                            else:
                                caption = str(raw_caption) if raw_caption else "Choice {0}".format(idx + 1)
                        else:
                            if is_ast_node(item):
                                caption = "Choice {0}".format(idx + 1)
                            else:
                                caption = str(item) if item else "Choice {0}".format(idx + 1)
                        
                        if not isinstance(caption, str) or 'ast.' in caption.lower():
                            caption = "Choice {0}".format(idx + 1)
                        
                        clean_caption = re.sub(r'\{[^}]+\}', '', caption)
                        
                        consequences = urw_processor.process_choice(menu_node, idx, match_info)
                        
                        result.append({
                            'index': idx,
                            'caption': clean_caption,
                            'consequences': consequences
                        })
                    except Exception as item_error:
                        urw_log.error("Error processing menu item {0}: {1}".format(idx, item_error), "VIEWER")
                        result.append({
                            'index': idx,
                            'caption': "Choice {0}".format(idx + 1),
                            'consequences': []
                        })
                
        except Exception as e:
            urw_log.error("Error getting menu consequences: {0}".format(e), "VIEWER")
            
        return result
    
    def urw_copy_debug_info():
        """Copy debug info to clipboard for bug reporting - Ren'Py 7.x.x version"""
        try:
            game_name = config.name if hasattr(config, 'name') and config.name else "Unknown Game"
            game_version = config.version if hasattr(config, 'version') and config.version else "Unknown"
            
            renpy_version = renpy.version_string if hasattr(renpy, 'version_string') else "Unknown"
            
            urw_version = urw_config.VERSION
            
            import platform
            os_info = platform.platform()
            
            def get_node_info(node_name):
                try:
                    if node_name is None:
                        return "None"
                    node = renpy.game.script.lookup(node_name)
                    if node and hasattr(node, 'filename') and hasattr(node, 'linenumber'):
                        return "{0}:{1}".format(node.filename, node.linenumber)
                    return "(node: {0})".format(node_name)
                except Exception:
                    return "(lookup failed: {0})".format(node_name)
            
            context_info = "N/A"
            context_details = []
            try:
                ctx = renpy.game.context()
                if ctx:
                    if hasattr(ctx, 'current') and ctx.current:
                        loc_info = get_node_info(ctx.current)
                        context_details.append("current: {0}".format(loc_info))
                    
                    if hasattr(ctx, 'call_location_stack'):
                        stack = ctx.call_location_stack
                        if isinstance(stack, (list, tuple)) and stack:
                            for i, node_name in enumerate(list(stack)[-3:]):
                                loc_info = get_node_info(node_name)
                                context_details.append("call_stack[{0}]: {1}".format(i, loc_info))
                    
                    if hasattr(ctx, 'return_stack'):
                        stack = ctx.return_stack
                        if isinstance(stack, (list, tuple)) and stack:
                            for i, node_name in enumerate(list(stack)[-3:]):
                                loc_info = get_node_info(node_name)
                                context_details.append("return_stack[{0}]: {1}".format(i, loc_info))
                
                context_info = "\n  ".join(context_details) if context_details else "N/A"
            except Exception as e:
                context_info = "Error: {0}".format(e)
            
            last_captions = "N/A"
            try:
                if hasattr(urw_processor, '_runtime_captions') and urw_processor._runtime_captions:
                    last_captions = "\n  ".join(["- {0}".format(c) for c in urw_processor._runtime_captions[:10]])
            except:
                pass
            
            sequence_info = "N/A"
            try:
                if hasattr(urw_menu_finder, '_global_menu_index'):
                    global_idx = urw_menu_finder._global_menu_index
                    global_history = urw_menu_finder._global_menu_history
                    label_idx = getattr(urw_menu_finder, '_menu_index_in_label', 0)
                    last_label = urw_menu_finder._last_label or "None"
                    recent = global_history[-10:] if len(global_history) > 10 else global_history
                    sequence_info = "Global Index: {0}, Recent Lines: {1}\n  Label: {2}, Label Index: {3}".format(global_idx, recent, last_label, label_idx)
            except:
                pass
            
            logs = urw_log.get_logs(50)
            logs_text = "\n".join(logs) if logs else "No logs available"
            
            report = """=== URW 2.0 Debug Report ===
    Generated: {0}

    [Game Information]
    Game: {1}
    Game Version: {2}
    Ren'Py Version: {3}

    [URW Information]
    URW Version: {4}
    URW Enabled: {5}
    Text Size: {6}
    Max Consequences: {7}

    [System Information]
    OS: {8}

    [Current Context]
      {9}

    [Last Menu Captions]
      {10}

    [Sequence Tracking]
      {11}

    [Debug Logs (Last 50)]
    {12}

    === End of Report ===""".format(
                _time.strftime("%Y-%m-%d %H:%M:%S"),
                game_name,
                game_version,
                renpy_version,
                urw_version,
                persistent.urw_enabled,
                persistent.urw_text_size,
                persistent.urw_max_consequences,
                os_info,
                context_info,
                last_captions,
                sequence_info,
                logs_text
            )

            import os
            filename = "urw_debug_report.txt"
            
            with open(filename, "wb") as f:
                f.write(report.encode('utf-8'))
            
            renpy.notify("Debug info saved to {0}".format(filename))
            urw_log.info("Debug info saved to {0}".format(filename), "DEBUG")
            
        except Exception as e:
            urw_log.error("Failed to save debug info: {0}".format(e), "DEBUG")
            renpy.notify("Failed to save: {0}".format(e))

init 0 python:
    # This runs AFTER persistent values are loaded from disk
    # Initialize URW with the loaded persistent values
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

style URW_slider:
    bar_vertical False
    bar_invert False
    xalign 0.5
    yalign 0.5
    left_bar Frame("#4fc3f7", 5, 5)
    right_bar Frame("#333", 5, 5)
    thumb None

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
    
    key "game_menu" action [Hide("URW_filters", transition=dissolve), Function(urw_force_save)]
    key "K_ESCAPE" action [Hide("URW_filters", transition=dissolve), Function(urw_force_save)]
    
    frame:
        xalign 0.5
        yalign 0.5
        xmaximum 850
        ymaximum 650
        background Frame("#1a1a2e", 20, 20)
        xpadding 35
        ypadding 25
        
        at transform:
            yoffset -60
            alpha 0.0
            ease 0.4 yoffset 0 alpha 1.0
        
        vbox:
            spacing 20
            xalign 0.5
            
            vbox:
                spacing 8
                xalign 0.5
                
                text "{color=#4fc3f7}{size=28}{b}Filter Settings{/b}{/size}{/color}":
                    xalign 0.5
                
                text "{color=#888}{size=14}Customize which consequences are displayed{/size}{/color}":
                    xalign 0.5
                
                add Solid("#4fc3f7", xysize=(300, 2)):
                    xalign 0.5
            
            viewport:
                scrollbars "vertical"
                mousewheel True
                xsize 780
                ysize 450
                
                vbox:
                    spacing 25
                    xsize 760
                    
                    # Type Filters
                    frame:
                        background Frame("#16213e", 12, 12)
                        xfill True
                        padding (20, 15)
                        
                        vbox:
                            spacing 15
                            
                            text "{color=#fff}{size=18}{b}Consequence Types{/b}{/size}{/color}"
                            
                            grid 3 3:
                                spacing 15
                                xalign 0.5
                                
                                # Variables
                                hbox:
                                    spacing 8
                                    textbutton "±":
                                        action [ToggleDict(persistent.urw_filters, 'variables'), Function(urw_force_save)]
                                        xsize 35
                                        ysize 35
                                        text_size 18
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
                                    spacing 8
                                    textbutton "?":
                                        action [ToggleDict(persistent.urw_filters, 'conditions'), Function(urw_force_save)]
                                        xsize 35
                                        ysize 35
                                        text_size 18
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
                                    spacing 8
                                    textbutton "→":
                                        action [ToggleDict(persistent.urw_filters, 'flow'), Function(urw_force_save)]
                                        xsize 35
                                        ysize 35
                                        text_size 18
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
                                    spacing 8
                                    textbutton "f":
                                        action [ToggleDict(persistent.urw_filters, 'functions'), Function(urw_force_save)]
                                        xsize 35
                                        ysize 35
                                        text_size 18
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
                                    spacing 8
                                    textbutton "◆":
                                        action [ToggleDict(persistent.urw_filters, 'flags'), Function(urw_force_save)]
                                        xsize 35
                                        ysize 35
                                        text_size 18
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
                                    spacing 8
                                    textbutton "♥":
                                        action [ToggleDict(persistent.urw_filters, 'relationships'), Function(urw_force_save)]
                                        xsize 35
                                        ysize 35
                                        text_size 18
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
                                    spacing 8
                                    textbutton "★":
                                        action [ToggleDict(persistent.urw_filters, 'stats'), Function(urw_force_save)]
                                        xsize 35
                                        ysize 35
                                        text_size 18
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
                                    spacing 8
                                    textbutton "?":
                                        action [ToggleDict(persistent.urw_filters, 'unknown'), Function(urw_force_save)]
                                        xsize 35
                                        ysize 35
                                        text_size 18
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
                        padding (20, 15)
                        
                        vbox:
                            spacing 15
                            
                            text "{color=#fff}{size=18}{b}Name-based Filters{/b}{/size}{/color}"
                            
                            grid 2 3:
                                spacing 20
                                xalign 0.5
                                
                                # Hide underscore
                                hbox:
                                    spacing 8
                                    textbutton (_("ON") if persistent.urw_name_filters.get('hide_underscore', True) else _("OFF")):
                                        action [ToggleDict(persistent.urw_name_filters, 'hide_underscore'), Function(urw_force_save)]
                                        xsize 55
                                        ysize 30
                                        text_size 12
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
                                    spacing 8
                                    textbutton (_("ON") if persistent.urw_name_filters.get('hide_renpy', True) else _("OFF")):
                                        action [ToggleDict(persistent.urw_name_filters, 'hide_renpy'), Function(urw_force_save)]
                                        xsize 55
                                        ysize 30
                                        text_size 12
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
                                    spacing 8
                                    textbutton (_("ON") if persistent.urw_name_filters.get('hide_config', False) else _("OFF")):
                                        action [ToggleDict(persistent.urw_name_filters, 'hide_config'), Function(urw_force_save)]
                                        xsize 55
                                        ysize 30
                                        text_size 12
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
                                    spacing 8
                                    textbutton (_("ON") if persistent.urw_name_filters.get('hide_store', True) else _("OFF")):
                                        action [ToggleDict(persistent.urw_name_filters, 'hide_store'), Function(urw_force_save)]
                                        xsize 55
                                        ysize 30
                                        text_size 12
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
                                    spacing 8
                                    textbutton (_("ON") if persistent.urw_name_filters.get('hide_internal', True) else _("OFF")):
                                        action [ToggleDict(persistent.urw_name_filters, 'hide_internal'), Function(urw_force_save)]
                                        xsize 55
                                        ysize 30
                                        text_size 12
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
                                
                                null
                    
                    # Quick Presets
                    frame:
                        background Frame("#16213e", 12, 12)
                        xfill True
                        padding (20, 15)
                        
                        vbox:
                            spacing 15
                            
                            text "{color=#fff}{size=18}{b}Quick Presets{/b}{/size}{/color}"
                            
                            hbox:
                                spacing 15
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
                                        Function(urw_force_save)
                                    ]
                                    xsize 120
                                    ysize 40
                                    text_size 14
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
                                        Function(urw_force_save)
                                    ]
                                    xsize 140
                                    ysize 40
                                    text_size 14
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
                                        Function(urw_force_save)
                                    ]
                                    xsize 140
                                    ysize 40
                                    text_size 14
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
                                        Function(urw_force_save)
                                    ]
                                    xsize 100
                                    ysize 40
                                    text_size 14
                                    text_xalign 0.5
                                    background "#607D8B"
                                    hover_background "#90A4AE"
                                    text_color "#fff"
            
            # Footer
            hbox:
                spacing 20
                xalign 0.5
                
                textbutton "← Back":
                    action [Hide("URW_filters", transition=dissolve), Function(urw_force_save)]
                    xsize 100
                    ysize 40
                    text_size 14
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
                        Function(urw_force_save)
                    ]
                    xsize 140
                    ysize 40
                    text_size 14
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
        xmaximum 600
        background Frame("#1a1a2e", 20, 20)
        xpadding 35
        ypadding 30
        
        at URW_fade_in
        
        vbox:
            spacing 20
            xalign 0.5
            
            text "{color=#4fc3f7}{size=28}{b}= URW 2.0 Statistics{/b}{/size}{/color}":
                xalign 0.5
            
            add Solid("#4fc3f7", xysize=(250, 2)):
                xalign 0.5
            
            null height 10
            
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
                padding (20, 15)
                
                vbox:
                    spacing 10
                    
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
                padding (20, 15)
                
                vbox:
                    spacing 10
                    
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
                padding (20, 15)
                
                vbox:
                    spacing 10
                    
                    text "{color=#fff}{size=16}{b}Cache Performance{/b}{/size}{/color}"
                    
                    hbox:
                        text "{color=#888}{size=14}Menu Cache:{/size}{/color}"
                        text "{color=#fff}{size=14} [_menu_cache_size]/[_menu_cache_max] ([_menu_cache_hit] hit rate){/size}{/color}"
                    
                    hbox:
                        text "{color=#888}{size=14}Consequence Cache:{/size}{/color}"
                        text "{color=#fff}{size=14} [_cons_cache_size]/[_cons_cache_max] ([_cons_cache_hit] hit rate){/size}{/color}"
            
            null height 10
            
            hbox:
                spacing 20
                xalign 0.5
                
                textbutton "Clear Caches":
                    action [Function(urw_clear_caches), Function(urw_force_save)]
                    xsize 130
                    ysize 40
                    text_size 14
                    text_xalign 0.5
                    background "#FF5722"
                    hover_background "#FF7043"
                    text_color "#fff"
                
                textbutton "Close":
                    action Hide("URW_stats_screen", transition=dissolve)
                    xsize 100
                    ysize 40
                    text_size 14
                    text_xalign 0.5
                    background "#4fc3f7"
                    hover_background "#5fd3f7"
                    text_color "#000"

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
    
    # FIXED: Save on close
    key "game_menu" action [Hide("URW_preferences", transition=dissolve), Function(urw_force_save)]
    key "K_ESCAPE" action [Hide("URW_preferences", transition=dissolve), Function(urw_force_save)]
    
    frame:
        xalign 0.5
        yalign 0.5
        xmaximum 800
        ymaximum 700
        background Frame("#1a1a2e", 20, 20)
        xpadding 40
        ypadding 30
        
        at transform:
            yoffset -80
            alpha 0.0
            ease 0.4 yoffset 0 alpha 1.0
        
        vbox:
            spacing 20
            xalign 0.5
            
            # Header
            vbox:
                spacing 8
                xalign 0.5
                
                hbox:
                    spacing 15
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
                
                add Solid("#4fc3f7", xysize=(400, 2)) xalign 0.5

            null height 10
            
            viewport:
                scrollbars "vertical"
                mousewheel True
                xsize 720
                ysize 480
                
                vbox:
                    spacing 25
                    xsize 700
                    
                    frame:
                        background Frame("#16213e", 15, 15)
                        xfill True
                        padding (25, 20)
                        
                        at URW_slide_in_left
                        
                        hbox:
                            spacing 30
                            xalign 0.5
                            
                            vbox:
                                spacing 5
                                text "{color=#fff}{size=20}{b}Enable Walkthrough{/b}{/size}{/color}"
                                text "{color=#888}{size=12}Toggle walkthrough hints on/off{/size}{/color}"
                            
                            textbutton (_("ENABLED") if persistent.urw_enabled else _("DISABLED")):
                                action [
                                    ToggleField(persistent, "urw_enabled"),
                                    Function(urw_log_persistent_changes, "Toggle", "urw_enabled", 
                                            not persistent.urw_enabled, persistent.urw_enabled),
                                    Function(urw_force_save)
                                ]
                                xsize 140
                                ysize 45
                                text_size 16
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
                        padding (25, 20)
                        
                        at transform:
                            alpha 0.0
                            xoffset 50
                            pause 0.15
                            ease 0.4 alpha 1.0 xoffset 0
                        
                        vbox:
                            spacing 20
                            
                            text "{color=#4fc3f7}{size=18}{b}■ Display Settings{/b}{/size}{/color}"
                            
                            vbox:
                                spacing 10
                                
                                hbox:
                                    spacing 15
                                    
                                    text "{color=#fff}{size=16}Text Size:{/size}{/color}"
                                    text "{color=#4fc3f7}{size=18}{b}[persistent.urw_text_size]{/b}{/size}{/color}"
                                
                                hbox:
                                    spacing 10
                                    xalign 0.5
                                    
                                    textbutton "−":
                                        action [
                                            If(persistent.urw_text_size > 12, 
                                                SetField(persistent, "urw_text_size", persistent.urw_text_size - 2)), 
                                            Function(urw_log_persistent_changes, "Decrease", "urw_text_size", 
                                                    persistent.urw_text_size, persistent.urw_text_size - 2),
                                            Function(urw_force_save)
                                        ]
                                        style "URW_size_button"
                                        text_size 24
                                        xsize 40
                                        ysize 40
                                        text_xalign 0.5
                                    
                                    bar:
                                        value FieldValue(persistent, "urw_text_size", range=40, style="slider")
                                        style "URW_slider"
                                        xsize 350
                                        ysize 20
                                        left_bar Frame("#4fc3f7", 5, 5)
                                        right_bar Frame("#333", 5, 5)
                                        thumb None
                                    
                                    textbutton "+":
                                        action [
                                            If(persistent.urw_text_size < 40, 
                                                SetField(persistent, "urw_text_size", persistent.urw_text_size + 2)),
                                            Function(urw_log_persistent_changes, "Increase", "urw_text_size", 
                                                    persistent.urw_text_size, persistent.urw_text_size + 2),
                                            Function(urw_force_save)
                                        ]
                                        style "URW_size_button"
                                        text_size 24
                                        xsize 40
                                        ysize 40
                                        text_xalign 0.5
                                
                                hbox:
                                    spacing 8
                                    xalign 0.5
                                    
                                    text "{color=#888}{size=12}Quick:{/size}{/color}":
                                        yalign 0.5
                                    
                                    for size in [14, 18, 22, 25, 30, 35]:
                                        textbutton "[size]":
                                            action [
                                                SetField(persistent, "urw_text_size", size),
                                                Function(urw_log_persistent_changes, "Set", "urw_text_size", 
                                                        persistent.urw_text_size, size),
                                                Function(urw_force_save)
                                            ]
                                            xsize 40
                                            ysize 28
                                            text_size 12
                                            text_xalign 0.5
                                            if persistent.urw_text_size == size:
                                                background Frame("#4fc3f7", 5, 5)
                                                text_color "#000"
                                            else:
                                                background Frame("#333", 5, 5)
                                                text_color "#aaa"
                                            hover_background Frame("#5fd3f7", 5, 5)
                            
                            vbox:
                                spacing 10
                                
                                hbox:
                                    spacing 15
                                    
                                    text "{color=#fff}{size=16}Max Consequences:{/size}{/color}"
                                    text "{color=#4fc3f7}{size=18}{b}[persistent.urw_max_consequences]{/b}{/size}{/color}"
                                
                                hbox:
                                    spacing 10
                                    xalign 0.5
                                    
                                    textbutton "−":
                                        action [
                                            If(persistent.urw_max_consequences > 1, 
                                                SetField(persistent, "urw_max_consequences", persistent.urw_max_consequences - 1)),
                                            Function(urw_log_persistent_changes, "Decrease", "urw_max_consequences", 
                                                    persistent.urw_max_consequences, persistent.urw_max_consequences - 1),
                                            Function(urw_force_save)
                                        ]
                                        style "URW_size_button"
                                        text_size 24
                                        xsize 40
                                        ysize 40
                                        text_xalign 0.5
                                    
                                    bar:
                                        value FieldValue(persistent, "urw_max_consequences", range=10, style="slider")
                                        style "URW_slider"
                                        xsize 250
                                        ysize 20
                                        left_bar Frame("#4fc3f7", 5, 5)
                                        right_bar Frame("#333", 5, 5)
                                        thumb None
                                    
                                    textbutton "+":
                                        action [
                                            If(persistent.urw_max_consequences < 10, 
                                                SetField(persistent, "urw_max_consequences", persistent.urw_max_consequences + 1)),
                                            Function(urw_log_persistent_changes, "Increase", "urw_max_consequences", 
                                                    persistent.urw_max_consequences, persistent.urw_max_consequences + 1),
                                            Function(urw_force_save)
                                        ]
                                        style "URW_size_button"
                                        text_size 24
                                        xsize 40
                                        ysize 40
                                        text_xalign 0.5
                                
                                hbox:
                                    spacing 8
                                    xalign 0.5
                                    
                                    text "{color=#888}{size=12}Quick:{/size}{/color}":
                                        yalign 0.5
                                    
                                    for count in [1, 2, 3, 5, 8, 10]:
                                        textbutton "[count]":
                                            action [
                                                SetField(persistent, "urw_max_consequences", count),
                                                Function(urw_log_persistent_changes, "Set", "urw_max_consequences", 
                                                        persistent.urw_max_consequences, count),
                                                Function(urw_force_save)
                                            ]
                                            xsize 35
                                            ysize 28
                                            text_size 12
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
                                spacing 20
                                xalign 0.5
                                
                                vbox:
                                    spacing 3
                                    text "{color=#fff}{size=16}Show All Consequences:{/size}{/color}"
                                    text "{color=#888}{size=11}When enabled, ignores max limit{/size}{/color}"
                                
                                textbutton (_("ON") if persistent.urw_show_all else _("OFF")):
                                    action [
                                        ToggleField(persistent, "urw_show_all"),
                                        Function(urw_log_persistent_changes, "Toggle", "urw_show_all", 
                                                not persistent.urw_show_all, persistent.urw_show_all),
                                        Function(urw_force_save)
                                    ]
                                    xsize 70
                                    ysize 35
                                    text_size 14
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
                                spacing 20
                                xalign 0.5
                                
                                vbox:
                                    spacing 3
                                    text "{color=#fff}{size=16}Full Text Display:{/size}{/color}"
                                    text "{color=#888}{size=11}Show complete text without truncation{/size}{/color}"
                                
                                textbutton (_("ON") if persistent.urw_full_text else _("OFF")):
                                    action [
                                        ToggleField(persistent, "urw_full_text"),
                                        Function(urw_log_persistent_changes, "Toggle", "urw_full_text", 
                                                not persistent.urw_full_text, persistent.urw_full_text),
                                        Function(urw_force_save)
                                    ]
                                    xsize 70
                                    ysize 35
                                    text_size 14
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
                            
                            text "{color=#4fc3f7}{size=18}{b}◆ Theme{/b}{/size}{/color}"
                            
                            hbox:
                                spacing 15
                                xalign 0.5
                                
                                for theme_name in ["modern", "classic", "minimal", "dark"]:
                                    textbutton theme_name.capitalize():
                                        action [
                                            SetField(persistent, "urw_theme", theme_name),
                                            Function(urw_log_persistent_changes, "Set", "urw_theme", 
                                                    persistent.urw_theme, theme_name),
                                            Function(urw_force_save)
                                        ]
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
                            
                            text "{color=#4fc3f7}{size=18}{b}⚙ Advanced Options{/b}{/size}{/color}":
                                xalign 0.5
                            
                            hbox:
                                spacing 20
                                xalign 0.5
                                
                                textbutton "✚ Filters":
                                    action Show("URW_filters", transition=dissolve)
                                    xsize 130
                                    ysize 45
                                    text_size 14
                                    text_xalign 0.5
                                    background Frame("#2196F3", 8, 8)
                                    hover_background Frame("#42A5F5", 8, 8)
                                    text_color "#fff"
                                
                                textbutton "■ Stats":
                                    action Show("URW_stats_screen", transition=dissolve)
                                    xsize 120
                                    ysize 45
                                    text_size 14
                                    text_xalign 0.5
                                    background Frame("#9C27B0", 8, 8)
                                    hover_background Frame("#AB47BC", 8, 8)
                                    text_color "#fff"
                                
                                textbutton "▼ Full Viewer":
                                    action Show("URW_full_viewer", transition=dissolve)
                                    xsize 150
                                    ysize 45
                                    text_size 14
                                    text_xalign 0.5
                                    background Frame("#00BCD4", 8, 8)
                                    hover_background Frame("#26C6DA", 8, 8)
                                    text_color "#fff"
                                
                                if urw_config.DEVELOPER:
                                    textbutton "! Debug":
                                        action Show("URW_debug", transition=dissolve)
                                        xsize 120
                                        ysize 45
                                        text_size 14
                                        text_xalign 0.5
                                        background Frame("#FF5722", 8, 8)
                                        hover_background Frame("#FF7043", 8, 8)
                                        text_color "#fff"
            
            # Footer
            hbox:
                spacing 20
                xalign 0.5
                
                at transform:
                    alpha 0.0
                    pause 0.6
                    ease 0.4 alpha 1.0
                
                textbutton "Close & Save":
                    action [Hide("URW_preferences", transition=dissolve), Function(urw_force_save)]
                    xsize 150
                    ysize 45
                    text_size 16
                    text_xalign 0.5
                    background Frame("#4CAF50", 8, 8)
                    hover_background Frame("#66BB6A", 8, 8)
                    text_color "#fff"
                
                textbutton "Reset All":
                    action [
                        SetField(persistent, "urw_text_size", urw_config.DEFAULT_TEXT_SIZE),
                        SetField(persistent, "urw_max_consequences", urw_config.DEFAULT_MAX_DISPLAY),
                        SetField(persistent, "urw_show_all", True),
                        SetField(persistent, "urw_full_text", False),
                        SetField(persistent, "urw_theme", "modern"),
                        SetField(persistent, "urw_logs_cleared", False),
                        Function(urw_log_persistent_changes, "Reset", "all_settings", "N/A", "defaults"),
                        Function(urw_force_save)
                    ]
                    xsize 120
                    ysize 45
                    text_size 16
                    text_xalign 0.5
                    background Frame("#f44336", 8, 8)
                    hover_background Frame("#ef5350", 8, 8)
                    text_color "#fff"

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
        background "#1a1a2e"
        xfill True
        padding (15, 10)
        
        vbox:
            spacing 5
            
            text "{color=#4fc3f7}{size=16}{b}Persistent Settings State{/b}{/size}{/color}":
                xalign 0.5
            
            hbox:
                spacing 20
                xalign 0.5
                
                vbox:
                    spacing 3
                    # Use string formatting with escaped values
                    $ filters_str = str(persistent.urw_filters).replace('{', '{{').replace('}', '}}')
                    $ name_filters_str = str(persistent.urw_name_filters).replace('{', '{{').replace('}', '}}')
                    
                    text "{color=#ccc}{size=12}urw_text_size: [persistent.urw_text_size]{/size}{/color}"
                    text "{color=#ccc}{size=12}urw_theme: [persistent.urw_theme]{/size}{/color}"
                    text "{color=#ccc}{size=12}urw_max_consequences: [persistent.urw_max_consequences]{/size}{/color}"
                    text "{color=#ccc}{size=12}urw_show_all: [persistent.urw_show_all]{/size}{/color}"
                    text "{color=#ccc}{size=12}urw_enabled: [persistent.urw_enabled]{/size}{/color}"
                    text "{color=#ccc}{size=12}urw_full_text: [persistent.urw_full_text]{/size}{/color}"
                    text "{color=#ccc}{size=12}urw_logs_cleared: [persistent.urw_logs_cleared]{/size}{/color}"
                
                vbox:
                    spacing 3
                    # Don't display full dictionaries in the debug screen to avoid issues
                    text "{color=#ccc}{size=12}urw_filters: (dict){/size}{/color}"
                    text "{color=#ccc}{size=12}urw_name_filters: (dict){/size}{/color}"
                    text "{color=#ccc}{size=12}urw_stats: (dict){/size}{/color}"
            
            # Log viewer
            frame:
                background "#1a1a2e"
                xfill True
                padding (10, 10)
                
                vbox:
                    spacing 5
                    
                    text "{color=#4fc3f7}{size=14}{b}Debug Logs (Last 100){/b}{/size}{/color}":
                        xalign 0.5
                    
                    viewport:
                        scrollbars "vertical"
                        mousewheel True
                        xsize 950
                        ysize 400
                        
                        vbox:
                            spacing 2
                            
                            python:
                                _logs = urw_log.get_logs(100)
                            
                            for _log_entry in _logs:
                                if "PERSISTENT" in _log_entry:
                                    text "{color=#ff9800}{size=10}[_log_entry]{/size}{/color}"
                                elif "ERROR" in _log_entry:
                                    text "{color=#f44336}{size=10}[_log_entry]{/size}{/color}"
                                elif "WARN" in _log_entry:
                                    text "{color=#ffeb3b}{size=10}[_log_entry]{/size}{/color}"
                                else:
                                    text "{color=#888}{size=10}[_log_entry]{/size}{/color}"
            
            # Debug actions
            hbox:
                spacing 15
                xalign 0.5
                
                textbutton "Clear Logs":
                    action Function(urw_log.clear)
                    xsize 110
                    ysize 35
                    text_size 12
                    text_xalign 0.5
                    background "#f44336"
                    hover_background "#ef5350"
                    text_color "#fff"
                
                textbutton "Reset Logs State":
                    action [
                        SetField(persistent, 'urw_logs_cleared', False),
                        Function(urw_force_save)
                    ]
                    xsize 140
                    ysize 35
                    text_size 12
                    text_xalign 0.5
                    background "#9C27B0"
                    hover_background "#AB47BC"
                    text_color "#fff"
                
                textbutton "Dump Logs to File":
                    action Function(urw_log.dump_to_file)
                    xsize 150
                    ysize 35
                    text_size 12
                    text_xalign 0.5
                    background "#2196F3"
                    hover_background "#42A5F5"
                    text_color "#fff"
                
                textbutton "Force Save Now":
                    action Function(urw_force_save)
                    xsize 140
                    ysize 35
                    text_size 12
                    text_xalign 0.5
                    background "#4CAF50"
                    hover_background "#66BB6A"
                    text_color "#fff"
                
                textbutton "Check Persistent":
                    action [
                        Function(lambda: urw_log.persistent_debug("Manual check - urw_text_size: {0}".format(persistent.urw_text_size))),
                        Function(lambda: urw_log.persistent_debug("Manual check - urw_theme: {0}".format(persistent.urw_theme)))
                    ]
                    xsize 140
                    ysize 35
                    text_size 12
                    text_xalign 0.5
                    background "#FF9800"
                    hover_background "#FFB74D"
                    text_color "#fff"
                
                textbutton "Close":
                    action Hide("URW_debug", transition=dissolve)
                    xsize 90
                    ysize 35
                    text_size 12
                    text_xalign 0.5
                    background "#4fc3f7"
                    hover_background "#5fd3f7"
                    text_color "#000"

init 999 python:
    # Add keyboard shortcut
    config.underlay.append(
        renpy.Keymap(
            alt_K_w = lambda: renpy.run(Show("URW_preferences"))
        )
    )
    
    # Add after load callback
    def urw_after_load():
        urw_log.persistent_debug("=== AFTER LOAD CALLBACK ===")
        urw_log.persistent_debug("Loaded persistent.urw_text_size: {0}".format(persistent.urw_text_size))
        urw_log.persistent_debug("Loaded persistent.urw_theme: {0}".format(persistent.urw_theme))
        urw_log.persistent_debug("Loaded persistent.urw_logs_cleared: {0}".format(persistent.urw_logs_cleared))
        
        if hasattr(store, 'urw_menu_finder') and hasattr(urw_menu_finder, 'reset_sequence'):
            urw_menu_finder.reset_sequence()
            urw_log.info("Menu sequence reset after load", "LOAD")
        
        urw_log.persistent_debug("=== END AFTER LOAD ===")
    
    config.after_load_callbacks.append(urw_after_load)
    
    # Add startup logging
    urw_log.persistent_debug("=== REN'PY STARTUP COMPLETE ===")
    urw_log.persistent_debug("Final startup values:")
    urw_log.persistent_debug("  urw_text_size: {0}".format(persistent.urw_text_size))
    urw_log.persistent_debug("  urw_theme: {0}".format(persistent.urw_theme))
    urw_log.persistent_debug("  urw_max_consequences: {0}".format(persistent.urw_max_consequences))
    urw_log.persistent_debug("  urw_logs_cleared: {0}".format(persistent.urw_logs_cleared))

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
        xsize 900
        ymaximum 700
        padding (30, 25)
        
        vbox:
            spacing 15
            
            text "{color=#4fc3f7}{size=24}{b}▼ Full Consequence Viewer{/b}{/size}{/color}":
                xalign 0.5
            
            add Solid("#4fc3f7", xysize=(300, 2)):
                xalign 0.5
            
            text "{color=#888}{size=14}View complete consequence details for current menu choices{/size}{/color}":
                xalign 0.5
            
            null height 10
            
            python:
                _viewer_data = urw_get_current_menu_consequences()
                _has_data = _viewer_data and len(_viewer_data) > 0
            
            if _has_data:
                viewport:
                    scrollbars "vertical"
                    mousewheel True
                    draggable True
                    ysize 450
                    xfill True
                    
                    vbox:
                        spacing 20
                        
                        for _choice_idx, _choice_data in enumerate(_viewer_data):
                            python:
                                _choice_num = _choice_idx + 1
                                _choice_caption = _choice_data.get('caption', 'Unknown')
                            
                            frame:
                                background "#16213e"
                                xfill True
                                padding (20, 15)
                                
                                vbox:
                                    spacing 10
                                    
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
                                                        
                                                        text "{color=#fff}{size=14}[_cons_var]{/size}{/color}"
                                                        
                                                        if _cons_val:
                                                            text "{color=#888}{size=12}Value: [_cons_val]{/size}{/color}"
                                                        
                                                        text "{color=#666}{size=11}Type: [_cons_desc]{/size}{/color}"
                                                
                                                if _cons_type == 'condition' and _has_branches:
                                                    python:
                                                        _branch_items = list(_cons.branch_consequences.items())
                                                    
                                                    for _branch_key, _branch_cons in _branch_items:
                                                        python:
                                                            if _branch_key.startswith("if "):
                                                                _branch_color = "#4fc3f7"
                                                                _branch_icon = "▶"
                                                            elif _branch_key.startswith("elif "):
                                                                _branch_color = "#ffa726"
                                                                _branch_icon = "▷"
                                                            else:
                                                                _branch_color = "#ab47bc"
                                                                _branch_icon = "▹"
                                                            _branch_display = _branch_key
                                                        
                                                        frame:
                                                            background "#0d1520"
                                                            xfill True
                                                            left_margin 40
                                                            padding (15, 10)
                                                            
                                                            vbox:
                                                                spacing 8
                                                                
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
                    padding (30, 40)
                    
                    vbox:
                        spacing 15
                        xalign 0.5
                        
                        text "{color=#888}{size=18}No menu currently active{/size}{/color}":
                            xalign 0.5
                        
                        text "{color=#666}{size=14}Open this viewer during a menu choice to see full consequence details.{/size}{/color}":
                            xalign 0.5
                            text_align 0.5
            
            null height 10
            
            # Footer buttons
            hbox:
                spacing 20
                xalign 0.5
                
                textbutton "Refresh":
                    action NullAction()
                    xsize 120
                    ysize 40
                    text_size 14
                    text_xalign 0.5
                    background "#2196F3"
                    hover_background "#42A5F5"
                    text_color "#fff"
                
                textbutton "Close":
                    action Hide("URW_full_viewer", transition=dissolve)
                    xsize 120
                    ysize 40
                    text_size 14
                    text_xalign 0.5
                    background "#4fc3f7"
                    hover_background "#5fd3f7"
                    text_color "#000"
