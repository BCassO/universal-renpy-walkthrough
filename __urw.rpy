############################################################
######### Universal Walkthrough System v1.1 ################
#########      (C) Knox Emberlyn 2025       ################
############################################################
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
##   2. Change line 40: debug = False  ->  debug = True  
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
    debug = False

init -998 python:
    import collections.abc
    import builtins
    import re
    import weakref


    def urwmsg(*args, **kwargs):
        if dukeconfig.debug:
            print(*args, **kwargs)
    urwmsg("=== AVAILABLE RENPY AST CLASSES ===")
    ast_classes = [attr for attr in dir(renpy.ast) if not attr.startswith('_')]
    audio_visual_classes = [cls for cls in ast_classes if any(keyword in cls.lower() for keyword in ['play', 'stop', 'music', 'sound', 'audio', 'queue'])]
    urwmsg("Audio/Visual AST classes:", audio_visual_classes)
    
    all_statement_classes = [cls for cls in ast_classes if cls[0].isupper()]
    urwmsg("All statement classes:", all_statement_classes)

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
            urwmsg("Using cached consequences for block {}".format(choice_block_id))
            return cached_result
        
        urwmsg("=== UNIVERSAL WALKTHROUGH ANALYZER ===")
        urwmsg("Choice block type:", type(choice_block))
        
        consequences = []
        statements = []
        
        # Handle both list format and block format
        if isinstance(choice_block, collections.abc.Sequence) and not isinstance(choice_block, (str, bytes)):
            statements = choice_block
            urwmsg("Processing choice block as sequence with {} statements".format(len(statements)))
        elif hasattr(choice_block, 'children'):
            statements = choice_block.children
            urwmsg("Processing choice block with children attribute")
        elif choice_block is None:
            urwmsg("Choice block is None, returning empty consequences")
            return consequences
        else:
            urwmsg("Unknown choice block format: {}, returning empty consequences".format(type(choice_block)))
            return consequences
        
        if not statements:
            urwmsg("No statements found in the choice block")
            return consequences
            
        urwmsg("Number of statements:", len(statements))
        
        # Process each statement to extract consequences
        for i, stmt in enumerate(statements):
            urwmsg("Statement {}: {}".format(i, type(stmt)))
            
            try:
                if isinstance(stmt, renpy.ast.Python):
                    consequences.extend(analyze_python_statement_enhanced(stmt))
                
                elif isinstance(stmt, renpy.ast.Jump):
                    consequences.append(('jump', stmt.target, '', f'→ {stmt.target}'))
                
                elif isinstance(stmt, renpy.ast.Call):
                    consequences.append(('call', stmt.label, '', f'📞 {stmt.label}'))
                
                elif isinstance(stmt, renpy.ast.Return):
                    expr = stmt.expression if stmt.expression else 'end'
                    consequences.append(('return', str(expr), '', f'↩ {expr}'))
                
                elif isinstance(stmt, renpy.ast.If):
                    # Analyze conditional consequences
                    for condition, block in stmt.entries:
                        sub_consequences = extract_choice_consequences(block)
                        if sub_consequences:
                            consequences.append(('condition', f'If {condition}', str(len(sub_consequences)), f'❓ Conditional'))
                
                elif isinstance(stmt, renpy.ast.Say):
                    urwmsg("  Skipping Say statement")
                    continue
                elif isinstance(stmt, renpy.ast.Scene):
                    urwmsg("  Skipping Scene statement")
                    continue
                elif isinstance(stmt, renpy.ast.Show):
                    urwmsg("  Skipping Show statement")
                    continue
                elif isinstance(stmt, renpy.ast.Hide):
                    urwmsg("  Skipping Hide statement")
                    continue
                elif isinstance(stmt, renpy.ast.With):
                    urwmsg("  Skipping With statement")
                    continue
                elif isinstance(stmt, renpy.ast.ShowLayer):
                    urwmsg("  Skipping ShowLayer statement")
                    continue
                elif isinstance(stmt, renpy.ast.Camera):
                    urwmsg("  Skipping Camera statement")
                    continue
                elif isinstance(stmt, renpy.ast.Transform):
                    urwmsg("  Skipping Transform statement")
                    continue
                
                # Other non-gameplay statements to skip
                elif isinstance(stmt, renpy.ast.Pass):
                    urwmsg("  Skipping Pass statement")
                    continue
                elif isinstance(stmt, renpy.ast.Label):
                    urwmsg("  Skipping Label statement")
                    continue
                elif isinstance(stmt, renpy.ast.Menu):
                    urwmsg("  Skipping nested Menu statement")
                    continue
                elif isinstance(stmt, renpy.ast.UserStatement):
                    urwmsg("  Skipping UserStatement")
                    continue
                
                else:
                    # Handle unknown statements more safely
                    class_name = stmt.__class__.__name__
                    
                    # Skip common visual/audio statements by name (since they don't exist as AST classes)
                    if class_name in ['Play', 'Stop', 'Queue', 'Music', 'Sound', 'Voice', 'Audio']:
                        urwmsg("  Skipping audio statement by name: {}".format(class_name))
                        continue
                    
                    # Skip other non-gameplay statements
                    if class_name in ['Comment', 'Translate', 'TranslateBlock', 'EndTranslate']:
                        urwmsg("  Skipping translation statement: {}".format(class_name))
                        continue
                    
                    # Try to extract meaningful info from unknown statements
                    urwmsg("  Processing unknown statement: {}".format(class_name))
                    
                    # Look for important attributes
                    for attr in ['target', 'label', 'expression', 'name', 'value']:
                        if hasattr(stmt, attr):
                            value = getattr(stmt, attr)
                            if value and not str(value).startswith('_'):
                                consequences.append(('unknown', f'{attr}: {str(value)}', '', f'{class_name.lower()} {value}'))
                                urwmsg("    Added unknown consequence: {} {}".format(class_name, value))
                                break
                    else:
                        # Only add if it might be important (not common visual elements)
                        if class_name not in ['With', 'Scene', 'Show', 'Hide', 'Say', 'ShowLayer', 'Camera', 'Transform']:
                            consequences.append(('unknown', class_name, '', class_name.lower()))
                            urwmsg("    Added generic unknown: {}".format(class_name))
            
            except Exception as e:
                urwmsg("  Error processing statement {}: {}".format(i, e))
                # Don't let a single statement error break the whole analysis
                continue
        
        cache_consequences(choice_block_id, consequences)
        return consequences


    def analyze_python_statement_enhanced(stmt):
        """Enhanced Python statement analysis using AST parser"""
        consequences = []
        
        urwmsg("    Analyzing Python statement...")
        
        # Source code
        source = None
        if hasattr(stmt, 'code'):
            code_obj = stmt.code
            
            # Try different methods to get source
            if hasattr(code_obj, 'source'):
                source = code_obj.source
                urwmsg("    Got source via .source: {}".format(repr(source[:100] if source else None)))
            elif hasattr(code_obj, 'py'):
                source = code_obj.py
                urwmsg("    Got source via .py: {}".format(repr(source[:100] if source else None)))
            elif hasattr(code_obj, 'python'):
                source = code_obj.python
                urwmsg("    Got source via .python: {}".format(repr(source[:100] if source else None)))
        
        if source:
            # Use Python's AST parser for more accurate analysis
            urwmsg("    Using AST parser for source analysis")
            consequences.extend(parse_python_source_enhanced(source))
        else:
            # Fallback to bytecode analysis for compiled games
            urwmsg("    No source found, trying bytecode analysis")
            consequences.extend(analyze_bytecode_enhanced(stmt))
        
        urwmsg("    Python analysis result: {} consequences".format(len(consequences)))
        for i, cons in enumerate(consequences):
            urwmsg("      {}: {}".format(i, cons))
        
        return consequences

    def parse_python_source_enhanced(source):
        """Enhanced Python source parsing with AST"""
        consequences = []
        
        if not source:
            urwmsg("      No source to parse")
            return consequences
        
        urwmsg("      Parsing source: {}".format(repr(source[:200])))
        
        try:
            # First try Python's AST parser for accuracy
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    # Handle assignments
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            
                            # Try to evaluate the value
                            try:
                                if isinstance(node.value, ast.Constant):
                                    value = str(node.value.value)
                                elif hasattr(node.value, 'n'):  # Python < 3.8
                                    value = str(node.value.n)
                                elif hasattr(node.value, 's'):  # Python < 3.8
                                    value = node.value.s
                                else:
                                    value = ast.unparse(node.value) if hasattr(ast, 'unparse') else '?'
                                
                                consequences.append(('assign', var_name, value, f'{var_name} = {value}'))
                                urwmsg("        AST: Found assignment {} = {}".format(var_name, value))
                            except:
                                consequences.append(('assign', var_name, '?', f'{var_name} = ?'))
                                urwmsg("        AST: Found assignment {} = ?".format(var_name))
                
                elif isinstance(node, ast.AugAssign):
                    # Handle += -= etc.
                    if isinstance(node.target, ast.Name):
                        var_name = node.target.id
                        op = node.op.__class__.__name__
                        
                        try:
                            if isinstance(node.value, ast.Constant):
                                value = str(node.value.value)
                            else:
                                value = '?'
                            
                            if op == 'Add':
                                consequences.append(('increase', var_name, value, f'{var_name} += {value}'))
                                urwmsg("        AST: Found increase {} += {}".format(var_name, value))
                            elif op == 'Sub':
                                consequences.append(('decrease', var_name, value, f'{var_name} -= {value}'))
                                urwmsg("        AST: Found decrease {} -= {}".format(var_name, value))
                        except:
                            consequences.append(('modify', var_name, '?', f'{var_name} {op}= ?'))
                            urwmsg("        AST: Found modify {} {}= ?".format(var_name, op))
        
        except SyntaxError as e:
            urwmsg("      AST parsing failed: {}, falling back to regex".format(e))
            # Fallback to regex-based parsing
            pass
        except Exception as e:
            urwmsg("      AST parsing error: {}, falling back to regex".format(e))
            pass
        
        # Always try regex parsing as well, since AST might miss some cases
        regex_consequences = parse_with_regex_fallback(source)
        consequences.extend(regex_consequences)
        
        urwmsg("      Total consequences found: {}".format(len(consequences)))
        
        return consequences

    def analyze_bytecode_enhanced(stmt):
        """Enhanced bytecode analysis for compiled games"""
        consequences = []
        
        urwmsg("      Analyzing bytecode...")
        
        try:
            import dis
            
            # Try to get the code object
            code_obj = None
            if hasattr(stmt, 'code'):
                if hasattr(stmt.code, 'py'):
                    code_obj = stmt.code.py
                elif hasattr(stmt.code, 'bytecode'):
                    code_obj = stmt.code.bytecode
                else:
                    code_obj = stmt.code
            
            if code_obj and hasattr(code_obj, 'co_code'):
                urwmsg("        Disassembling bytecode...")
                instructions = list(dis.get_instructions(code_obj))
                
                for i, instr in enumerate(instructions):
                    if instr.opname in ['STORE_NAME', 'STORE_GLOBAL', 'STORE_FAST']:
                        var_name = instr.argval
                        
                        # Check previous instruction for operation type
                        if i > 0:
                            prev_instr = instructions[i-1]
                            if prev_instr.opname == 'INPLACE_ADD':
                                consequences.append(('increase', var_name, '?', f'compiled: {var_name} += ?'))
                                urwmsg("        Bytecode: Found increase {}".format(var_name))
                            elif prev_instr.opname == 'INPLACE_SUBTRACT':
                                consequences.append(('decrease', var_name, '?', f'compiled: {var_name} -= ?'))
                                urwmsg("        Bytecode: Found decrease {}".format(var_name))
                            elif prev_instr.opname in ['LOAD_CONST', 'LOAD_FAST']:
                                # Try to get the constant value
                                if prev_instr.opname == 'LOAD_CONST' and prev_instr.argval is not None:
                                    value = str(prev_instr.argval)
                                    consequences.append(('assign', var_name, value, f'compiled: {var_name} = {value}'))
                                    urwmsg("        Bytecode: Found assignment {} = {}".format(var_name, value))
                                else:
                                    consequences.append(('assign', var_name, '?', f'compiled: {var_name} = ?'))
                                    urwmsg("        Bytecode: Found assignment {} = ?".format(var_name))
            else:
                urwmsg("        No usable code object found")
        
        except Exception as e:
            urwmsg("        Bytecode analysis failed: {}".format(e))
            consequences.append(('code', 'Python statement', '', 'Python code executed'))
        
        return consequences

    def parse_with_regex_fallback(source):
        """Fallback regex parsing"""
        consequences = []
        
        code_lines = [line.strip() for line in source.split('\n') if line.strip()]
        
        for line in code_lines:
            urwmsg("    Analyzing line: {}".format(repr(line)))
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
                        urwmsg("    Added increase: {} += {} (full line: {})".format(clean_var, actual_value, line))
                    except:
                        consequences.append(('increase', clean_var, '?', line))
                        urwmsg("    Added increase: {} += ? (full line: {})".format(clean_var, line))
                except:
                    consequences.append(('code', 'Variable increase', '', line))
                    urwmsg("    Added generic increase code: {}".format(line))

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
                        urwmsg("    Added decrease: {} -= {} (full line: {})".format(clean_var, actual_value, line))
                    except:
                        consequences.append(('decrease', clean_var, '?', line))
                        urwmsg("    Added decrease: {} -= ? (full line: {})".format(clean_var, line))
                except:
                    consequences.append(('code', 'Variable decrease', '', line))
                    urwmsg("    Added generic decrease code: {}".format(line))

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
                                urwmsg("    Added assignment: {} = {} (full line: {})".format(clean_var, display_value, line))
                            else:
                                urwmsg("    Skipped renpy.pause assignment: {}".format(line))
                    except:
                        consequences.append(('code', 'Variable assignment', '', line))
                        urwmsg("    Added generic assignment code: {}".format(line))

            # Handle special patterns
            else:
                # Check for boolean assignments
                if any(keyword in line.lower() for keyword in [' = true', ' = false']):
                    try:
                        var_name = line.split('=')[0].strip()
                        value_part = line.split('=')[1].strip()
                        clean_var = re.sub(r'\[.*?\]', '', var_name)

                        consequences.append(('boolean', clean_var, value_part, line))
                        urwmsg("    Added boolean: {} = {} (full line: {})".format(clean_var, value_part, line))
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
                        'renpy.transition',
                        'renpy.end_replay'
                    ]

                    # Check if this is a function we should ignore
                    should_ignore = False
                    for ignore_func in ignore_functions:
                        if ignore_func in line:
                            should_ignore = True
                            urwmsg("    Skipped ignored function: {}".format(line))
                            break

                    if not should_ignore:
                        # This might be an important function call
                        consequences.append(('function', 'Function call', line[:30], line))
                        urwmsg("    Added important function call: {}".format(line))

                # Any other meaningful code (but not comments or empty lines)
                elif len(line) > 3 and not line.startswith('#') and not line.strip().startswith('renpy.'):
                    consequences.append(('code', 'Python code', line[:30], line))
                    urwmsg("    Added meaningful code: {}".format(line))
                else:
                    urwmsg("    Skipped non-meaningful line: {}".format(line))
        
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
        """For debugging"""
        if dukeconfig.debug:
            info = get_memory_usage_info()
            print("=== WALKTHROUGH MEMORY USAGE ===")
            print("Registry entries: {}".format(info['registry_entries']))
            print("Cache entries: {}".format(info['cache_entries']))
            print("Estimated total memory: {:.1f} KB".format(info['total_estimated_memory'] / 1024))
    
    def format_consequences(consequences):
        """Format consequences for display - UNIVERSAL with better arrow support"""
        urwmsg("=== UNIVERSAL FORMATTER ===")
        urwmsg("Input consequences:", len(consequences))
        
        if not consequences:
            urwmsg("No consequences to format")
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
        
        # Arrow symbols with fallbacks
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
            urwmsg("Processing consequence: {} - {} {} | {}".format(action_type, repr(content), repr(value), repr(full_code)))
            
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
        urwmsg("Final formatted result: {}".format(repr(result)))
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
            urwmsg("Registry cleanup: {} entries, removing oldest {}".format(len(menu_registry), REGISTRY_CLEANUP_SIZE))
            
            # Sort by access time (LRU - Least Recently Used)
            sorted_items = sorted(menu_registry_access_times.items(), key=lambda x: x[1])
            
            # Remove oldest entries
            for i in range(min(REGISTRY_CLEANUP_SIZE, len(sorted_items))):
                key_to_remove = sorted_items[i][0]
                if key_to_remove in menu_registry:
                    del menu_registry[key_to_remove]
                del menu_registry_access_times[key_to_remove]
            
            urwmsg("Registry after cleanup: {} entries".format(len(menu_registry)))

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

            urwmsg("Registered menu at {}:{} (registry size: {})".format(file_name, line_num, len(menu_registry)))

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
            urwmsg("=== ENHANCED MENU DETECTION ===")
            
            # Strategy 1: Check runtime registry first (fastest and most accurate)
            menu_node = find_menu_from_registry(items)
            if menu_node:
                urwmsg("✓ Found menu via runtime registry")
                return menu_node
            
            # Strategy 2: Use existing proximity-based method
            menu_node = find_menu_by_proximity_and_text(items)
            if menu_node:
                urwmsg("✓ Found menu via proximity and text matching")
                register_menu_at_runtime(items, menu_node)
                return menu_node
            
            # Strategy 3: Try fingerprint matching as fallback
            menu_nodes = get_all_candidate_menus(items)
            menu_node = match_by_fingerprint(items, menu_nodes)
            if menu_node:
                urwmsg("✓ Found menu via fingerprint matching")
                register_menu_at_runtime(items, menu_node)
                return menu_node
            
            urwmsg("✗ No suitable menu node found")
            return None
            
        except Exception as e:
            urwmsg("Error in enhanced menu detection: {}".format(e))
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
        """proximity + text matching logic"""
        # Get current execution position
        ctx = renpy.game.context()
        current_position = ctx.current
        
        if not current_position:
            return None

        script = renpy.game.script
        current_file = current_position[0]
        current_line = current_position[2] if len(current_position) > 2 else 0
        
        urwmsg("Looking for menu nodes in file: {}".format(current_file))
        urwmsg("Current line: {}".format(current_line))
        urwmsg("Expected items count: {}".format(len(items)))
        
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
                    urwmsg("Found menu node at line: {} with {} items (file: {})".format(
                        getattr(node, 'linenumber', 'unknown'), 
                        len(getattr(node, 'items', [])),
                        node_file))
        
        # Method 2: If no exact matches, search by proximity and item count
        if not menu_nodes:
            urwmsg("No exact file matches, searching all menu nodes...")
            all_menu_nodes = []
            
            for node_key, node in script.namemap.items():
                if (hasattr(node, '__class__') and node.__class__.__name__ == 'Menu' and
                    hasattr(node, 'items') and len(node.items) == len(items)):
                    all_menu_nodes.append(node)
                    urwmsg("Found potential menu node with {} items".format(len(node.items)))
            
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
                        
                        urwmsg("Comparing '{}' vs '{}' (score: {})".format(
                            clean_node_text[:30], clean_item_text[:30], score))
                
                if score > best_score:
                    best_score = score
                    best_match = node
                    urwmsg("New best match with score: {}".format(score))
        
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
                                urwmsg("Perfect match at line {} (distance: {})".format(node.linenumber, distance))
                    
                    if closest_match:
                        best_match = closest_match
                        urwmsg("Selected closest perfect match at line {} (distance: {})".format(closest_match.linenumber, best_distance))
            
            urwmsg("Selected menu node by text matching (score: {})".format(best_score))
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
                        urwmsg("Node at line {} (distance: {})".format(node.linenumber, distance))
            
            if best_node:
                urwmsg("Selected menu node by line proximity (distance: {})".format(best_distance))
                return best_node
        
        # Method 6: Last resort - find ANY menu node with matching item count
        urwmsg("Last resort: searching for any menu with {} items...".format(len(items)))
        for node_key, node in script.namemap.items():
            if (hasattr(node, '__class__') and node.__class__.__name__ == 'Menu' and
                hasattr(node, 'items') and len(node.items) == len(items)):
                urwmsg("Found fallback menu node with matching item count")
                return node
        
        return None


    cleanup_counter = 0
    CLEANUP_INTERVAL = 100  # Clean up every 100 menu calls


    original_menu = renpy.exports.menu
    
    def universal_walkthrough_menu(items, set_expr=None, args=None, kwargs=None, item_arguments=None, **extra_kwargs):
        """Enhanced walkthrough menu wrapper with correct signature"""
        global cleanup_counter
        
        urwmsg("=== UNIVERSAL WALKTHROUGH MENU ===")
        urwmsg("Arguments received: items={}, set_expr={}, args={}, kwargs={}, item_arguments={}".format(len(items) if items else 0, set_expr, args, kwargs, item_arguments))
        
        
        cleanup_counter += 1
        if cleanup_counter >= CLEANUP_INTERVAL:
            cleanup_counter = 0
            cleanup_menu_registry()
            log_memory_usage()

        if not hasattr(persistent, 'universal_walkthrough_enabled'):
            persistent.universal_walkthrough_enabled = True
        
        if not persistent.universal_walkthrough_enabled:
            return original_menu(items, set_expr, args, kwargs, item_arguments)

        try:
            menu_node = find_correct_menu_node(items)
            
            if menu_node and hasattr(menu_node, 'items'):
                enhanced_items = []
                
                for i, item in enumerate(items):
                    if isinstance(item, (list, tuple)) and len(item) >= 1:
                        caption_text = item[0]
                        rest = item[1:] if len(item) > 1 else ()
                    else:
                        caption_text = str(item)
                        rest = ()
                    
                    enhanced_caption = caption_text
                    
                    if i < len(menu_node.items):
                        menu_choice = menu_node.items[i]
                        
                        if len(menu_choice) >= 3 and menu_choice[2]:
                            choice_block = menu_choice[2]
                            consequences = extract_choice_consequences(choice_block)
                            
                            if consequences:
                                formatted_consequences = format_consequences(consequences)
                                enhanced_caption += "\n{{size={}}}{{color=#888}}WT:{{/color}} ".format(
                                    persistent.universal_wt_text_size if hasattr(persistent, 'universal_wt_text_size') else 25
                                ) + formatted_consequences + "{/size}"
                    
                    if rest:
                        enhanced_items.append((enhanced_caption,) + rest)
                    else:
                        enhanced_items.append(enhanced_caption)
                
                return original_menu(enhanced_items, set_expr, args, kwargs, item_arguments)
        
        except RENPY_CONTROL_EXCEPTIONS:
            raise
        except Exception as e:
            urwmsg("Error in walkthrough menu: {}".format(e))
        
        return original_menu(items, set_expr, args, kwargs, item_arguments)
    
    # Replace the menu function
    renpy.exports.menu = universal_walkthrough_menu

    # Clear caches on game quit
    def on_quit_game():
        """Clear volatile caches"""
        global consequence_cache, consequence_cache_access
        consequence_cache.clear()
        consequence_cache_access.clear()
        urwmsg("Cleared consequence cache on quit")

    config.quit_callbacks.append(on_quit_game)

    if not hasattr(persistent, 'universal_walkthrough_enabled'):
        persistent.universal_walkthrough_enabled = True
        urwmsg("Set universal_walkthrough_enabled to True")
    
    print("Universal Ren'Py Walkthrough System v1.1 Loaded")


    
    def clear_walkthrough_caches():
        """Safely clear walkthrough caches"""
        global menu_registry, consequence_cache, consequence_cache_access, menu_node_weakrefs
        
        try:
            menu_registry.clear()
            consequence_cache.clear()
            consequence_cache_access.clear()
            menu_node_weakrefs.clear()
            
            if dukeconfig.debug: 
                print("Walkthrough caches cleared successfully")
        except Exception as e:
            if dukeconfig.debug: 
                print("Error clearing caches: {}".format(e))



