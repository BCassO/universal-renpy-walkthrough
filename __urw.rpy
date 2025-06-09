#################################################################
######### Universal Walkthrough System v1.0 Beta ################
#########                                        ################
#########    Copyright © Knox Emberlyn 2025.     ################
#################################################################
##
## INSTALLATION:
##   1. Download this __urw.rpy file
##   2. Place it in your game's game\ folder  
##   3. Start or load your game
##   4. Press Alt+W in-game to open walkthrough preferences
##
## COMPATIBILITY:
##   - Tested on various Ren'Py 8.x.x engines
##   - Should work with any Ren'Py 8 series game
##   - Works with both compiled (.rpyc) and source (.rpy) games
##
## TROUBLESHOOTING:
##   If the walkthrough doesn't work with your game:
##   1. Open this file in a text editor
##   2. Change line 41: debug = False  ->  debug = True  
##   3. Run the game and try some menu choices
##   4. Press Shift+O to open console and check for error messages
##   5. Submit bug reports with debug output to: 
##      https://github.com/BCassO/universal-renpy-walkthrough/issues
##
## BUG REPORTS:
##   Before reporting issues, please:
##   - Search existing issues at: https://github.com/BCassO/universal-renpy-walkthrough/issues
##   - Include your game name, Ren'Py version, and debug output
##   - Provide details - "it doesn't work" helps nobody!
##
## SUPPORT:
##   Repository: https://github.com/BCassO/universal-renpy-walkthrough
##   Issues: https://github.com/BCassO/universal-renpy-walkthrough/issues
##   Documentation: https://github.com/BCassO/universal-renpy-walkthrough/blob/main/README.md
##
#################################################################

init -999 python in dukeconfig:
    debug = False  # Set to True to enable debug messages

