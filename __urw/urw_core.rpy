####################################################################
####            Universal Ren'Py Walkthrough System             ####
####               (C) Knox Emberlyn 2025-2026                  ####
####################################################################

####################################################################

init -1000 python:
    class URWConfig:
        """URW Configuration Container"""
        VERSION = "2.0.1"
        DEBUG = False
        DEVELOPER = True
        
        # Cache settings
        MAX_MENU_CACHE = 500
        MAX_CONSEQUENCE_CACHE = 300
        CACHE_CLEANUP_THRESHOLD = 0.8
        
        # Analysis settings
        MAX_RECURSION_DEPTH = 10
        MAX_CONSEQUENCES_PER_CHOICE = 50
        ANALYZE_NESTED_CONDITIONALS = True
        
        # Display settings
        DEFAULT_TEXT_SIZE = 25
        DEFAULT_MAX_DISPLAY = 3
        
    urw_config = URWConfig()

init -999:
    default persistent.urw_enabled = True
    default persistent.urw_text_size = 25
    default persistent.urw_choice_text_size = 25
    default persistent.urw_auto_adapt_buttons = True
    default persistent.urw_custom_choice_menu = True
    default persistent.urw_max_consequences = 3
    default persistent.urw_show_all = True
    default persistent.urw_spoiler_mode = False
    default persistent.urw_highlight_best = True
    default persistent.urw_theme = "modern"
    default persistent.urw_full_text = False  # Show full text without truncation
    default persistent.urw_hide_dialogue = True  # Hide Say/TranslateSay dialogue hints
    
    # Type filters
    default persistent.urw_filters = {
        'variables': True,      # Variable changes (+= -= =)
        'conditions': True,     # If/elif/else
        'flow': True,          # Jump/call/return
        'functions': True,      # Function calls
        'flags': True,         # Boolean flags
        'relationships': True,  # Relationship variables
        'stats': True,         # Stat changes
        'unknown': False       # Unknown types
    }
    
    # Name-based filters
    default persistent.urw_name_filters = {
        'hide_underscore': True,
        'hide_renpy': True,
        'hide_config': False,
        'hide_store': True,
        'hide_internal': True,
        'custom_hide': [],      # List of custom prefixes to hide
        'custom_show': [],      # List of custom prefixes to always show (priority)
        'important_vars': []    # Variables marked as important
    }
    
    # Choice history
    default persistent.urw_choice_history = []
    default persistent.urw_max_history = 100
    
    # Statistics
    default persistent.urw_stats = {
        'menus_analyzed': 0,
        'choices_made': 0,
        'consequences_shown': 0,
        'session_start': None
    }