style wt_toggle_button:
    background "#333"
    hover_background "#555"
    selected_background "#4a9eff"
    
style wt_size_button:
    background "#444"
    hover_background "#666"
    
style wt_preset_button:
    background "#333"
    hover_background "#6bb8ff"
    
style wt_debug_button:
    background "#ff6b6b"
    hover_background "#ff8c8c"
    color "#fff"
    xsize 100
    ysize 30
    
style wt_close_button:
    background "#4a9eff"
    hover_background "#6bb8ff"

transform wt_screen_show:
    alpha 0.0 yoffset -100
    ease 0.5 alpha 1.0 yoffset 0

transform wt_screen_hide:
    alpha 1.0 yoffset 0
    ease 0.3 alpha 0.0 yoffset -50



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
        ymaximum 500
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
                
                text "{color=#4a9eff}{size=32}{b}Universal Walkthrough System{/b}{/size}{/color}":
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        pause 0.2
                        ease 0.5 alpha 1.0
                
                text "{color=#8cc8ff}{size=18}{i}Enhance your gaming experience{/i}{/size}{/color}":
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
                            text_size 24
                            xsize 40
                            ysize 40
                            text_xalign 0.5
                        
                        frame:
                            background "#2a2a2a"
                            xsize 300
                            ysize 20
                            
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
                            text_size 24
                            xsize 40
                            ysize 40
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
            
            if dukeconfig.debug:
                vbox:
                    spacing 10
                    xalign 0.5
                    at transform:
                        alpha 0.0
                        pause 1.4
                        ease 0.4 alpha 1.0
                    
                    text "{color=#ffaa00}{size=16}{b}Debug Information{/b}{/size}{/color}":
                        xalign 0.5
                    
                    text "{color=#ccc}{size=14}Registry: [len(menu_registry)] | Cache: [len(consequence_cache)] entries{/size}{/color}":
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