init -998 python:
    import collections.abc
    import builtins
    import re
    import weakref

    # Ren'Py control exceptions that should NOT be caught
    RENPY_CONTROL_EXCEPTIONS = (
        renpy.game.RestartContext,
        renpy.game.RestartTopContext, 
        renpy.game.FullRestartException,
        renpy.game.UtterRestartException,
        renpy.game.QuitException,
        renpy.game.JumpException,
        renpy.game.JumpOutException,
        renpy.game.CallException,
        renpy.game.EndReplay
    )

    persistent.universal_wt_text_size = 25 # Default text size for walkthrough display

    # Consequence analysis cache with memory management
    consequence_cache = {}
    consequence_cache_access = {}
    MAX_CONSEQUENCE_CACHE = 200

    def get_cached_consequences(choice_block_id):
        """Get cached consequences with LRU management"""
        if choice_block_id in consequence_cache:
            consequence_cache_access[choice_block_id] = renpy.get_game_runtime()
            return consequence_cache[choice_block_id]
        return None

    def cache_consequences(choice_block_id, consequences):
        """Cache consequences with size limit"""
        # Cleanup cache if too large
        if len(consequence_cache) >= MAX_CONSEQUENCE_CACHE:
            # Remove oldest 50 entries
            sorted_cache = sorted(consequence_cache_access.items(), key=lambda x: x[1])
            for i in range(50):
                if i < len(sorted_cache):
                    old_key = sorted_cache[i][0]
                    if old_key in consequence_cache:
                        del consequence_cache[old_key]
                    del consequence_cache_access[old_key]
        
        consequence_cache[choice_block_id] = consequences
        consequence_cache_access[choice_block_id] = renpy.get_game_runtime()

    menu_node_weakrefs = {}

    def store_menu_node_weakref(key, menu_node):
        """Store menu node as weak reference"""
        try:
            menu_node_weakrefs[key] = weakref.ref(menu_node)
        except TypeError:
            # Some objects can't be weak referenced
            menu_node_weakrefs[key] = menu_node

    def get_menu_node_from_weakref(key):
        """Get menu node from weak reference"""
        if key in menu_node_weakrefs:
            ref = menu_node_weakrefs[key]
            if hasattr(ref, '__call__'):  # It's a weak reference
                node = ref()
                if node is None:  # Object was garbage collected
                    del menu_node_weakrefs[key]
                    return None
                return node
            else:  # Direct reference (fallback)
                return ref
        return None

    def extract_choice_consequences(choice_block):
        """Extract detailed consequences from a choice block - UNIVERSAL for all Ren'Py games"""
        
        choice_block_id = id(choice_block) if choice_block else 0
    
        # Check cache first
        cached_result = get_cached_consequences(choice_block_id)
        if cached_result is not None:
            if dukeconfig.debug: print("Using cached consequences for block {}".format(choice_block_id))
            return cached_result
        
        
        if dukeconfig.debug: print("=== UNIVERSAL WALKTHROUGH ANALYZER ===")
        if dukeconfig.debug: print("Choice block type:", type(choice_block))
        
        consequences = []
        statements = []
        
        # Handle both list format and block format
        if isinstance(choice_block, collections.abc.Sequence) and not isinstance(choice_block, (str, bytes)):
            statements = choice_block
            if dukeconfig.debug: print("Processing choice block as sequence with {} statements".format(len(statements)))
        elif hasattr(choice_block, 'children'):
            statements = choice_block.children
            if dukeconfig.debug: print("Processing choice block with children attribute")
        elif choice_block is None:
            if dukeconfig.debug: print("Choice block is None, returning empty consequences")
            return consequences
        else:
            if dukeconfig.debug: print("Unknown choice block format: {}, returning empty consequences".format(type(choice_block)))
            return consequences
        
        if not statements:
            if dukeconfig.debug: print("No statements found in the choice block")
            return consequences
            
        if dukeconfig.debug: print("Number of statements:", len(statements))
        
        # Process each statement to extract consequences
        for i, stmt in enumerate(statements):
            if dukeconfig.debug: print("Statement {}: {}".format(i, type(stmt)))
            
            # Handle renpy.ast.Python statements - MOST IMPORTANT FOR VARIABLES
            if hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'Python':
                if dukeconfig.debug: print("  Found Python statement")
                source = None
                
                # Try to get source code
                if hasattr(stmt, 'code'):
                    code_obj = stmt.code
                    if dukeconfig.debug: print("  Code object type: {}".format(type(code_obj)))
                    
                    # Try different attributes for source
                    for attr in ['source', 'py', 'python']:
                        if hasattr(code_obj, attr):
                            potential_source = getattr(code_obj, attr)
                            if dukeconfig.debug: print("  Checking code.{}: {}".format(attr, type(potential_source)))
                            if isinstance(potential_source, str):
                                source = potential_source.strip()
                                if dukeconfig.debug: print("  Found source in code.{}: {}".format(attr, repr(source)))
                                break

                # NEW: Fallback for compiled files without source
                if not source and hasattr(stmt, 'code'):
                    try:
                        import dis
                        code_obj = stmt.code.py if hasattr(stmt.code, 'py') else stmt.code
                        
                        # Try to get source from AST if available
                        if hasattr(stmt, 'code') and hasattr(stmt.code, 'source'):
                            source = stmt.code.source
                            if dukeconfig.debug: print("  Found source via AST: {}".format(repr(source)))
                        
                        # Advanced bytecode analysis
                        elif hasattr(code_obj, 'co_code'):
                            # Analyze bytecode for variable operations
                            instructions = list(dis.get_instructions(code_obj))
                            
                            for i, instr in enumerate(instructions):
                                # Look for STORE_NAME, STORE_GLOBAL operations
                                if instr.opname in ['STORE_NAME', 'STORE_GLOBAL', 'STORE_FAST']:
                                    var_name = instr.argval
                                    
                                    # Check previous instruction for operation type
                                    if i > 0:
                                        prev_instr = instructions[i-1]
                                        if prev_instr.opname == 'INPLACE_ADD':
                                            consequences.append(('increase', var_name, '?', 'compiled: {} += ?'.format(var_name)))
                                        elif prev_instr.opname == 'INPLACE_SUBTRACT':
                                            consequences.append(('decrease', var_name, '?', 'compiled: {} -= ?'.format(var_name)))
                                        elif prev_instr.opname in ['LOAD_CONST', 'LOAD_FAST']:
                                            consequences.append(('assign', var_name, '?', 'compiled: {} = ?'.format(var_name)))
                            
                            if dukeconfig.debug: print("  Analyzed {} bytecode instructions".format(len(instructions)))
                    
                    except Exception as e:
                        if dukeconfig.debug: print("  Advanced bytecode analysis failed: {}".format(e))
                
                if source:
                    if dukeconfig.debug: print("  Processing source code: {}".format(repr(source)))
                    
                    # Split multi-line code into individual statements
                    code_lines = [line.strip() for line in source.split('\n') if line.strip()]
                    
                    for line in code_lines:
                        if dukeconfig.debug: print("    Analyzing line: {}".format(repr(line)))
                        
                        # Handle += operations (increments)
                        if '+=' in line:
                            try:
                                var_name = line.split('+=')[0].strip()
                                value_part = line.split('+=')[1].strip()
                                
                                # Clean variable name (remove any array indices, etc.)
                                clean_var = re.sub(r'\[.*?\]', '', var_name)
                                
                                # Try to evaluate the value
                                try:
                                    # Handle simple numeric values
                                    if value_part.isdigit():
                                        actual_value = value_part
                                    elif value_part.replace('.', '').isdigit():
                                        actual_value = value_part
                                    elif value_part.startswith('-') and value_part[1:].isdigit():
                                        actual_value = value_part
                                    else:
                                        actual_value = value_part  # Keep original for complex expressions
                                    
                                    consequences.append(('increase', clean_var, actual_value, line))
                                    if dukeconfig.debug: print("    Added increase: {} += {} (full line: {})".format(clean_var, actual_value, line))
                                except:
                                    consequences.append(('increase', clean_var, '?', line))
                                    if dukeconfig.debug: print("    Added increase: {} += ? (full line: {})".format(clean_var, line))
                            except:
                                consequences.append(('code', 'Variable increase', '', line))
                                if dukeconfig.debug: print("    Added generic increase code: {}".format(line))
                        
                        # Handle -= operations (decrements)
                        elif '-=' in line:
                            try:
                                var_name = line.split('-=')[0].strip()
                                value_part = line.split('-=')[1].strip()
                                
                                clean_var = re.sub(r'\[.*?\]', '', var_name)
                                
                                try:
                                    if value_part.isdigit():
                                        actual_value = value_part
                                    elif value_part.replace('.', '').isdigit():
                                        actual_value = value_part
                                    else:
                                        actual_value = value_part
                                    
                                    consequences.append(('decrease', clean_var, actual_value, line))
                                    if dukeconfig.debug: print("    Added decrease: {} -= {} (full line: {})".format(clean_var, actual_value, line))
                                except:
                                    consequences.append(('decrease', clean_var, '?', line))
                                    if dukeconfig.debug: print("    Added decrease: {} -= ? (full line: {})".format(clean_var, line))
                            except:
                                consequences.append(('code', 'Variable decrease', '', line))
                                if dukeconfig.debug: print("    Added generic decrease code: {}".format(line))
                        
                        # Handle = assignments (but not == comparisons)
                        elif '=' in line and '==' not in line and '!=' not in line and '<=' not in line and '>=' not in line:
                            # Skip control structures
                            if not any(line.strip().startswith(x) for x in ['if ', 'elif ', 'for ', 'while ', 'def ', 'class ', 'import ', 'from ']):
                                try:
                                    var_name = line.split('=')[0].strip()
                                    value_part = line.split('=', 1)[1].strip()
                                    
                                    clean_var = re.sub(r'\[.*?\]', '', var_name)
                                    
                                    # Only include meaningful variable assignments
                                    if not clean_var.startswith('_') and len(clean_var) > 1:
                                        # Skip renpy.pause assignments (they're just timing)
                                        if not clean_var.startswith('renpy.pause'):
                                            # Truncate long values for display
                                            display_value = value_part[:20] + ('...' if len(value_part) > 20 else '')
                                            
                                            consequences.append(('assign', clean_var, display_value, line))
                                            if dukeconfig.debug: print("    Added assignment: {} = {} (full line: {})".format(clean_var, display_value, line))
                                        else:
                                            if dukeconfig.debug: print("    Skipped renpy.pause assignment: {}".format(line))
                                except:
                                    consequences.append(('code', 'Variable assignment', '', line))
                                    if dukeconfig.debug: print("    Added generic assignment code: {}".format(line))
                        
                        # Handle special patterns
                        else:
                            # Check for boolean assignments
                            if any(keyword in line.lower() for keyword in [' = true', ' = false']):
                                try:
                                    var_name = line.split('=')[0].strip()
                                    value_part = line.split('=')[1].strip()
                                    clean_var = re.sub(r'\[.*?\]', '', var_name)
                                    
                                    consequences.append(('boolean', clean_var, value_part, line))
                                    if dukeconfig.debug: print("    Added boolean: {} = {} (full line: {})".format(clean_var, value_part, line))
                                except:
                                    pass
                            
                            # Check for function calls or method calls - BUT FILTER OUT USELESS ONES
                            elif '(' in line and ')' in line:
                                # List of functions to ignore (not useful for walkthrough)
                                ignore_functions = [
                                    'renpy.pause',
                                    'renpy.sound',
                                    'renpy.music', 
                                    'renpy.with_statement',
                                    'renpy.scene',
                                    'renpy.show',
                                    'renpy.hide',
                                    'renpy.say',
                                    'renpy.call_screen',
                                    'renpy.transition'
                                ]
                                
                                # Check if this is a function we should ignore
                                should_ignore = False
                                for ignore_func in ignore_functions:
                                    if ignore_func in line:
                                        should_ignore = True
                                        if dukeconfig.debug: print("    Skipped ignored function: {}".format(line))
                                        break
                                
                                if not should_ignore:
                                    # This might be an important function call
                                    consequences.append(('function', 'Function call', line[:30], line))
                                    if dukeconfig.debug: print("    Added important function call: {}".format(line))
                            
                            # Any other meaningful code (but not comments or empty lines)
                            elif len(line) > 3 and not line.startswith('#') and not line.strip().startswith('renpy.'):
                                consequences.append(('code', 'Python code', line[:30], line))
                                if dukeconfig.debug: print("    Added meaningful code: {}".format(line))
                            else:
                                if dukeconfig.debug: print("    Skipped non-meaningful line: {}".format(line))
                
                else:
                    # Even if we can't get source, note that there's Python code
                    consequences.append(('code', 'Python statement', '', 'Python code executed'))
                    if dukeconfig.debug: print("  Added generic Python statement")
            
            # Handle renpy.ast.Jump statements - NAVIGATION
            elif hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'Jump':
                target = getattr(stmt, 'target', 'unknown')
                if dukeconfig.debug: print("  Found Jump to: {}".format(target))
                consequences.append(('jump', target, '', 'jump {}'.format(target)))
            
            # Handle renpy.ast.Call statements - NAVIGATION
            elif hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'Call':
                label = getattr(stmt, 'label', 'unknown')
                if dukeconfig.debug: print("  Found Call to: {}".format(label))
                consequences.append(('call', label, '', 'call {}'.format(label)))
            
            # Handle renpy.ast.Return statements
            elif hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'Return':
                expr = getattr(stmt, 'expression', None)
                if expr and str(expr) != 'None':
                    if dukeconfig.debug: print("  Found Return: {}".format(expr))
                    consequences.append(('return', str(expr), '', 'return {}'.format(expr)))
                else:
                    consequences.append(('return', 'end', '', 'return'))
            
            # Handle renpy.ast.If statements (conditional code)
            elif hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'If':
                if dukeconfig.debug: print("  Found conditional statement")
                consequences.append(('condition', 'Conditional', '', 'if statement'))
            
            # SKIP visual elements that don't affect gameplay
            elif hasattr(stmt, '__class__') and stmt.__class__.__name__ in ['Say', 'TranslateSay', 'Scene', 'Show', 'Hide', 'With', 'Play', 'Stop', 'Queue']:
                if dukeconfig.debug: print("  Skipping visual/audio statement: {}".format(stmt.__class__.__name__))
                continue

            elif hasattr(stmt, '__class__') and stmt.__class__.__name__ == 'UserStatement':
                # Try to extract info from UserStatement
                if hasattr(stmt, 'parsed') and stmt.parsed:
                    # This might contain the actual statement data
                    if dukeconfig.debug: print("  UserStatement parsed: {}".format(stmt.parsed))
            
            # NOTE: You could add more analysis here for game-specific statements

            
            # Handle unknown but potentially important statements
            else:
                if dukeconfig.debug: print("  Unknown statement type: {}".format(type(stmt)))
                class_name = stmt.__class__.__name__ if hasattr(stmt, '__class__') else 'Unknown'
                
                # Only include potentially important unknown statements
                if class_name not in ['UserStatement', 'Pass', 'Label', 'Menu']:
                    # Try to extract useful information
                    info_found = False
                    for attr in ['target', 'label', 'expression', 'name']:
                        if hasattr(stmt, attr):
                            value = getattr(stmt, attr)
                            if value and not str(value).startswith('_'):
                                if dukeconfig.debug: print("  Statement has {}: {}".format(attr, value))
                                consequences.append(('unknown', '{}: {}'.format(attr, str(value)), '', '{} {}'.format(class_name.lower(), value)))
                                info_found = True
                                break
                    
                    if not info_found:
                        consequences.append(('unknown', class_name, '', class_name.lower()))
        
        if dukeconfig.debug: print("Total meaningful consequences found: {}".format(len(consequences)))
        for i, consequence in enumerate(consequences):
            if len(consequence) >= 4:
                action_type, content, value, full_code = consequence
                if dukeconfig.debug: print("  Consequence {}: {} - {} {} | Code: {}".format(i, action_type, repr(content), repr(value), repr(full_code)))
            else:
                if dukeconfig.debug: print("  Consequence {}: {}".format(i, consequence))
        

        cache_consequences(choice_block_id, consequences)
        return consequences


    def get_memory_usage_info():
        """Get current memory usage of the walkthrough system"""
        import sys
        
        registry_size = len(menu_registry)
        cache_size = len(consequence_cache)
        weakref_size = len(menu_node_weakrefs)
        
        # Estimate memory usage (rough approximation)
        registry_memory = sys.getsizeof(menu_registry) + sum(sys.getsizeof(k) + sys.getsizeof(v) for k, v in menu_registry.items())
        cache_memory = sys.getsizeof(consequence_cache) + sum(sys.getsizeof(k) + sys.getsizeof(v) for k, v in consequence_cache.items())
        
        return {
            'registry_entries': registry_size,
            'cache_entries': cache_size,
            'weakref_entries': weakref_size,
            'estimated_registry_memory': registry_memory,
            'estimated_cache_memory': cache_memory,
            'total_estimated_memory': registry_memory + cache_memory
        }

    def log_memory_usage():
        """Log current memory usage for debugging"""
        if dukeconfig.debug:
            info = get_memory_usage_info()
            print("=== WALKTHROUGH MEMORY USAGE ===")
            print("Registry entries: {}".format(info['registry_entries']))
            print("Cache entries: {}".format(info['cache_entries']))
            print("Estimated total memory: {:.1f} KB".format(info['total_estimated_memory'] / 1024))
    
    def format_consequences(consequences):
        """Format consequences for display - UNIVERSAL with better arrow support"""
        if dukeconfig.debug: print("=== UNIVERSAL FORMATTER ===")
        if dukeconfig.debug: print("Input consequences:", len(consequences))
        
        if not consequences:
            if dukeconfig.debug: print("No consequences to format")
            return ""
        
        formatted = []
        colors = {
            'increase': '#4f4',      # Green for increases
            'decrease': '#f44',      # Red for decreases
            'assign': '#44f',        # Blue for assignments
            'boolean': '#4af',       # Light blue for boolean
            'jump': '#f84',          # Orange for jumps
            'call': '#8f4',          # Light green for calls
            'return': '#f48',        # Pink for returns
            'function': '#af4',      # Yellow-green for functions
            'condition': '#ff8',     # Yellow for conditionals
            'code': '#ccc',          # Gray for generic code
            'unknown': '#f8f'        # Magenta for unknown
        }
        
        # Define arrow symbols with fallbacks
        arrows = {
            'jump': "{font=DejaVuSans.ttf}➤{/font}",      # Force emoji font
            'call': "{font=TwemojiCOLRv0.ttf}📞{/font}",  # Force emoji font
            'return': "{font=DejaVuSans.ttf}↩{/font}",    # Force emoji font
            'function': "{font=TwemojiCOLRv0.ttf}🔧{/font}", # Force emoji font
            'condition': "{font=TwemojiCOLRv0.ttf}❓{/font}",  # Force emoji font
            'code': "{font=DejaVuSans.ttf}⚙{/font}"       # Force emoji font
        }
        
        for consequence in consequences:
            if len(consequence) >= 4:
                action_type, content, value, full_code = consequence
            elif len(consequence) >= 3:
                action_type, content, value = consequence
                full_code = ''
            else:
                action_type, content = consequence[0], consequence[1]
                value, full_code = '', ''
                
            color = colors.get(action_type, '#fff')
            if dukeconfig.debug: print("Processing consequence: {} - {} {} | {}".format(action_type, repr(content), repr(value), repr(full_code)))
            
            if action_type == 'increase':
                if value and value != '1' and value != '?':
                    formatted.append("{color=" + color + "}+" + str(content) + " (+" + str(value) + "){/color}")
                else:
                    formatted.append("{color=" + color + "}+" + str(content) + "{/color}")
                    
            elif action_type == 'decrease':
                if value and value != '1' and value != '?':
                    formatted.append("{color=" + color + "}-" + str(content) + " (-" + str(value) + "){/color}")
                else:
                    formatted.append("{color=" + color + "}-" + str(content) + "{/color}")
                    
            elif action_type == 'assign':
                if len(str(value)) > 15:
                    formatted.append("{color=" + color + "}" + str(content) + " = " + str(value)[:12] + "...{/color}")
                else:
                    formatted.append("{color=" + color + "}" + str(content) + " = " + str(value) + "{/color}")
                    
            elif action_type == 'boolean':
                formatted.append("{color=" + color + "}" + str(content) + " = " + str(value) + "{/color}")
                
            elif action_type == 'jump':
                arrow = arrows.get('jump', '>')
                formatted.append("{color=" + color + "}" + arrow + " " + str(content) + "{/color}")
                
            elif action_type == 'call':
                arrow = arrows.get('call', 'CALL')
                formatted.append("{color=" + color + "}" + arrow + " " + str(content) + "{/color}")
                
            elif action_type == 'return':
                arrow = arrows.get('return', '<-')
                if value and str(value) != 'end':
                    formatted.append("{color=" + color + "}" + arrow + " " + str(value) + "{/color}")
                else:
                    formatted.append("{color=" + color + "}" + arrow + " End{/color}")
                    
            elif action_type == 'function':
                arrow = arrows.get('function', 'FN')
                if full_code and len(full_code) <= 30:
                    formatted.append("{color=" + color + "}" + arrow + " " + str(full_code) + "{/color}")
                elif value and len(str(value)) <= 25:
                    formatted.append("{color=" + color + "}" + arrow + " " + str(value) + "{/color}")
                else:
                    decrypted_code = renpy.python.quote_eval(full_code) if full_code else 'Function'
                    formatted.append("{color=" + color + "}" + arrow + " " + decrypted_code + "{/color}")
                    
            elif action_type == 'condition':
                arrow = arrows.get('condition', '?')
                formatted.append("{color=" + color + "}" + arrow + " Conditional{/color}")
                
            elif action_type == 'code':
                arrow = arrows.get('code', 'CODE')
                if full_code and len(full_code) <= 25:
                    formatted.append("{color=" + color + "}" + arrow + " " + str(full_code) + "{/color}")
                elif value and len(str(value)) <= 20:
                    formatted.append("{color=" + color + "}" + arrow + " " + str(value) + "{/color}")
                else:
                    formatted.append("{color=" + color + "}" + arrow + " Code{/color}")
                    
            else:
                formatted.append("{color=" + color + "}" + str(content)[:20] + "{/color}")
        
        # Prioritize important consequences for display
        high_priority = []
        medium_priority = []
        low_priority = []
        
        for item in formatted:
            item_lower = item.lower()
            if any(keyword in item_lower for keyword in ['trust', 'love', 'relationship', 'affection', 'points', 'money', 'health', 'reputation', '➤', '📞']): # NOTE: You can add more on your own
                high_priority.append(item)
            elif any(keyword in item_lower for keyword in ['=', '+', '-', '↩', 'true', 'false', '🔧', '⚙']):
                medium_priority.append(item)
            else:
                low_priority.append(item)
        
        # Show most important consequences first, limit to avoid clutter
        final_consequences = high_priority[:3] + medium_priority[:2]
        
        # If we still don't have enough important info, add some low priority
        if len(final_consequences) < 2:
            final_consequences.extend(low_priority[:2])
        
        # Limit total consequences to avoid overwhelming the player
        if len(final_consequences) > 4:
            final_consequences = final_consequences[:4]
        
        result = " | ".join(final_consequences)
        if dukeconfig.debug: print("Final formatted result: {}".format(repr(result)))
        return result


    def create_current_execution_fingerprint():
        """Create fingerprint of current execution context"""
        try:
            ctx = renpy.game.context()
            current_pos = ctx.current
            if not current_pos:
                return tuple()
            
            fingerprint = []
            script = renpy.game.script
            current_line = current_pos[2] if len(current_pos) > 2 else 0
            
            # Look at nearby statements
            for offset in [-2, -1, 1, 2]:
                try:
                    target_line = current_line + offset
                    for node_key, node in script.namemap.items():
                        if hasattr(node, 'linenumber') and node.linenumber == target_line:
                            fingerprint.append(node.__class__.__name__)
                            break
                except:
                    pass
            
            return tuple(fingerprint)
        except:
            return tuple()

    def calculate_fingerprint_similarity(fp1, fp2):
        """Calculate similarity between two fingerprints"""
        if not fp1 or not fp2:
            return 0.0
        
        matches = 0
        total = max(len(fp1), len(fp2))
        
        for item in fp1:
            if item in fp2:
                matches += 1
        
        return float(matches) / total if total > 0 else 0.0

    def create_menu_fingerprint(menu_node):
        """Create a unique fingerprint for a menu based on surrounding statements"""
        fingerprint = []
        
        if hasattr(menu_node, 'linenumber'):
            # Get statements before and after the menu
            script = renpy.game.script
            for offset in [-3, -2, -1, 1, 2, 3]:  # Look 3 lines before/after
                try:
                    nearby_line = menu_node.linenumber + offset
                    # Find statement at this line and add to fingerprint
                    for node_key, node in script.namemap.items():
                        if hasattr(node, 'linenumber') and node.linenumber == nearby_line:
                            fingerprint.append(node.__class__.__name__)
                            break
                except:
                    pass
        
        return tuple(fingerprint)  # Immutable fingerprint

    def match_by_fingerprint(items, menu_nodes):
        """Match menu by comparing execution context fingerprints"""
        current_fingerprint = create_current_execution_fingerprint()
        
        best_match = None
        best_similarity = 0
        
        for node in menu_nodes:
            node_fingerprint = create_menu_fingerprint(node)
            similarity = calculate_fingerprint_similarity(current_fingerprint, node_fingerprint)
            
            if similarity > best_similarity:
                best_similarity = similarity
                best_match = node
        
        return best_match if best_similarity > 0.7 else None


    menu_registry = {}
    menu_registry_access_times = {}  # Track when entries were last accessed
    MAX_REGISTRY_SIZE = 500  # Limit registry size
    REGISTRY_CLEANUP_SIZE = 100  # How many to remove during cleanup

    def cleanup_menu_registry():
        """Clean up old entries from menu registry to prevent memory leaks"""
        if len(menu_registry) > MAX_REGISTRY_SIZE:
            if dukeconfig.debug: print("Registry cleanup: {} entries, removing oldest {}".format(len(menu_registry), REGISTRY_CLEANUP_SIZE))
            
            # Sort by access time (LRU - Least Recently Used)
            sorted_items = sorted(menu_registry_access_times.items(), key=lambda x: x[1])
            
            # Remove oldest entries
            for i in range(min(REGISTRY_CLEANUP_SIZE, len(sorted_items))):
                key_to_remove = sorted_items[i][0]
                if key_to_remove in menu_registry:
                    del menu_registry[key_to_remove]
                del menu_registry_access_times[key_to_remove]
            
            if dukeconfig.debug: print("Registry after cleanup: {} entries".format(len(menu_registry)))

    def register_menu_at_runtime(items, menu_node):
        """Register menu when first encountered"""

        # Cleanup if needed before adding new entry
        cleanup_menu_registry()
        
        ctx = renpy.game.context()
        current_pos = ctx.current
        
        if current_pos:
            file_name = current_pos[0]
            line_num = current_pos[2] if len(current_pos) > 2 else 0
            
            # Create composite key
            menu_key = (file_name, line_num, len(items), tuple(item[0] for item in items))
            
            # Store the actual menu node for this exact context
            menu_registry[menu_key] = menu_node
            menu_registry_access_times[menu_key] = renpy.get_game_runtime()  # Track access time

            if dukeconfig.debug: print("Registered menu at {}:{} (registry size: {})".format(file_name, line_num, len(menu_registry)))

    def find_menu_from_registry(items):
        """Find menu from runtime registry"""
        ctx = renpy.game.context()
        current_pos = ctx.current
        
        if current_pos:
            file_name = current_pos[0]
            line_num = current_pos[2] if len(current_pos) > 2 else 0
            
            # Try exact match first
            exact_key = (file_name, line_num, len(items), tuple(item[0] for item in items))
            if exact_key in menu_registry:
                menu_registry_access_times[exact_key] = renpy.get_game_runtime()
                return menu_registry[exact_key]
            
            # Try fuzzy match (same file + items, close line number)
            for key, node in menu_registry.items():
                if (key[0] == file_name and key[2] == len(items) and 
                    abs(key[1] - line_num) < 100 and key[3] == tuple(item[0] for item in items)):
                    # Update access time
                    menu_registry_access_times[key] = renpy.get_game_runtime()
                    return node
        
        return None
    
    def find_correct_menu_node(items):
        """Enhanced menu finding with runtime registry and multiple strategies"""
        try:
            if dukeconfig.debug: print("=== ENHANCED MENU DETECTION ===")
            
            # Strategy 1: Check runtime registry first (fastest and most accurate)
            menu_node = find_menu_from_registry(items)
            if menu_node:
                if dukeconfig.debug: print("✓ Found menu via runtime registry")
                return menu_node
            
            # Strategy 2: Use existing proximity-based method
            menu_node = find_menu_by_proximity_and_text(items)
            if menu_node:
                if dukeconfig.debug: print("✓ Found menu via proximity and text matching")
                # Register this successful match for future use
                register_menu_at_runtime(items, menu_node)
                return menu_node
            
            # Strategy 3: Try fingerprint matching as fallback
            menu_nodes = get_all_candidate_menus(items)
            menu_node = match_by_fingerprint(items, menu_nodes)
            if menu_node:
                if dukeconfig.debug: print("✓ Found menu via fingerprint matching")
                register_menu_at_runtime(items, menu_node)
                return menu_node
            
            if dukeconfig.debug: print("✗ No suitable menu node found")
            return None
            
        except Exception as e:
            if dukeconfig.debug: print("Error in enhanced menu detection: {}".format(e))
            return None

    def get_all_candidate_menus(items):
        """Get all menus that could potentially match"""
        menu_nodes = []
        script = renpy.game.script
        
        for node_key, node in script.namemap.items():
            if (hasattr(node, '__class__') and node.__class__.__name__ == 'Menu' and
                hasattr(node, 'items') and len(node.items) == len(items)):
                menu_nodes.append(node)
        
        return menu_nodes

    def find_menu_by_proximity_and_text(items):
        """Your existing proximity + text matching logic (extracted as separate function)"""
        # Get current execution position
        ctx = renpy.game.context()
        current_position = ctx.current
        
        if not current_position:
            return None

        script = renpy.game.script
        current_file = current_position[0]
        current_line = current_position[2] if len(current_position) > 2 else 0
        
        if dukeconfig.debug: print("Looking for menu nodes in file: {}".format(current_file))
        if dukeconfig.debug: print("Current line: {}".format(current_line))
        if dukeconfig.debug: print("Expected items count: {}".format(len(items)))
        
        # Enhanced file matching for compiled games
        menu_nodes = []
        current_file_base = current_file.replace('.rpyc', '.rpy').replace('.rpa', '.rpy')
        
        # Method 1: Look for exact filename matches
        for node_key, node in script.namemap.items():
            if (hasattr(node, '__class__') and node.__class__.__name__ == 'Menu' and
                hasattr(node, 'filename')):
                
                node_file = node.filename
                node_file_base = node_file.replace('.rpyc', '.rpy').replace('.rpa', '.rpy') if node_file else ''
                
                # Try multiple matching strategies
                if (node_file == current_file or 
                    node_file_base == current_file_base or
                    node_file_base.endswith(current_file_base.split('/')[-1]) or
                    current_file_base.endswith(node_file_base.split('/')[-1])):
                    
                    menu_nodes.append(node)
                    if dukeconfig.debug: print("Found menu node at line: {} with {} items (file: {})".format(
                        getattr(node, 'linenumber', 'unknown'), 
                        len(getattr(node, 'items', [])),
                        node_file))
        
        # Method 2: If no exact matches, search by proximity and item count
        if not menu_nodes:
            if dukeconfig.debug: print("No exact file matches, searching all menu nodes...")
            all_menu_nodes = []
            
            for node_key, node in script.namemap.items():
                if (hasattr(node, '__class__') and node.__class__.__name__ == 'Menu' and
                    hasattr(node, 'items') and len(node.items) == len(items)):
                    all_menu_nodes.append(node)
                    if dukeconfig.debug: print("Found potential menu node with {} items".format(len(node.items)))
            
            menu_nodes = all_menu_nodes
        
        # Method 3: Try to match by item text content
        best_match = None
        best_score = 0
        
        for node in menu_nodes:
            if hasattr(node, 'items') and len(node.items) == len(items):
                score = 0
                
                # Compare item texts
                for i in range(min(len(node.items), len(items))):
                    if len(node.items[i]) > 0 and len(items[i]) > 0:
                        node_text = str(node.items[i][0]) if node.items[i][0] else ""
                        item_text = str(items[i][0]) if items[i][0] else ""
                        
                        # Clean texts for comparison (remove renpy markup)
                        import re
                        clean_node_text = re.sub(r'\{[^}]*\}', '', node_text).strip()
                        clean_item_text = re.sub(r'\{[^}]*\}', '', item_text).strip()
                        
                        if clean_node_text == clean_item_text:
                            score += 10
                        elif clean_node_text.lower() == clean_item_text.lower():
                            score += 8
                        elif clean_node_text in clean_item_text or clean_item_text in clean_node_text:
                            score += 5
                        
                        if dukeconfig.debug: print("Comparing '{}' vs '{}' (score: {})".format(
                            clean_node_text[:30], clean_item_text[:30], score))
                
                if score > best_score:
                    best_score = score
                    best_match = node
                    if dukeconfig.debug: print("New best match with score: {}".format(score))
        
        # Method 4: If we have a good text match, use it
        if best_match and best_score >= 10:
            if best_score == 20:  # Perfect match on both items
                # Find all perfect matches and pick the closest one
                perfect_matches = []
                for node in menu_nodes:
                    if hasattr(node, 'items') and len(node.items) == len(items):
                        score = 0
                        for i in range(min(len(node.items), len(items))):
                            if len(node.items[i]) > 0 and len(items[i]) > 0:
                                node_text = str(node.items[i][0]) if node.items[i][0] else ""
                                item_text = str(items[i][0]) if items[i][0] else ""
                                import re
                                clean_node_text = re.sub(r'\{[^}]*\}', '', node_text).strip()
                                clean_item_text = re.sub(r'\{[^}]*\}', '', item_text).strip()
                                if clean_node_text == clean_item_text:
                                    score += 10
                        if score == 20:  # Perfect match
                            perfect_matches.append(node)
                
                # From perfect matches, pick the closest to current line
                if len(perfect_matches) > 1:
                    best_distance = float('inf')
                    closest_match = None
                    for node in perfect_matches:
                        if hasattr(node, 'linenumber'):
                            distance = abs(node.linenumber - current_line)
                            if distance < best_distance:
                                best_distance = distance
                                closest_match = node
                                if dukeconfig.debug: print("Perfect match at line {} (distance: {})".format(node.linenumber, distance))
                    
                    if closest_match:
                        best_match = closest_match
                        if dukeconfig.debug: print("Selected closest perfect match at line {} (distance: {})".format(closest_match.linenumber, best_distance))
            
            if dukeconfig.debug: print("Selected menu node by text matching (score: {})".format(best_score))
            return best_match
        
        # Method 5: Fallback to line proximity if we have potential nodes
        if menu_nodes:
            best_node = None
            best_distance = float('inf')
            
            for node in menu_nodes:
                if hasattr(node, 'linenumber'):
                    distance = abs(node.linenumber - current_line)
                    if distance < best_distance:
                        best_distance = distance
                        best_node = node
                        if dukeconfig.debug: print("Node at line {} (distance: {})".format(node.linenumber, distance))
            
            if best_node:
                if dukeconfig.debug: print("Selected menu node by line proximity (distance: {})".format(best_distance))
                return best_node
        
        # Method 6: Last resort - find ANY menu node with matching item count
        if dukeconfig.debug: print("Last resort: searching for any menu with {} items...".format(len(items)))
        for node_key, node in script.namemap.items():
            if (hasattr(node, '__class__') and node.__class__.__name__ == 'Menu' and
                hasattr(node, 'items') and len(node.items) == len(items)):
                if dukeconfig.debug: print("Found fallback menu node with matching item count")
                return node
        
        return None


    cleanup_counter = 0
    CLEANUP_INTERVAL = 100  # Clean up every 100 menu calls

    # Hook the menu function - UNIVERSAL for all Ren'Py games
    if hasattr(renpy.exports, 'menu'):
        original_menu = renpy.exports.menu
        
        def universal_walkthrough_menu(items, set=None, args=None, kwargs=None, item_arguments=None):
            """Universal walkthrough menu function for any Ren'Py game"""
            global cleanup_counter
            
            if dukeconfig.debug: print("=== UNIVERSAL WALKTHROUGH MENU ===")
            # Periodic memory cleanup
            cleanup_counter += 1
            if cleanup_counter >= CLEANUP_INTERVAL:
                cleanup_counter = 0
                cleanup_menu_registry()
                
                # Also clean up consequence cache
                if len(consequence_cache) > MAX_CONSEQUENCE_CACHE:
                    if dukeconfig.debug: print("Cleaning up consequence cache")
                    sorted_cache = sorted(consequence_cache_access.items(), key=lambda x: x[1])
                    for i in range(50):  # Remove 50 oldest entries
                        if i < len(sorted_cache):
                            old_key = sorted_cache[i][0]
                            if old_key in consequence_cache:
                                del consequence_cache[old_key]
                            if old_key in consequence_cache_access:
                                del consequence_cache_access[old_key]
                
                # Log memory usage every cleanup
                log_memory_usage()

            if dukeconfig.debug: print("Items received:", len(items) if items else 0)


            # NOTE: Add file type and script debugging
            if dukeconfig.debug: 
                print("=== SCRIPT DEBUG INFO ===")
                ctx = renpy.game.context()
                if ctx and ctx.current:
                    filename = ctx.current[0]
                    print("Current file: {}".format(filename))
                    print("File type: {}".format('rpyc' if filename.endswith('.rpyc') else 'rpy' if filename.endswith('.rpy') else 'other'))
                
                # Count total menu nodes in script
                menu_count = 0
                for node_key, node in renpy.game.script.namemap.items():
                    if hasattr(node, '__class__') and node.__class__.__name__ == 'Menu':
                        menu_count += 1
                print("Total menu nodes in script: {}".format(menu_count))
                
                # Show first few items for debugging
                if items:
                    for i, item in enumerate(items[:2]):  # Show first 2 items
                        print("Item {}: {}".format(i, repr(item[0]) if len(item) > 0 else 'empty'))
            
            
            # Check if walkthrough is enabled (create settings if they don't exist)
            if not hasattr(persistent, 'universal_walkthrough_enabled'):
                persistent.universal_walkthrough_enabled = True
            
            if not persistent.universal_walkthrough_enabled:
                if dukeconfig.debug: print("Universal walkthrough disabled, calling original menu")
                return original_menu(items, set, args, kwargs, item_arguments)
            
            try:
                # Find the correct menu node for these specific items
                menu_node = find_correct_menu_node(items)
                if dukeconfig.debug: print("Found menu node: {}".format(menu_node is not None))
                
                if menu_node and hasattr(menu_node, 'items'):
                    if dukeconfig.debug: print("Menu node has {} items".format(len(menu_node.items)))
                    enhanced_items = []
                    
                    for i, (caption, condition, value) in enumerate(items):
                        enhanced_caption = caption
                        
                        # Get corresponding menu choice from AST
                        if i < len(menu_node.items):
                            menu_choice = menu_node.items[i]
                            if dukeconfig.debug: print("Processing menu choice {}: {}".format(i, type(menu_choice)))
                            
                            if len(menu_choice) >= 3 and menu_choice[2]:
                                choice_block = menu_choice[2]
                                if dukeconfig.debug: print("Found choice block for choice {}: {}".format(i, type(choice_block)))
                                consequences = extract_choice_consequences(choice_block)
                                
                                if consequences:
                                    formatted_consequences = format_consequences(consequences)
                                    if dukeconfig.debug: print("Adding WT for choice {}: {}".format(i, formatted_consequences))
                                    enhanced_caption += "\n{{size={}}}{{color=#888}}WT:{{/color}} ".format(persistent.universal_wt_text_size if hasattr(persistent, 'universal_wt_text_size') else 16) + formatted_consequences + "{/size}"
                                else:
                                    if dukeconfig.debug: print("No consequences found for choice {}".format(i))
                            else:
                                if dukeconfig.debug: print("No choice block for choice {}".format(i))
                        
                        enhanced_items.append((enhanced_caption, condition, value))
                    
                    if dukeconfig.debug: print("Calling original menu with enhanced items")
                    return original_menu(enhanced_items, set, args, kwargs, item_arguments)
                else:
                    if dukeconfig.debug: print("No menu node found or node has no items")
            
            except RENPY_CONTROL_EXCEPTIONS:
                # Re-raise Ren'Py control flow exceptions - these are NOT errors!
                raise
                
            except Exception as e:
                if dukeconfig.debug: print("Error in universal_walkthrough_menu:", e)
                import traceback
                traceback.print_exc()
            
            # Fallback to original
            if dukeconfig.debug: print("Falling back to original menu")
            return original_menu(items, set, args, kwargs, item_arguments)
        
        renpy.exports.menu = universal_walkthrough_menu
        if dukeconfig.debug: print("Universal walkthrough menu hook installed")


    # Clear caches on game quit
    def on_quit_game():
        """Clear volatile caches"""
        global consequence_cache, consequence_cache_access
        consequence_cache.clear()
        consequence_cache_access.clear()
        if dukeconfig.debug: print("Cleared consequence cache on quit")

    config.quit_callbacks.append(on_quit_game)

    # Set default persistent values
    if not hasattr(persistent, 'universal_walkthrough_enabled'):
        persistent.universal_walkthrough_enabled = True
        if dukeconfig.debug: print("Set universal_walkthrough_enabled to True")
    
    print("Universal Ren'Py Walkthrough System v1.0 Loaded")