init -998 python:
    import collections
    import collections.abc
    import weakref
    import time as _time
    import re
    import ast as _ast
    import hashlib
    
    ##################################################################
    #                    URW LOGGING SYSTEM                          #
    ##################################################################
    
    class URWLogger:
        """Logging system for URW"""
        
        _instance = None
        
        def __new__(cls):
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._initialized = False
            return cls._instance
        
        def __init__(self):
            if self._initialized:
                return
            self._initialized = True
            self._log_buffer = []
            self._max_buffer = 1000
            self._enabled = urw_config.DEBUG
            
        def log(self, message, level="INFO", category="GENERAL"):
            """Log a message with level and category"""
            if not self._enabled and level != "ERROR":
                return
                
            timestamp = _time.strftime("%H:%M:%S")
            entry = f"[URW {timestamp}] [{level}] [{category}] {message}"
            
            self._log_buffer.append(entry)
            if len(self._log_buffer) > self._max_buffer:
                self._log_buffer = self._log_buffer[-self._max_buffer//2:]
            
            if urw_config.DEBUG:
                print(entry)
        
        def debug(self, message, category="DEBUG"):
            self.log(message, "DEBUG", category)
            
        def info(self, message, category="INFO"):
            self.log(message, "INFO", category)
            
        def warn(self, message, category="WARN"):
            self.log(message, "WARN", category)
            
        def error(self, message, category="ERROR"):
            self.log(message, "ERROR", category)
            
        def get_logs(self, count=50):
            return self._log_buffer[-count:]
            
        def clear(self):
            self._log_buffer.clear()
    
    urw_log = URWLogger()
    
    ##################################################################
    #                    URW CACHE SYSTEM                            #
    ##################################################################
    
    class URWCache:
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
                    
            urw_log.debug(f"Cache '{self.name}' cleaned: removed {remove_count} entries", "CACHE")
            
        def clear(self):
            self._cache.clear()
            self._access_times.clear()
            
        def stats(self):
            total = self._hit_count + self._miss_count
            hit_rate = (self._hit_count / total * 100) if total > 0 else 0
            return {
                'size': len(self._cache),
                'max_size': self.max_size,
                'hits': self._hit_count,
                'misses': self._miss_count,
                'hit_rate': f"{hit_rate:.1f}%"
            }
    
    # Global caches
    urw_menu_cache = URWCache(urw_config.MAX_MENU_CACHE, "menu")
    urw_consequence_cache = URWCache(urw_config.MAX_CONSEQUENCE_CACHE, "consequence")
    urw_node_cache = URWCache(200, "node")
    
    ##################################################################
    #                URW CONSEQUENCE TYPES                           #
    ##################################################################
    
    class ConsequenceType:
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
    
    class URWConsequence:
        """Represents a single consequence from a choice"""
        
        def __init__(self, ctype, variable, value="", display="", source_line=0, confidence=1.0, sub_consequences=None, branch_consequences=None):
            self.type = ctype
            self.variable = variable
            self.value = value
            self.display = display or f"{variable}"
            self.source_line = source_line
            self.confidence = confidence
            self.metadata = ConsequenceType.get_metadata(ctype)
            self.sub_consequences = sub_consequences or []  # For conditions: flat list of nested consequences
            # branch_consequences: dict of {"if condition": [cons], "elif cond": [cons], "else": [cons]}
            self.branch_consequences = branch_consequences or {}
            
        def __repr__(self):
            return f"<Consequence {self.type}: {self.variable}={self.value}>"
            
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
                        return f"{icon}{self.variable} ({self.value})"
                    return f"{icon}{self.variable}"
                elif self.type == "assign":
                    val = self.value[:15] + "..." if len(str(self.value)) > 15 else self.value
                    return f"{self.variable}={val}"
                elif self.type == "boolean":
                    return f"{self.variable}={self.value}"
                elif self.type in ["jump", "call"]:
                    return f"{icon} {self.variable}"
                elif self.type == "return":
                    return f"{icon}"
                elif self.type == "condition":
                    cond = str(self.variable)[:25]
                    return f"{icon} {cond}"
                else:
                    return self.display[:30]
            
            elif style == "detailed":
                return f"{icon} {self.type.upper()}: {self.variable} = {self.value}"
            
            return self.display
            
        def get_priority(self):
            """Get display priority (higher = more important)"""
            base_priority = self.metadata["priority"]
            
            # Boost priority for relationship/stat-like variables
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
    
    class URWAnalyzer:
        """AST analyzer for extracting consequences"""
        
        # Ren'Py control exceptions to never catch
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
        
        # Statements to skip (visual/audio/dialogue only)
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
            """Analyze a block of statements and extract consequences"""
            if depth > self._max_depth:
                urw_log.warn(f"Max recursion depth reached at {depth}", "ANALYZER")
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
                    urw_log.error(f"Error analyzing statement: {e}", "ANALYZER")
                    continue
                    
            return consequences
            
        def _analyze_statement(self, stmt, depth):
            """Analyze a single statement"""
            consequences = []
            
            if stmt is None:
                return consequences
                
            stmt_class = stmt.__class__.__name__
            
            if stmt_class in self.SKIP_STATEMENTS:
                return consequences
                
            # Python code
            if stmt_class == 'Python':
                consequences.extend(self._analyze_python(stmt, depth))
                
            # Jump statement
            elif stmt_class == 'Jump':
                target = getattr(stmt, 'target', '?')
                consequences.append(URWConsequence(
                    ConsequenceType.JUMP, target, '', f"→ {target}",
                    getattr(stmt, 'linenumber', 0)
                ))
                
            # Call statement  
            elif stmt_class == 'Call':
                label = getattr(stmt, 'label', '?')
                consequences.append(URWConsequence(
                    ConsequenceType.CALL, label, '', f"⇒ {label}",
                    getattr(stmt, 'linenumber', 0)
                ))
                
            # Return statement
            elif stmt_class == 'Return':
                expr = getattr(stmt, 'expression', None)
                val = str(expr) if expr else 'end'
                consequences.append(URWConsequence(
                    ConsequenceType.RETURN, 'return', val, f"← {val}",
                    getattr(stmt, 'linenumber', 0)
                ))
                
            # If/conditional statement
            elif stmt_class == 'If':
                consequences.extend(self._analyze_conditional(stmt, depth))
                
            # While loop
            elif stmt_class == 'While':
                consequences.extend(self._analyze_while(stmt, depth))
                
            # Menu (nested)
            elif stmt_class == 'Menu':
                # Don't recurse into nested menus
                pass
                
            # User statement (custom)
            elif stmt_class == 'UserStatement':
                # Could be anything - try to extract info
                pass
                
            else:
                # Unknown statement type
                for attr in ['target', 'label', 'expression', 'name', 'value']:
                    if hasattr(stmt, attr):
                        value = getattr(stmt, attr)
                        if value and not str(value).startswith('_'):
                            consequences.append(URWConsequence(
                                ConsequenceType.UNKNOWN,
                                f"{stmt_class}.{attr}", str(value)[:30], '',
                                getattr(stmt, 'linenumber', 0),
                                confidence=0.5
                            ))
                            break
                            
            return consequences
            
        def _analyze_python(self, stmt, depth):
            """Analyze Python statement"""
            consequences = []
            source = None
            
            # Get source code
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
            """Parse Python source using AST"""
            consequences = []
            
            try:
                tree = _ast.parse(source)
                
                for node in _ast.walk(tree):
                    # Assignment: x = value
                    if isinstance(node, _ast.Assign):
                        for target in node.targets:
                            if isinstance(target, _ast.Name):
                                var_name = target.id
                                try:
                                    if hasattr(_ast, 'unparse'):
                                        value = _ast.unparse(node.value)
                                    elif isinstance(node.value, _ast.Constant):
                                        value = str(node.value.value)
                                    else:
                                        value = "?"
                                        
                                    # Detect type based on value
                                    ctype = ConsequenceType.ASSIGN
                                    if value in ['True', 'False']:
                                        ctype = ConsequenceType.BOOLEAN
                                        
                                    consequences.append(URWConsequence(
                                        ctype, var_name, value[:50]
                                    ))
                                except:
                                    consequences.append(URWConsequence(
                                        ConsequenceType.ASSIGN, var_name, "?"
                                    ))
                    
                    # Augmented assignment: x += value, x -= value
                    elif isinstance(node, _ast.AugAssign):
                        if isinstance(node.target, _ast.Name):
                            var_name = node.target.id
                            op = node.op.__class__.__name__
                            
                            try:
                                if hasattr(_ast, 'unparse'):
                                    value = _ast.unparse(node.value)
                                elif isinstance(node.value, _ast.Constant):
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
                    
                    # If statement in Python
                    elif isinstance(node, _ast.If):
                        try:
                            if hasattr(_ast, 'unparse'):
                                cond_text = _ast.unparse(node.test)
                            else:
                                cond_text = "condition"
                                
                            if len(cond_text) > 30:
                                cond_text = cond_text[:27] + "..."
                                
                            consequences.append(URWConsequence(
                                ConsequenceType.CONDITION, f"if {cond_text}", ""
                            ))
                        except:
                            pass
                    
                    # Function calls
                    elif isinstance(node, _ast.Call):
                        try:
                            if hasattr(_ast, 'unparse'):
                                call_text = _ast.unparse(node)
                            elif isinstance(node.func, _ast.Name):
                                call_text = node.func.id
                            elif isinstance(node.func, _ast.Attribute):
                                call_text = f"*.{node.func.attr}"
                            else:
                                call_text = "function"
                                
                            # Skip internal functions
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
                urw_log.debug(f"AST parse error: {e}", "ANALYZER")
                
            return consequences
            
        def _parse_python_regex(self, source):
            """Fallback regex parsing for Python code"""
            consequences = []
            
            lines = source.split('\n')
            for line in lines:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                    
                # Augmented assignment
                if '+=' in line:
                    try:
                        var, val = line.split('+=', 1)
                        var = re.sub(r'\[.*?\]', '', var.strip())
                        consequences.append(URWConsequence(
                            ConsequenceType.INCREASE, var, val.strip()[:20]
                        ))
                    except:
                        pass
                        
                elif '-=' in line:
                    try:
                        var, val = line.split('-=', 1)
                        var = re.sub(r'\[.*?\]', '', var.strip())
                        consequences.append(URWConsequence(
                            ConsequenceType.DECREASE, var, val.strip()[:20]
                        ))
                    except:
                        pass
                        
                # Regular assignment (avoid comparison operators)
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
                            
            return consequences
            
        def _analyze_conditional(self, stmt, depth):
            """Analyze If statement"""
            consequences = []
            
            if not hasattr(stmt, 'entries'):
                return consequences
                
            branch_info = []
            all_sub_consequences = []
            branch_consequences = {}  # Dict to store consequences per branch
            
            num_entries = len(stmt.entries) if hasattr(stmt.entries, '__len__') else 0
            
            for idx, (condition, block) in enumerate(stmt.entries):
                is_last = (idx == num_entries - 1)
                
                if condition is not None:
                    cond_str = str(condition).strip()
                    if cond_str.startswith('store.'):
                        cond_str = cond_str[6:]
                    
                    
                    is_else_branch = is_last and cond_str.lower() in ('true', '1')
                    
                    if is_else_branch:
                        branch_label = "else"
                        branch_key = "else"
                    else:
                        # Store full condition for branch key
                        full_cond_str = cond_str
                        if len(cond_str) > 35:
                            cond_str = cond_str[:32] + "..."
                            
                        if idx == 0:
                            branch_label = f"if {cond_str}"
                            branch_key = f"if {full_cond_str}"
                        else:
                            branch_label = f"elif {cond_str}"
                            branch_key = f"elif {full_cond_str}"
                else:
                    branch_label = "else"
                    branch_key = "else"
                    
                branch_info.append(branch_label)
                    
                if block and depth < self._max_depth:
                    sub_cons = self.analyze_block(block, depth + 1)
                    all_sub_consequences.extend(sub_cons)
                    # Store consequences for this specific branch
                    branch_consequences[branch_key] = sub_cons
                else:
                    branch_consequences[branch_key] = []
                    
            # Create condition consequence
            if branch_info:
                if len(branch_info) == 1:
                    cond_text = branch_info[0]
                elif len(branch_info) == 2 and branch_info[1] == "else":
                    cond_text = f"{branch_info[0]}/else"
                else:
                    cond_text = f"{branch_info[0]} (+{len(branch_info)-1})"
                    
                consequences.append(URWConsequence(
                    ConsequenceType.CONDITION, cond_text, str(len(all_sub_consequences)),
                    source_line=getattr(stmt, 'linenumber', 0),
                    sub_consequences=all_sub_consequences,  # Flat list for backward compat
                    branch_consequences=branch_consequences  # Organized by branch
                ))
                
            # Add important sub-consequences to main list too
            important_types = [ConsequenceType.INCREASE, ConsequenceType.DECREASE,
                            ConsequenceType.JUMP, ConsequenceType.CALL]
            for sub in all_sub_consequences:
                if sub.type in important_types:
                    consequences.append(sub)
                    
            return consequences
            
        def _analyze_while(self, stmt, depth):
            """Analyze While loop"""
            consequences = []
            
            if hasattr(stmt, 'condition'):
                cond_str = str(stmt.condition)[:30]
                consequences.append(URWConsequence(
                    ConsequenceType.CONDITION, f"while {cond_str}", ""
                ))
                
            if hasattr(stmt, 'block') and depth < self._max_depth:
                consequences.extend(self.analyze_block(stmt.block, depth + 1))
                
            return consequences
    
    # Global analyzer instance
    urw_analyzer = URWAnalyzer()
    
    ##################################################################
    #                URW MENU FINDER                                 #
    ##################################################################
    
    class URWMenuFinder:
        """Menu detection using multiple strategies"""
        
        def __init__(self):
            self._strategy_scores = {}
            self._seen_menus_by_label = {}  # label -> [menu_line, menu_line, ...]
            self._last_label = None
            self._menu_index_in_label = 0
            self._global_menu_history = []  # List of (caption_hash, line_found)
            self._global_menu_index = 0
            
        def reset_sequence(self, label=None):
            """Reset menu sequence tracking (call on label change or game restart)"""
            if label:
                self._seen_menus_by_label[label] = []
            else:
                self._seen_menus_by_label.clear()
            self._menu_index_in_label = 0
            self._global_menu_history = []
            self._global_menu_index = 0
            
        def find_menu_node(self, items):
            """Find the correct menu AST node for the given items"""
            urw_log.debug(f"Finding menu with {len(items)} items", "MENU_FINDER")
            
            context = self._get_execution_context()
            if not context:
                urw_log.warn("No execution context available", "MENU_FINDER")
                return None, None
            
            current_label = context.get('label')
            if current_label != self._last_label:
                self._last_label = current_label
                self._menu_index_in_label = 0
                urw_log.debug(f"Label changed to: {current_label}", "MENU_FINDER")
                
            cache_key = self._create_cache_key(items, context)
            
            cached = urw_menu_cache.get(cache_key)
            if cached:
                urw_log.debug(f"Menu found in cache (index {self._menu_index_in_label})", "MENU_FINDER")
                self._menu_index_in_label += 1
                return cached
                
            # Strategy 1: Direct execution stack lookup
            result = self._find_via_execution_stack(items, context)
            if result[0]:
                self._record_seen_menu(result[0], context)
                urw_menu_cache.set(cache_key, result)
                return result
                
            # Strategy 2: Sequence-aware matching (for duplicate menus like Yes/No)
            result = self._find_via_sequence(items, context)
            if result[0]:
                self._record_seen_menu(result[0], context)
                urw_menu_cache.set(cache_key, result)
                return result
                
            # Strategy 3: File + line proximity
            result = self._find_via_proximity(items, context)
            if result[0]:
                self._record_seen_menu(result[0], context)
                urw_menu_cache.set(cache_key, result)
                return result
                
            # Strategy 4: Text matching across all menus
            result = self._find_via_text_match(items, context)
            if result[0]:
                self._record_seen_menu(result[0], context)
                urw_menu_cache.set(cache_key, result)
                return result
                
            urw_log.warn("Could not find matching menu node", "MENU_FINDER")
            # Still increment even on failure to keep sequence consistent
            self._menu_index_in_label += 1
            return None, None
        
        def _record_seen_menu(self, menu_node, context):
            """Record that we've seen this menu"""
            label = context.get('label', '__global__')
            if label not in self._seen_menus_by_label:
                self._seen_menus_by_label[label] = []
            if hasattr(menu_node, 'linenumber'):
                self._seen_menus_by_label[label].append(menu_node.linenumber)
                # Also record in global history
                self._global_menu_history.append(menu_node.linenumber)
            self._menu_index_in_label += 1
            self._global_menu_index += 1
            
        def _get_caption_signature(self, items):
            """Get a signature string from menu captions"""
            captions = []
            for item in items:
                if hasattr(item, 'caption'):
                    text = str(item.caption)
                elif isinstance(item, (list, tuple)) and len(item) > 0:
                    text = str(item[0])
                else:
                    text = str(item)
                # Clean and normalize
                clean = re.sub(r'\{[^}]*\}', '', text).strip().lower()
                captions.append(clean)
            return "|".join(sorted(captions))  # Sort for consistency
            
        def _find_via_sequence(self, items, context):
            """Find menu using global sequence tracking for duplicate menus"""
            try:
                script = renpy.game.script
                
                # Get caption signature for this menu
                caption_sig = self._get_caption_signature(items)
                
                # Find ALL menus across all files with matching captions
                matching_menus = []
                
                for node_name, node in script.namemap.items():
                    if not isinstance(node, renpy.ast.Menu):
                        continue
                    if not hasattr(node, 'items') or not hasattr(node, 'linenumber'):
                        continue
                    
                    # Check text match
                    if self._items_match(node.items, items):
                        matching_menus.append(node)
                
                if not matching_menus:
                    return None, None
                
                # Sort by filename then line number for consistent ordering
                matching_menus.sort(key=lambda n: (n.filename or '', n.linenumber))
                
                urw_log.debug(f"Found {len(matching_menus)} menus matching '{caption_sig[:30]}...'", "MENU_FINDER")
                
                # If only one match, use it
                if len(matching_menus) == 1:
                    return matching_menus[0], {'strategy': 'sequence_single', 'offset': 0}
                
                # Multiple matches - use global history to find the right one
                # Find menus we haven't returned yet (by line number)
                seen_lines = set(self._global_menu_history)
                
                for menu in matching_menus:
                    if menu.linenumber not in seen_lines:
                        urw_log.debug(f"Sequence match: line {menu.linenumber} (unseen, global idx {self._global_menu_index})", "MENU_FINDER")
                        return menu, {'strategy': 'sequence_global', 'offset': 0}
                
                # All seen? Use global index modulo to cycle through
                idx = self._global_menu_index % len(matching_menus)
                menu = matching_menus[idx]
                urw_log.debug(f"Sequence match: line {menu.linenumber} (by global index {self._global_menu_index} -> {idx})", "MENU_FINDER")
                return menu, {'strategy': 'sequence_index', 'offset': 0}
                
            except Exception as e:
                urw_log.error(f"Error in sequence search: {e}", "MENU_FINDER")
                return None, None
            
        def _get_execution_context(self):
            """Get current execution context"""
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
                
                # Helper function to lookup node from node name and extract location
                def get_node_location(node_name):
                    """Get (filename, linenumber) from a node name by looking up the actual node"""
                    try:
                        if node_name is None:
                            return None, 0
                        # Lookup the node in the script's namemap
                        node = script.lookup(node_name)
                        if node and hasattr(node, 'filename') and hasattr(node, 'linenumber'):
                            return node.filename, node.linenumber
                    except Exception:
                        pass
                    return None, 0
                
                # Method 1
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
                        urw_log.debug(f"Could not lookup current node: {e}", "MENU_FINDER")
                
                # Method 2
                if not context['filename'] and hasattr(ctx, 'call_location_stack'):
                    stack = ctx.call_location_stack
                    if isinstance(stack, (list, tuple)) and stack:
                        for node_name in reversed(list(stack)):
                            filename, linenumber = get_node_location(node_name)
                            if filename:
                                context['filename'] = filename
                                context['linenumber'] = linenumber
                                break
                
                # Method 3
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
                
                # Get current label
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
                    
                # Get call stack info safely
                if hasattr(ctx, 'return_stack'):
                    stack = ctx.return_stack
                    if isinstance(stack, (list, tuple)):
                        context['call_stack'] = list(stack[-5:])
                    
                return context
                
            except Exception as e:
                urw_log.error(f"Error getting execution context: {e}", "MENU_FINDER")
                return None
                
        def _create_cache_key(self, items, context):
            """Create unique cache key that includes sequence index for duplicate menus"""
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
            """Find menu using execution stack"""
            try:
                # If context already found the menu node, use it
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
            """Check if AST menu items match runtime items"""
            # Extract runtime captions
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
            
            # Extract AST captions
            ast_captions = []
            for item in ast_items:
                if item and len(item) >= 1:
                    caption = str(item[0]) if item[0] else ""
                    clean = re.sub(r'\{[^}]*\}', '', caption).strip()
                    ast_captions.append(clean)
            
            # Check if all runtime captions exist in AST captions
            matches = 0
            for rc in runtime_captions:
                if rc in ast_captions:
                    matches += 1
            
            # Consider a match if most runtime items are found
            return matches >= len(runtime_captions) * 0.8
                
        def _find_via_proximity(self, items, context):
            """Find menu using file/line proximity"""
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
                urw_log.debug(f"Found menu at line {best_node.linenumber} (score: {best_score})", "MENU_FINDER")
                
                return best_node, best_info
                
            except Exception as e:
                urw_log.error(f"Error in proximity search: {e}", "MENU_FINDER")
                return None, None
                
        def _find_via_text_match(self, items, context):
            """Find menu using text matching (last resort)"""
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
                        
                if best_match and best_score >= len(items) * 8:  # At least 80% match
                    return best_match, best_info
                    
                return None, None
                
            except Exception as e:
                urw_log.error(f"Error in text match search: {e}", "MENU_FINDER")
                return None, None
                
        def _calculate_match_score(self, node, items, target_line):
            """Calculate how well a menu node matches - prioritize text matching over line proximity"""
            score = 0
            info = {'strategy': 'proximity', 'offset': 0}
            
            node_items = node.items
            distance = abs(node.linenumber - target_line)
            
            text_matches = self._count_text_matches(node_items, items)
            text_match_ratio = text_matches / max(len(items), 1)
            
            # Text matching is primary scoring (up to 200 points)
            if text_match_ratio >= 1.0:
                score += 200  # Perfect match
                info['strategy'] = 'text_match'
            elif text_match_ratio >= 0.8:
                score += 150
                info['strategy'] = 'text_match'
            elif text_match_ratio >= 0.5:
                score += 100
            else:
                score += int(text_match_ratio * 50)
            
            # Distance scoring (secondary, up to 50 points)
            # Only matters if text match is inconclusive
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
                
            # Item count matching (up to 30 points)
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
            """Count how many runtime items match node items by text"""
            # Extract node captions
            node_texts = set()
            for item in node_items:
                if item and len(item) > 0:
                    text = str(item[0]) if item[0] else ""
                    clean = re.sub(r'\{[^}]*\}', '', text).strip().lower()
                    if clean:
                        node_texts.add(clean)
            
            # Count matches
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
            """Score text matching between node and items"""
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