screen universal_walkthrough_preferences():
    modal True
    
    frame:
        background Color("#222")
        xalign 0.5
        yalign 0.5
        vbox:
            xalign 0.5
            text "Universal Walkthrough Settings" size 24
            
            textbutton "Enable Walkthrough: {}".format("ON" if persistent.universal_walkthrough_enabled else "OFF"):
                action ToggleVariable("persistent.universal_walkthrough_enabled")
            
            text "Text Size: {}".format(persistent.universal_wt_text_size)
            hbox:
                textbutton "-" action SetVariable("persistent.universal_wt_text_size", max(12, persistent.universal_wt_text_size - 2))
                textbutton "+" action SetVariable("persistent.universal_wt_text_size", min(40, persistent.universal_wt_text_size + 2))
            
            # Memory management options
            text "Memory Usage: {} entries".format(len(menu_registry) + len(consequence_cache))
            
            textbutton "Clear Cache" action Function(lambda: (menu_registry.clear(), consequence_cache.clear()))
            
            if dukeconfig.debug:
                textbutton "Show Memory Info" action Function(log_memory_usage)
            
            textbutton "Close" action ToggleScreen("universal_walkthrough_preferences")

init 999 python:
    config.underlay.append(
        renpy.Keymap(
            alt_K_w = lambda: renpy.run(ToggleScreen("universal_walkthrough_preferences"))
        )
    )