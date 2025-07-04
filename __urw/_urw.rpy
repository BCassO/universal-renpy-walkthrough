####          Universal Walkthrough System v1.5            ####
####             (C) Knox Emberlyn 2025                    ####

# This file is part of the Universal Walkthrough System for Ren'Py created by Knox Emberlyn., working checkpoint

init -999:
    define persistent.universal_wt_filters = {
            'conditions': True,      # if/elif/else statements
            'jumps': True,          # jump statements  
            'calls': True,          # call statements
            'returns': True,        # return statements
            'increases': True,      # variable += operations
            'decreases': True,      # variable -= operations
            'assignments': True,    # variable = value
            'booleans': True,       # variable = True/False
            'functions': True,      # function calls
            'code': True,          # generic code blocks
            'unknown': False       # unknown statement types
        }

    define persistent.universal_wt_name_filters = {
            'hide_underscore': True,    # Hide variables starting with _
            'hide_renpy': True,         # Hide renpy.* calls
            'hide_config': False,       # Hide config.* variables
            'hide_store': True,         # Hide store.* variables
            'custom_prefix': "",        # Custom prefix to hide (user input)
            'custom_contains': ""       # Custom text to hide if contains (user input)
        }

    define persistent.universal_wt_text_size = 25
    define persistent.universal_wt_max_consequences = 2
    define persistent.universal_wt_show_all_available = True

init -999 python in dukeconfig:
    debug = False  # Set to True to enable debug messages
    developer = True

init -998 python:
    import collections.abc
    import builtins
    import re
    import weakref
    import time as _urwtime

    node_strategy_cache = {}

    def urwmsg(*args, **kwargs):
        if dukeconfig.debug:
            print(*args, **kwargs)
    

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

    
    # Caching with execution context awareness
    consequence_cache = {}
    consequence_cache_access = {}
    MAX_CONSEQUENCE_CACHE = 200

    # Execution context tracking
    menu_registry = {}
    menu_registry_access_times = {}
    MAX_REGISTRY_SIZE = 500
    REGISTRY_CLEANUP_SIZE = 100

    def get_execution_context_signature():
        """Create a unique signature for the current execution context"""
        try:
            ctx = renpy.game.context()
            if not ctx or not hasattr(ctx, 'current') or not ctx.current:
                return None
            
            current_pos = ctx.current
            filename = current_pos[0] if current_pos else None
            linenumber = current_pos[2] if len(current_pos) > 2 else 0
            
            urwmsg("RAW CONTEXT DEBUG:")
            urwmsg("  ctx.current: {}".format(ctx.current))
            urwmsg("  filename: {}".format(filename))
            urwmsg("  linenumber: {}".format(linenumber))
            
            # Try to get the actual current position from the call stack or other sources
            actual_line = linenumber
            
            # Check if we can get better position info from the script execution
            if hasattr(renpy.game, 'context'):
                game_ctx = renpy.game.context()
                if hasattr(game_ctx, 'call_stack') and game_ctx.call_stack:
                    # Try to get from call stack
                    for call_entry in reversed(game_ctx.call_stack):
                        if hasattr(call_entry, 'return_point') and call_entry.return_point:
                            potential_line = call_entry.return_point[2] if len(call_entry.return_point) > 2 else 0
                            urwmsg("  Call stack return point: {}".format(potential_line))
                            if potential_line > 0 and potential_line != linenumber:
                                actual_line = potential_line
                                break
                
                # Try alternative context sources
                if hasattr(game_ctx, 'next_node'):
                    next_node = game_ctx.next_node
                    if next_node and hasattr(next_node, 'linenumber'):
                        urwmsg("  Next node line: {}".format(next_node.linenumber))
                
                if hasattr(game_ctx, 'current_node'):
                    current_node = game_ctx.current_node
                    if current_node and hasattr(current_node, 'linenumber'):
                        urwmsg("  Current node line: {}".format(current_node.linenumber))
            
            # Try to find the actual executing menu by looking at recent script execution
            if hasattr(renpy, 'get_filename_line'):
                try:
                    debug_info = renpy.get_filename_line()
                    if debug_info:
                        debug_file, debug_line = debug_info
                        urwmsg("  renpy.get_filename_line(): {} : {}".format(debug_file, debug_line))
                        if debug_line and debug_line != linenumber:
                            actual_line = debug_line
                except Exception as e:
                    urwmsg("  Error getting filename_line: {}".format(e))
            
            # Final fallback: scan for the closest menu to our suspected position
            if actual_line != linenumber:
                urwmsg("  CORRECTED LINE: {} -> {}".format(linenumber, actual_line))
                linenumber = actual_line
            
            # Get the actual executing node if possible
            executing_node = None
            if filename and hasattr(renpy.game, 'script'):
                script = renpy.game.script
                if hasattr(script, 'namemap'):
                    closest_node = None
                    closest_distance = float('inf')
                    
                    for node_name, node in script.namemap.items():
                        if (hasattr(node, 'filename') and hasattr(node, 'linenumber') and 
                            node.filename == filename):
                            distance = abs(node.linenumber - linenumber)
                            if distance < closest_distance:
                                closest_distance = distance
                                closest_node = node
                                if distance <= 5:  # Very close match
                                    executing_node = node
                                    break
                    
                    if not executing_node and closest_node:
                        executing_node = closest_node
                        urwmsg("  Using closest node at line {} (distance: {})".format(
                            closest_node.linenumber, closest_distance))
            
            # Create execution fingerprint using actual Ren'Py Context attributes
            execution_path = []
            
            # Use return_stack and call_location_stack from Context class
            if hasattr(ctx, 'return_stack') and ctx.return_stack:
                # Get last 3 return locations for context
                for return_site in ctx.return_stack[-3:]:
                    if return_site:
                        execution_path.append(str(return_site))
                        
            if hasattr(ctx, 'call_location_stack') and ctx.call_location_stack:
                # Get last 3 call locations for context  
                for call_loc in ctx.call_location_stack[-3:]:
                    if call_loc:
                        execution_path.append(str(call_loc))
            
            # Add current label context by walking backwards from current position
            current_label = None
            if filename and hasattr(renpy.game, 'script'):
                script = renpy.game.script
                best_label = None
                best_line = -1
                
                for node_name, node in script.namemap.items():
                    if (isinstance(node, renpy.ast.Label) and 
                        hasattr(node, 'filename') and hasattr(node, 'linenumber') and
                        node.filename == filename and node.linenumber <= linenumber and
                        node.linenumber > best_line):
                        best_label = node
                        best_line = node.linenumber
                
                if best_label:
                    current_label = best_label.name
                    execution_path.append(current_label)
                    urwmsg("  Found current label: {} at line {}".format(current_label, best_line))
            
            try:
                timestamp = _urwtime.time()
            except Exception as time_error:
                urwmsg("  Error getting _urwtime.time(): {}, using fallback".format(time_error))
                try:
                    import datetime
                    timestamp = datetime.datetime.now().timestamp()
                except:
                    timestamp = 0
            
            return {
                'filename': filename,
                'linenumber': linenumber,
                'execution_path': tuple(execution_path),
                'node_id': id(executing_node) if executing_node else None,
                'current_label': current_label,
                'timestamp': timestamp
            }
        except Exception as e:
            urwmsg("Error creating execution context: {}".format(e))
            # Return a minimal context to prevent total failure
            try:
                ctx = renpy.game.context()
                if ctx and hasattr(ctx, 'current') and ctx.current:
                    return {
                        'filename': ctx.current[0] if ctx.current else None,
                        'linenumber': ctx.current[2] if len(ctx.current) > 2 else 0,
                        'execution_path': (),
                        'node_id': None,
                        'current_label': None,
                        'timestamp': 0
                    }
            except:
                pass
            return None

    def create_menu_execution_fingerprint(menu_node, items):
        """Create a comprehensive fingerprint for menu identification"""
        try:
            fingerprint = {
                'node_id': id(menu_node),
                'filename': getattr(menu_node, 'filename', ''),
                'linenumber': getattr(menu_node, 'linenumber', 0),
                'item_count': len(items),
                'item_texts': tuple(str(item[0]) if isinstance(item, (list, tuple)) else str(item) for item in items),
                'preceding_nodes': [],
                'following_nodes': []
            }
            
            # Get surrounding AST context
            if hasattr(menu_node, 'filename') and hasattr(menu_node, 'linenumber'):
                script = renpy.game.script
                line_num = menu_node.linenumber
                
                # Find nodes within 10 lines before/after
                for node_key, node in script.namemap.items():
                    if (hasattr(node, 'filename') and hasattr(node, 'linenumber') and 
                        node.filename == menu_node.filename):
                        
                        line_diff = node.linenumber - line_num
                        if -10 <= line_diff < 0:  # Preceding nodes
                            fingerprint['preceding_nodes'].append((node.__class__.__name__, line_diff))
                        elif 0 < line_diff <= 10:  # Following nodes
                            fingerprint['following_nodes'].append((node.__class__.__name__, line_diff))
                
                # Sort by line distance
                fingerprint['preceding_nodes'].sort(key=lambda x: abs(x[1]))
                fingerprint['following_nodes'].sort(key=lambda x: x[1])
                
                # Keep only closest 5 nodes each direction
                fingerprint['preceding_nodes'] = tuple(fingerprint['preceding_nodes'][:5])
                fingerprint['following_nodes'] = tuple(fingerprint['following_nodes'][:5])
            
            return fingerprint
        except Exception as e:
            urwmsg("Error creating menu fingerprint: {}".format(e))
            return None

    

    def get_strategy_from_node(node):
        """Get strategy information using node ID as key"""
        try:
            node_id = id(node)
            if node_id in node_strategy_cache:
                strategy_info = node_strategy_cache[node_id]
                urwmsg("RETRIEVED STRATEGY: {} with offset {} for node at line {}".format(
                    strategy_info['strategy'], strategy_info['offset'], 
                    getattr(node, 'linenumber', 0)))
                return strategy_info['strategy'], strategy_info['offset']
            else:
                urwmsg("No strategy found for node at line {}, using default 'exact'".format(
                    getattr(node, 'linenumber', 0)))
                return 'exact', 0
        except Exception as e:
            urwmsg("Error retrieving strategy for node: {}".format(e))
            return 'exact', 0

    def find_exact_menu_match(items, execution_context):
        """Find exact menu match"""
        try:
            if not execution_context:
                return None
            
            script = renpy.game.script
            filename = execution_context['filename']
            linenumber = execution_context['linenumber']
            current_label = execution_context.get('current_label')
            
            urwmsg("Looking for menu match in {} at line {} (label: {})".format(
                filename, linenumber, current_label))
            
            # DEBUG: Show what we're looking for
            urwmsg("SEARCH TARGET:")
            urwmsg("  Looking for {} menu items:".format(len(items)))
            for i, item in enumerate(items):
                item_text = str(item[0]) if isinstance(item, (list, tuple)) else str(item)
                clean_text = re.sub(r'\{[^}]*\}', '', item_text).strip()
                urwmsg("    [{}]: '{}' (clean: '{}')".format(i, item_text, clean_text))
            
            # Strategy 1: Find ALL menu nodes in file first
            all_menus = []
            for node_key, node in script.namemap.items():
                if isinstance(node, renpy.ast.Menu) and hasattr(node, 'filename') and hasattr(node, 'items'):
                    # Check filename match (handle .rpy/.rpyc variations)
                    node_file = node.filename.replace('.rpyc', '.rpy') if node.filename else ''
                    check_file = filename.replace('.rpyc', '.rpy') if filename else ''
                    
                    if node_file == check_file or node_file.endswith(check_file.split('/')[-1]):
                        all_menus.append(node)
            
            urwmsg("Found {} total menu nodes in file".format(len(all_menus)))
            
            # DEBUG: Show ALL menus with their details
            for i, node in enumerate(all_menus):
                distance = abs(node.linenumber - linenumber)
                urwmsg("  Menu #{} at line {} (distance: {}, {} items):".format(
                    i+1, node.linenumber, distance, len(node.items) if hasattr(node, 'items') else 0))
                
                if hasattr(node, 'items'):
                    for j, menu_item in enumerate(node.items):
                        if menu_item and len(menu_item) > 0:
                            menu_text = str(menu_item[0]) if menu_item[0] else ""
                            clean_menu = re.sub(r'\{[^}]*\}', '', menu_text).strip()
                            urwmsg("    [{}]: '{}' (clean: '{}')".format(j, menu_text, clean_menu))
            
            # Filter candidates with flexible item count matching
            candidates = []
            for node in all_menus:
                if hasattr(node, 'items') and len(node.items) > 0:
                    distance = abs(node.linenumber - linenumber)
                    
                    # FLEXIBLE MATCHING: Try different item arrangements
                    match_results = []
                    
                    # Strategy A: Exact count match (original logic)
                    if len(node.items) == len(items):
                        match_results.append(('exact', node.items, 0))
                    
                    # Strategy B: Menu has one extra item (likely a question/prompt)
                    elif len(node.items) == len(items) + 1:
                        # Try skipping first item (question at start)
                        match_results.append(('skip_first', node.items[1:], 1))
                        # Try skipping last item (rare but possible)
                        match_results.append(('skip_last', node.items[:-1], 0))
                    
                    # Strategy C: Menu has fewer items (unlikely but check anyway)
                    elif len(node.items) < len(items) and len(node.items) >= 2:
                        match_results.append(('partial', node.items, 0))
                    
                    # Test each matching strategy
                    for strategy, test_items, offset in match_results:
                        if len(test_items) != len(items):
                            continue
                            
                        text_match_score = 0
                        match_details = []
                        
                        for i, (menu_item, input_item) in enumerate(zip(test_items, items)):
                            menu_text = str(menu_item[0]) if menu_item and menu_item[0] else ""
                            input_text = str(input_item[0]) if isinstance(input_item, (list, tuple)) else str(input_item)
                            
                            # Clean texts for comparison
                            clean_menu = re.sub(r'\{[^}]*\}', '', menu_text).strip()
                            clean_input = re.sub(r'\{[^}]*\}', '', input_text).strip()
                            
                            item_score = 0
                            if clean_menu == clean_input:
                                text_match_score += 10
                                item_score = 10
                                match_details.append("EXACT")
                            elif clean_menu.lower() == clean_input.lower():
                                text_match_score += 8
                                item_score = 8
                                match_details.append("CASE")
                            else:
                                match_details.append("MISS")
                            
                            urwmsg("    {} Item {} match: '{}' vs '{}' = {} ({})".format(
                                strategy.upper(), i, clean_menu, clean_input, item_score, match_details[-1]))
                        
                        if text_match_score >= len(items) * 8:  # At least 80% match
                            candidates.append((node, text_match_score, distance, strategy, offset))
                            urwmsg("  ✓ CANDIDATE: line {} (distance: {}, score: {}, strategy: {}, matches: {})".format(
                                node.linenumber, distance, text_match_score, strategy, " ".join(match_details)))
                            break  # Use first successful strategy
                        else:
                            urwmsg("  ✗ {} STRATEGY: line {} (distance: {}, score: {}, matches: {}) - below threshold".format(
                                strategy.upper(), node.linenumber, distance, text_match_score, " ".join(match_details)))
            
            urwmsg("Final candidates: {}".format(len(candidates)))
            
            # Find menus within immediate vicinity (within 20 lines)
            immediate_candidates = []
            close_candidates = []
            distant_candidates = []
            
            for node, text_match_score, distance, strategy, offset in candidates:
                urwmsg("  Processing candidate at line {} (distance: {}, score: {}, strategy: {})".format(
                    node.linenumber, distance, text_match_score, strategy))
                
                # Immediate vicinity (within 20 lines) gets highest priority
                if distance <= 20:
                    immediate_candidates.append((node, text_match_score, distance, strategy, offset))
                    urwmsg("    → IMMEDIATE category (≤20 lines)")
                # Close matches (within 100 lines)
                elif distance <= 100:
                    close_candidates.append((node, text_match_score, distance, strategy, offset))
                    urwmsg("    → CLOSE category (≤100 lines)")
                else:
                    distant_candidates.append((node, text_match_score, distance, strategy, offset))
                    urwmsg("    → DISTANT category (>100 lines)")
            
            def store_strategy_on_node(node, strategy, offset):
                """Store strategy information using node ID as key"""
                try:
                    node_id = id(node)
                    node_strategy_cache[node_id] = {
                        'strategy': strategy,
                        'offset': offset,
                        'filename': getattr(node, 'filename', ''),
                        'linenumber': getattr(node, 'linenumber', 0)
                    }
                    urwmsg("STORED STRATEGY: {} with offset {} for node at line {} (ID: {})".format(
                        strategy, offset, getattr(node, 'linenumber', 0), node_id))
                except Exception as e:
                    urwmsg("Warning: Could not store strategy for node: {}".format(e))

            # Process immediate candidates first
            if immediate_candidates:
                urwmsg("Using IMMEDIATE candidates ({}) - within 20 lines".format(len(immediate_candidates)))
                # Sort by distance first, then by score, then prefer exact matches
                immediate_candidates.sort(key=lambda x: (x[2], -x[1], 0 if x[3] == 'exact' else 1))
                best_node, score, distance, strategy, offset = immediate_candidates[0]
                
                # Store strategy on node
                store_strategy_on_node(best_node, strategy, offset)
                
                urwmsg("Found IMMEDIATE menu match at {}:{} (score: {}, distance: {}, strategy: {})".format(
                    best_node.filename, best_node.linenumber, score, distance, strategy))
                return best_node
            
            # Process close candidates second
            if close_candidates:
                urwmsg("Using close candidates ({}) - NO IMMEDIATE MATCHES FOUND!".format(len(close_candidates)))
                # Sort by distance first, then by score, then prefer exact matches
                close_candidates.sort(key=lambda x: (x[2], -x[1], 0 if x[3] == 'exact' else 1))
                best_node, score, distance, strategy, offset = close_candidates[0]
                
                store_strategy_on_node(best_node, strategy, offset)
                
                urwmsg("Found CLOSE menu match at {}:{} (score: {}, distance: {}, strategy: {})".format(
                    best_node.filename, best_node.linenumber, score, distance, strategy))
                
                urwmsg("DEBUG: No immediate matches found. Expected menu around line {} ± 20 (range {}-{})".format(
                    linenumber, linenumber-20, linenumber+20))
                
                return best_node
            
            if distant_candidates:
                urwmsg("Using distant candidates ({}) - checking label context".format(len(distant_candidates)))
                
                perfect_distant = []
                for node, score, distance, strategy, offset in distant_candidates:
                    if score == len(items) * 10:  # Perfect text match
                        perfect_distant.append((node, score, distance, strategy, offset))
                
                if perfect_distant:
                    perfect_distant.sort(key=lambda x: (x[2], 0 if x[3] == 'exact' else 1))  # Sort by distance, prefer exact
                    best_node, score, distance, strategy, offset = perfect_distant[0]
                    
                    store_strategy_on_node(best_node, strategy, offset)
                    
                    urwmsg("Found DISTANT perfect menu match at {}:{} (distance: {})".format(
                        best_node.filename, best_node.linenumber, distance))
                    return best_node
            
            urwmsg("No suitable menu match found")
            return None
        except Exception as e:
            urwmsg("Error in exact menu match: {}".format(e))
            import traceback
            urwmsg("Traceback: {}".format(traceback.format_exc()))
            return None
    
    def register_menu_with_context(items, menu_node, execution_context):
        """Register menu with context tracking"""
        try:
            cleanup_menu_registry()
            
            if not execution_context or not menu_node:
                return
            
            # Create comprehensive key with execution context
            fingerprint = create_menu_execution_fingerprint(menu_node, items)
            if not fingerprint:
                return
            
            menu_key = (
                execution_context['filename'],
                execution_context['linenumber'],
                fingerprint['node_id'],
                fingerprint['item_texts'],
                execution_context.get('current_label', ''),
                fingerprint['preceding_nodes'],
                fingerprint['following_nodes']
            )
            
            menu_registry[menu_key] = {
                'node': menu_node,
                'fingerprint': fingerprint,
                'execution_context': execution_context
            }
            menu_registry_access_times[menu_key] = _urwtime.time()
            
            urwmsg("Registered menu at {}:{} with fingerprint".format(
                execution_context['filename'], execution_context['linenumber']))
            
        except Exception as e:
            urwmsg("Error registering menu with context: {}".format(e))

    def find_menu_from_enhanced_registry(items, execution_context):
        """Find menu using enhanced registry with context matching"""
        try:
            if not execution_context:
                return None
            
            # Try exact match first
            for menu_key, menu_data in menu_registry.items():
                stored_context = menu_data['execution_context']
                
                # Check if contexts match closely
                if (stored_context['filename'] == execution_context['filename'] and
                    abs(stored_context['linenumber'] - execution_context['linenumber']) <= 10):
                    
                    fingerprint = menu_data['fingerprint']
                    
                    # Verify item texts match exactly
                    current_item_texts = tuple(str(item[0]) if isinstance(item, (list, tuple)) else str(item) for item in items)
                    if fingerprint['item_texts'] == current_item_texts:
                        
                        # Additional context verification
                        if (stored_context.get('current_label') == execution_context.get('current_label') or
                            not stored_context.get('current_label') or
                            not execution_context.get('current_label')):
                            
                            menu_registry_access_times[menu_key] = _urwtime.time()
                            urwmsg("Found menu from enhanced registry")
                            return menu_data['node']
            
            return None
        except Exception as e:
            urwmsg("Error finding menu from enhanced registry: {}".format(e))
            return None

    def cleanup_menu_registry():
        """Clean up old entries from menu registry"""
        if len(menu_registry) > MAX_REGISTRY_SIZE:
            urwmsg("Registry cleanup: {} entries, removing oldest {}".format(len(menu_registry), REGISTRY_CLEANUP_SIZE))
            
            sorted_items = sorted(menu_registry_access_times.items(), key=lambda x: x[1])
            
            for i in range(min(REGISTRY_CLEANUP_SIZE, len(sorted_items))):
                key_to_remove = sorted_items[i][0]
                if key_to_remove in menu_registry:
                    del menu_registry[key_to_remove]
                del menu_registry_access_times[key_to_remove]

    def find_correct_menu_node_enhanced(items):
        """Enhanced menu finding function with multiple strategies"""
        try:
            urwmsg("=== KNOX MENU DETECTION v1.5 ===")
            
            # Get current execution context
            execution_context = get_execution_context_signature()
            if not execution_context:
                urwmsg("No execution context available")
                return None
            
            urwmsg("Execution context: {}:{} (label: {})".format(
                execution_context['filename'], execution_context['linenumber'], 
                execution_context.get('current_label', 'None')))
            
            # Strategy 1: Check enhanced registry
            menu_node = find_menu_from_enhanced_registry(items, execution_context)
            if menu_node:
                urwmsg("✓ Found menu via enhanced registry")
                return menu_node
            
            # Strategy 2: Find exact match using context
            menu_node = find_exact_menu_match(items, execution_context)
            if menu_node:
                urwmsg("✓ Found menu via exact context match")
                register_menu_with_context(items, menu_node, execution_context)
                return menu_node
            
            # Strategy 3: Fallback to original proximity method
            menu_node = find_menu_by_proximity_and_text(items)
            if menu_node:
                urwmsg("✓ Found menu via proximity fallback")
                register_menu_with_context(items, menu_node, execution_context)
                return menu_node
            
            urwmsg("✗ No suitable menu node found")
            return None
            
        except Exception as e:
            urwmsg("Error in enhanced menu detection: {}".format(e))
            return None

    
    def extract_choice_consequences(choice_block):
        """Consequence extraction from a choice block with enhanced handling"""
        choice_block_id = id(choice_block) if choice_block else 0
    
        cached_result = get_cached_consequences(choice_block_id)
        if cached_result is not None:
            return cached_result
        
        urwmsg("=== URW CONSEQUENCE ANALYZER ===")
        
        consequences = []
        statements = []
        
        if isinstance(choice_block, collections.abc.Sequence) and not isinstance(choice_block, (str, bytes)):
            statements = choice_block
        elif hasattr(choice_block, 'children'):
            statements = choice_block.children
        elif choice_block is None:
            return consequences
        else:
            return consequences
        
        if not statements:
            return consequences
        
        # Statement processing with improved conditional handling
        for i, stmt in enumerate(statements):
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
                    # Handle all condition types properly
                    urwmsg("PROCESSING IF STATEMENT with {} entries".format(len(stmt.entries)))
                    
                    condition_details = []
                    total_sub_consequences = []
                    
                    for entry_idx, (condition, block) in enumerate(stmt.entries):
                        urwmsg("  Entry {}: condition = {}".format(entry_idx, condition))
                        
                        # Get sub-consequences for this branch
                        sub_consequences = extract_choice_consequences(block) if block else []
                        if sub_consequences:
                            total_sub_consequences.extend(sub_consequences)
                        
                        # Process the condition text
                        if condition is not None:
                            # This is an 'if' or 'elif' branch
                            condition_str = str(condition).strip()
                            
                            # Clean up the condition text
                            if condition_str.startswith('store.'):
                                condition_str = condition_str[6:]
                            
                            # Handle common conditions specially
                            if 'config.developer' in condition_str:
                                condition_str = condition_str.replace('config.developer', 'developer_mode')
                            if '_in_replay' in condition_str:
                                condition_str = condition_str.replace('_in_replay', 'in_replay')
                            
                            # Limit length for display
                            if len(condition_str) > 35:
                                condition_str = condition_str[:32] + "..."
                            
                            # Determine the condition type
                            if entry_idx == 0:
                                condition_details.append(f"if {condition_str}")
                            else:
                                condition_details.append(f"elif {condition_str}")
                        else:
                            # This is an 'else' branch
                            condition_details.append("else")
                    
                    urwmsg("  Condition details: {}".format(condition_details))
                    urwmsg("  Total sub-consequences: {}".format(len(total_sub_consequences)))
                    
                    # Decide how to represent this conditional block
                    if len(condition_details) == 0:
                        # No conditions found, skip
                        continue
                    elif len(condition_details) == 1:
                        # Single if statement
                        condition_text = condition_details[0]
                        consequences.append(('condition', condition_text, str(len(total_sub_consequences)), f'❓ {condition_text}'))
                    elif len(condition_details) == 2 and condition_details[1] == "else":
                        # if-else block
                        condition_text = f"{condition_details[0]}-else"
                        consequences.append(('condition', condition_text, str(len(total_sub_consequences)), f'❓ {condition_text}'))
                    else:
                        # Complex if-elif-else block
                        primary_condition = condition_details[0]
                        additional_branches = len(condition_details) - 1
                        
                        if additional_branches == 1 and condition_details[1] == "else":
                            condition_text = f"{primary_condition}-else"
                        else:
                            condition_text = f"{primary_condition} (+{additional_branches})"
                        
                        consequences.append(('condition', condition_text, str(len(total_sub_consequences)), f'❓ {condition_text}'))
                    
                    # If there are meaningful sub-consequences, add them too
                    if total_sub_consequences:
                        # Check if we should show sub-consequences directly
                        has_important_consequences = any(
                            cons[0] in ['jump', 'call', 'return', 'increase', 'decrease'] 
                            for cons in total_sub_consequences
                        )
                        
                        if has_important_consequences and len(condition_details) == 1:
                            # For simple conditions with important consequences, show both
                            consequences.extend(total_sub_consequences)
                
                # Skip visual/audio elements
                elif isinstance(stmt, (renpy.ast.Say, renpy.ast.Scene, renpy.ast.Show, renpy.ast.Hide, 
                                    renpy.ast.With, renpy.ast.ShowLayer, renpy.ast.Camera, renpy.ast.Transform,
                                    renpy.ast.Pass, renpy.ast.Label, renpy.ast.Menu, renpy.ast.UserStatement)):
                    continue
                
                else:
                    class_name = stmt.__class__.__name__
                    if class_name not in ['Play', 'Stop', 'Queue', 'Music', 'Sound', 'Voice', 'Audio', 'Comment', 'Translate', 'TranslateBlock', 'EndTranslate']:
                        for attr in ['target', 'label', 'expression', 'name', 'value']:
                            if hasattr(stmt, attr):
                                value = getattr(stmt, attr)
                                if value and not str(value).startswith('_'):
                                    consequences.append(('unknown', f'{attr}: {str(value)}', '', f'{class_name.lower()} {value}'))
                                    break
            
            except Exception as e:
                urwmsg("Error processing statement {}: {}".format(i, e))
                continue
        
        # Deduplication that preserves detailed conditions
        seen_conditions = set()
        filtered_consequences = []
        
        for consequence in consequences:
            if consequence[0] == 'condition':
                # Use the full condition text as key to avoid over-deduplication
                condition_key = consequence[1]  # Use the full condition text
                if condition_key not in seen_conditions:
                    seen_conditions.add(condition_key)
                    filtered_consequences.append(consequence)
                else:
                    urwmsg("SKIPPING duplicate condition: {}".format(condition_key))
            else:
                filtered_consequences.append(consequence)
        
        urwmsg("FINAL CONSEQUENCES: {} (from {} original)".format(len(filtered_consequences), len(consequences)))
        
        cache_consequences(choice_block_id, filtered_consequences)
        return filtered_consequences

    def analyze_python_statement_enhanced(stmt):
        """Python statement analysis using AST parser"""
        consequences = []
        
        source = None
        if hasattr(stmt, 'code'):
            code_obj = stmt.code
            
            if hasattr(code_obj, 'source'):
                source = code_obj.source
            elif hasattr(code_obj, 'py'):
                source = code_obj.py
            elif hasattr(code_obj, 'python'):
                source = code_obj.python
        
        if source:
            consequences.extend(parse_python_source_enhanced(source))
        else:
            consequences.extend(analyze_bytecode_enhanced(stmt))
        
        return consequences

    def parse_python_source_enhanced(source):
        """Enhanced Python source parsing with better conditional detection"""
        consequences = []
        
        if not source:
            return consequences
        
        try:
            import ast
            tree = ast.parse(source)
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name):
                            var_name = target.id
                            
                            try:
                                if isinstance(node.value, ast.Constant):
                                    value = str(node.value.value)
                                elif hasattr(node.value, 'n'):
                                    value = str(node.value.n)
                                elif hasattr(node.value, 's'):
                                    value = node.value.s
                                else:
                                    value = ast.unparse(node.value) if hasattr(ast, 'unparse') else '?'
                                
                                consequences.append(('assign', var_name, value, f'{var_name} = {value}'))
                            except:
                                consequences.append(('assign', var_name, '?', f'{var_name} = ?'))
                
                elif isinstance(node, ast.AugAssign):
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
                            elif op == 'Sub':
                                consequences.append(('decrease', var_name, value, f'{var_name} -= {value}'))
                        except:
                            consequences.append(('modify', var_name, '?', f'{var_name} {op}= ?'))
                
                # Detect if statements in Python code
                elif isinstance(node, ast.If):
                    try:
                        # Get condition text
                        condition_text = "unknown_condition"
                        if hasattr(ast, 'unparse'):
                            condition_text = ast.unparse(node.test)
                        elif hasattr(node.test, 'id'):
                            condition_text = node.test.id
                        elif hasattr(node.test, 'attr'):
                            condition_text = f"*.{node.test.attr}"
                        
                        # Clean up common conditions
                        if 'config.developer' in condition_text:
                            condition_text = condition_text.replace('config.developer', 'developer_mode')
                        if '_in_replay' in condition_text:
                            condition_text = condition_text.replace('_in_replay', 'in_replay')
                        
                        # Check for else clause
                        has_else = node.orelse is not None and len(node.orelse) > 0
                        has_elif = has_else and any(isinstance(n, ast.If) for n in node.orelse)
                        
                        if has_elif:
                            condition_text += " (+elif)"
                        elif has_else:
                            condition_text += "-else"
                        
                        consequences.append(('condition', f"if {condition_text}", '1', f'❓ if {condition_text}'))
                    except:
                        consequences.append(('condition', 'if condition', '1', '❓ if condition'))
        
        except (SyntaxError, Exception) as e:
            urwmsg("AST parsing failed: {}, falling back to regex".format(e))
        
        # Regex fallback
        regex_consequences = parse_with_regex_fallback(source)
        consequences.extend(regex_consequences)
        
        return consequences

    def analyze_bytecode_enhanced(stmt):
        """Bytecode analysis for compiled games"""
        consequences = []
        
        try:
            import dis
            
            code_obj = None
            if hasattr(stmt, 'code'):
                if hasattr(stmt.code, 'py'):
                    code_obj = stmt.code.py
                elif hasattr(stmt.code, 'bytecode'):
                    code_obj = stmt.code.bytecode
                else:
                    code_obj = stmt.code
            
            if code_obj and hasattr(code_obj, 'co_code'):
                instructions = list(dis.get_instructions(code_obj))
                
                for i, instr in enumerate(instructions):
                    if instr.opname in ['STORE_NAME', 'STORE_GLOBAL', 'STORE_FAST']:
                        var_name = instr.argval
                        
                        if i > 0:
                            prev_instr = instructions[i-1]
                            if prev_instr.opname == 'INPLACE_ADD':
                                consequences.append(('increase', var_name, '?', f'compiled: {var_name} += ?'))
                            elif prev_instr.opname == 'INPLACE_SUBTRACT':
                                consequences.append(('decrease', var_name, '?', f'compiled: {var_name} -= ?'))
                            elif prev_instr.opname in ['LOAD_CONST', 'LOAD_FAST']:
                                if prev_instr.opname == 'LOAD_CONST' and prev_instr.argval is not None:
                                    value = str(prev_instr.argval)
                                    consequences.append(('assign', var_name, value, f'compiled: {var_name} = {value}'))
                                else:
                                    consequences.append(('assign', var_name, '?', f'compiled: {var_name} = ?'))
        
        except Exception:
            consequences.append(('code', 'Python statement', '', 'Python code executed'))
        
        return consequences

    def parse_with_regex_fallback(source):
        """Enhanced fallback regex parsing with conditional detection"""
        consequences = []
        
        code_lines = [line.strip() for line in source.split('\n') if line.strip()]
        
        for line in code_lines:
            # Detect if statements
            if line.strip().startswith('if ') and ':' in line:
                try:
                    condition_part = line.split('if ')[1].split(':')[0].strip()
                    
                    # Clean up common conditions
                    if 'config.developer' in condition_part:
                        condition_part = condition_part.replace('config.developer', 'developer_mode')
                    if '_in_replay' in condition_part:
                        condition_part = condition_part.replace('_in_replay', 'in_replay')
                    
                    if len(condition_part) > 30:
                        condition_part = condition_part[:27] + "..."
                    
                    consequences.append(('condition', f'if {condition_part}', '1', f'❓ if {condition_part}'))
                except:
                    consequences.append(('condition', 'if condition', '1', '❓ if condition'))
            
            # Detect elif statements
            elif line.strip().startswith('elif ') and ':' in line:
                try:
                    condition_part = line.split('elif ')[1].split(':')[0].strip()
                    
                    if 'config.developer' in condition_part:
                        condition_part = condition_part.replace('config.developer', 'developer_mode')
                    if '_in_replay' in condition_part:
                        condition_part = condition_part.replace('_in_replay', 'in_replay')
                    
                    if len(condition_part) > 30:
                        condition_part = condition_part[:27] + "..."
                    
                    consequences.append(('condition', f'elif {condition_part}', '1', f'❓ elif {condition_part}'))
                except:
                    consequences.append(('condition', 'elif condition', '1', '❓ elif condition'))
            
            # Detect else statements
            elif line.strip() == 'else:':
                consequences.append(('condition', 'else', '1', '❓ else'))
            
            elif '+=' in line:
                try:
                    var_name = line.split('+=')[0].strip()
                    value_part = line.split('+=')[1].strip()
                    clean_var = re.sub(r'\[.*?\]', '', var_name)
    
                    try:
                        if value_part.isdigit():
                            actual_value = value_part
                        elif value_part.replace('.', '').isdigit():
                            actual_value = value_part
                        elif value_part.startswith('-') and value_part[1:].isdigit():
                            actual_value = value_part
                        else:
                            actual_value = value_part
    
                        consequences.append(('increase', clean_var, actual_value, line))
                    except:
                        consequences.append(('increase', clean_var, '?', line))
                except:
                    consequences.append(('code', 'Variable increase', '', line))
    
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
                    except:
                        consequences.append(('decrease', clean_var, '?', line))
                except:
                    consequences.append(('code', 'Variable decrease', '', line))
    
            elif '=' in line and '==' not in line and '!=' not in line and '<=' not in line and '>=' not in line:
                if not any(line.strip().startswith(x) for x in ['if ', 'elif ', 'for ', 'while ', 'def ', 'class ', 'import ', 'from ']):
                    try:
                        var_name = line.split('=')[0].strip()
                        value_part = line.split('=', 1)[1].strip()
                        clean_var = re.sub(r'\[.*?\]', '', var_name)
    
                        if not clean_var.startswith('_') and len(clean_var) > 1:
                            if not clean_var.startswith('renpy.pause'):
                                display_value = value_part[:20] + ('...' if len(value_part) > 20 else '')
                                consequences.append(('assign', clean_var, display_value, line))
                    except:
                        consequences.append(('code', 'Variable assignment', '', line))
    
            else:
                if any(keyword in line.lower() for keyword in [' = true', ' = false']):
                    try:
                        var_name = line.split('=')[0].strip()
                        value_part = line.split('=')[1].strip()
                        clean_var = re.sub(r'\[.*?\]', '', var_name)
                        consequences.append(('boolean', clean_var, value_part, line))
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
                        consequences.append(('function', 'Function call', line[:30], line))
    
                elif len(line) > 3 and not line.startswith('#') and not line.strip().startswith('renpy.'):
                    consequences.append(('code', 'Python code', line[:30], line))
        
        return consequences

    def get_cached_consequences(choice_block_id):
        """Get cached consequences with LRU management"""
        if choice_block_id in consequence_cache:
            consequence_cache_access[choice_block_id] = _urwtime.time()
            return consequence_cache[choice_block_id]
        return None

    def cache_consequences(choice_block_id, consequences):
        """Cache consequences with size limit"""
        if len(consequence_cache) >= MAX_CONSEQUENCE_CACHE:
            sorted_cache = sorted(consequence_cache_access.items(), key=lambda x: x[1])
            for i in range(50):
                if i < len(sorted_cache):
                    old_key = sorted_cache[i][0]
                    if old_key in consequence_cache:
                        del consequence_cache[old_key]
                    del consequence_cache_access[old_key]
        
        consequence_cache[choice_block_id] = consequences
        consequence_cache_access[choice_block_id] = _urwtime.time()

    def find_menu_by_proximity_and_text(items):
        """Fallback proximity + text matching logic"""
        ctx = renpy.game.context()
        current_position = ctx.current
        
        if not current_position:
            return None

        script = renpy.game.script
        current_file = current_position[0]
        current_line = current_position[2] if len(current_position) > 2 else 0
        
        menu_nodes = []
        current_file_base = current_file.replace('.rpyc', '.rpy').replace('.rpa', '.rpy')
        
        for node_key, node in script.namemap.items():
            if (hasattr(node, '__class__') and node.__class__.__name__ == 'Menu' and
                hasattr(node, 'filename')):
                
                node_file = node.filename
                node_file_base = node_file.replace('.rpyc', '.rpy').replace('.rpa', '.rpy') if node_file else ''
                
                if (node_file == current_file or 
                    node_file_base == current_file_base or
                    node_file_base.endswith(current_file_base.split('/')[-1]) or
                    current_file_base.endswith(node_file_base.split('/')[-1])):
                    
                    menu_nodes.append(node)
        
        best_match = None
        best_score = 0
        
        for node in menu_nodes:
            if hasattr(node, 'items') and len(node.items) == len(items):
                score = 0
                
                for i in range(min(len(node.items), len(items))):
                    if len(node.items[i]) > 0 and len(items[i]) > 0:
                        node_text = str(node.items[i][0]) if node.items[i][0] else ""
                        item_text = str(items[i][0]) if items[i][0] else ""
                        
                        clean_node_text = re.sub(r'\{[^}]*\}', '', node_text).strip()
                        clean_item_text = re.sub(r'\{[^}]*\}', '', item_text).strip()
                        
                        if clean_node_text == clean_item_text:
                            score += 10
                        elif clean_node_text.lower() == clean_item_text.lower():
                            score += 8
                        elif clean_node_text in clean_item_text or clean_item_text in clean_node_text:
                            score += 5
                
                if score > best_score:
                    best_score = score
                    best_match = node
        
        if best_match and best_score >= 10:
            if best_score == 20:
                perfect_matches = []
                for node in menu_nodes:
                    if hasattr(node, 'items') and len(node.items) == len(items):
                        score = 0
                        for i in range(min(len(node.items), len(items))):
                            if len(node.items[i]) > 0 and len(items[i]) > 0:
                                node_text = str(node.items[i][0]) if node.items[i][0] else ""
                                item_text = str(items[i][0]) if items[i][0] else ""
                                clean_node_text = re.sub(r'\{[^}]*\}', '', node_text).strip()
                                clean_item_text = re.sub(r'\{[^}]*\}', '', item_text).strip()
                                if clean_node_text == clean_item_text:
                                    score += 10
                        if score == 20:
                            perfect_matches.append(node)
                
                if len(perfect_matches) > 1:
                    best_distance = float('inf')
                    closest_match = None
                    for node in perfect_matches:
                        if hasattr(node, 'linenumber'):
                            distance = abs(node.linenumber - current_line)
                            if distance < best_distance:
                                best_distance = distance
                                closest_match = node
                    
                    if closest_match:
                        best_match = closest_match
            
            return best_match
        
        if menu_nodes:
            best_node = None
            best_distance = float('inf')
            
            for node in menu_nodes:
                if hasattr(node, 'linenumber'):
                    distance = abs(node.linenumber - current_line)
                    if distance < best_distance:
                        best_distance = distance
                        best_node = node
            
            if best_node:
                return best_node
        
        for node_key, node in script.namemap.items():
            if (hasattr(node, '__class__') and node.__class__.__name__ == 'Menu' and
                hasattr(node, 'items') and len(node.items) == len(items)):
                return node
        
        return None

    def escape_renpy_formatting(text):
        """Escape Ren'Py formatting characters in text to prevent interpretation"""
        import re
        def double_brackets(match):
            return match.group(0) * 2
        
        # Double up brackets and braces to escape them
        return re.sub(r'\{+|\[+', double_brackets, text)
    
    def format_consequences_urw(consequences):
        """Format consequences for display"""
        if not consequences:
            return ""
    
        MAX_CONSEQUENCES = persistent.universal_wt_max_consequences
        SHOW_ALL = persistent.universal_wt_show_all_available
        
        # Get filter settings
        filters = persistent.universal_wt_filters
        name_filters = persistent.universal_wt_name_filters
        
        urwmsg("CONSEQUENCE FORMATTING: MAX_CONSEQUENCES = {}, SHOW_ALL = {}".format(MAX_CONSEQUENCES, SHOW_ALL))
        urwmsg("CONSEQUENCE FORMATTING: Total consequences available = {}".format(len(consequences)))
        
        formatted = []
        
        arrows = {
            'jump': "➤",
            'call': "📞",
            'return': "↩",
            'function': "🔧",
            'condition': "❓",
            'code': "⚙"
        }
    
        # Filter and format consequences
        seen_consequences = set()
        
        for consequence in consequences:
            if len(consequence) >= 4:
                action_type, content, value, full_code = consequence
            elif len(consequence) >= 3:
                action_type, content, value = consequence
                full_code = ''
            else:
                action_type, content = consequence[0], consequence[1]
                value, full_code = '', ''
    
            # FILTER 1: Check if this action type is enabled
            type_filter_map = {
                'condition': 'conditions',
                'jump': 'jumps',
                'call': 'calls', 
                'return': 'returns',
                'increase': 'increases',
                'decrease': 'decreases',
                'assign': 'assignments',
                'boolean': 'booleans',
                'function': 'functions',
                'code': 'code',
                'unknown': 'unknown'
            }
            
            filter_key = type_filter_map.get(action_type, 'unknown')
            if not filters.get(filter_key, True):
                urwmsg("FILTERED OUT: {} (type filter disabled)".format(action_type))
                continue
    
            # FILTER 2: Check name-based filters
            content_str = str(content).lower()
            should_filter = False
    
            if name_filters.get('hide_underscore', True) and content_str.startswith('_'):
                urwmsg("FILTERED OUT: {} (starts with underscore)".format(content))
                should_filter = True
            elif name_filters.get('hide_renpy', True) and ('renpy.' in content_str):
                urwmsg("FILTERED OUT: {} (contains renpy.)".format(content))
                should_filter = True
            elif name_filters.get('hide_config', False) and ('config.' in content_str):
                urwmsg("FILTERED OUT: {} (contains config.)".format(content))
                should_filter = True
            elif name_filters.get('hide_store', True) and ('store.' in content_str):
                urwmsg("FILTERED OUT: {} (contains store.)".format(content))
                should_filter = True
    
            # Check custom prefix filters (semicolon-separated auto-parsing)
            if not should_filter:
                custom_prefix_str = name_filters.get('custom_prefix', '')
                if custom_prefix_str:
                    # Parse semicolon-separated prefixes
                    prefix_filters = [p.strip().lower() for p in custom_prefix_str.split(';') if p.strip()]
                    for prefix in prefix_filters:
                        if content_str.startswith(prefix):
                            urwmsg("FILTERED OUT: {} (custom prefix filter: '{}')".format(content, prefix))
                            should_filter = True
                            break
    
            # Check custom contains filters (semicolon-separated auto-parsing)
            if not should_filter:
                custom_contains_str = name_filters.get('custom_contains', '')
                if custom_contains_str:
                    # Parse semicolon-separated contains patterns
                    contains_filters = [c.strip().lower() for c in custom_contains_str.split(';') if c.strip()]
                    for contains_text in contains_filters:
                        if contains_text in content_str:
                            urwmsg("FILTERED OUT: {} (custom contains filter: '{}')".format(content, contains_text))
                            should_filter = True
                            break
    
            if should_filter:
                continue
    
            # Check for duplicates
            consequence_id = (action_type, str(content), str(value))
            if consequence_id in seen_consequences:
                continue
            seen_consequences.add(consequence_id)
                
            # Format the consequence based on type - WITH ESCAPING
            if action_type == 'increase':
                if value and value != '1' and value != '?':
                    formatted.append("+{} (+{})".format(escape_renpy_formatting(str(content)), escape_renpy_formatting(str(value))))
                else:
                    formatted.append("+{}".format(escape_renpy_formatting(str(content))))
                    
            elif action_type == 'decrease':
                content_escaped = escape_renpy_formatting(str(content))
                value_escaped = escape_renpy_formatting(str(value))
                if value and value != '1' and value != '?':
                    formatted.append("-{} (-{})".format(content_escaped, value_escaped))
                else:
                    formatted.append("-{}".format(content_escaped))
                    
            elif action_type == 'assign':
                content_escaped = escape_renpy_formatting(str(content))
                value_escaped = escape_renpy_formatting(str(value))
                if len(str(value)) > 15:
                    formatted.append("{} = {}...".format(content_escaped, str(value_escaped)[:12]))
                else:
                    formatted.append("{} = {}".format(content_escaped, value_escaped))
                    
            elif action_type == 'boolean':
                content_escaped = escape_renpy_formatting(str(content))
                value_escaped = escape_renpy_formatting(str(value))
                formatted.append("{} = {}".format(content_escaped, value_escaped))
                
            elif action_type == 'jump':
                content_escaped = escape_renpy_formatting(str(content))
                arrow = arrows.get('jump', '>')
                formatted.append("{} {}".format(arrow, content_escaped))
                
            elif action_type == 'call':
                content_escaped = escape_renpy_formatting(str(content))
                arrow = arrows.get('call', 'CALL')
                formatted.append("{} {}".format(arrow, content_escaped))
                
            elif action_type == 'return':
                value = escape_renpy_formatting(str(value))
                arrow = arrows.get('return', '<-')
                if value and str(value) != 'end':
                    formatted.append("{} {}".format(arrow, value))
                else:
                    formatted.append("{} End".format(arrow))
                    
            elif action_type == 'function':
                arrow = arrows.get('function', 'FN')
                if full_code and len(full_code) <= 30:
                    full_code_escaped = escape_renpy_formatting(str(full_code))
                    formatted.append("{} {}".format(arrow, full_code_escaped))
                elif value and len(str(value)) <= 25:
                    value_escaped = escape_renpy_formatting(str(value))
                    formatted.append("{} {}".format(arrow, value_escaped))
                else:
                    try:
                        decrypted_code = renpy.python.quote_eval(full_code) if full_code else value
                        decrypted_escaped = escape_renpy_formatting(str(decrypted_code))
                        formatted.append("{} {}" .format(arrow, decrypted_escaped))
                    except:
                        # formatted.append("{color=" + color + "}" + arrow + " Code{/color}")
                        formatted.append("{} {}".format(arrow, "Code"))

                        
            elif action_type == 'condition':
                condition_escaped = escape_renpy_formatting(str(content))
                arrow = arrows.get('condition', '?')
                formatted.append("{} {}".format(arrow, condition_escaped))
                
            elif action_type == 'code':
                arrow = arrows.get('code', 'CODE')
                if full_code and len(full_code) <= 25:
                    full_code_escaped = escape_renpy_formatting(str(full_code))
                    formatted.append("{} {}".format(arrow, full_code_escaped))
                elif value and len(str(value)) <= 20:
                    value_escaped = escape_renpy_formatting(str(value))
                    formatted.append("{} {}".format(arrow, value_escaped))
                else:
                    formatted.append("{} Code".format(arrow))
                    
            else:
                content_escaped = escape_renpy_formatting(str(content)[:20])
                formatted.append("{}".format(str(content_escaped)))
        
        urwmsg("CONSEQUENCE FORMATTING: Formatted {} consequences after filtering".format(len(formatted)))
    
        if SHOW_ALL:
            final_consequences = formatted
            urwmsg("CONSEQUENCE FORMATTING: Show All enabled - displaying all {} consequences".format(len(final_consequences)))
        else:
            high_priority = []
            medium_priority = []
            low_priority = []
            
            for item in formatted:
                item_lower = item.lower()
                if any(keyword in item_lower for keyword in ['trust', 'love', 'relationship', 'affection', 're_', 'faith', 'points', 'money', 'health', 'reputation', '➤', '📞']):
                    high_priority.append(item)
                elif any(keyword in item_lower for keyword in ['=', '+', '-', '↩', 'true', 'false', '🔧', '⚙', '❓']):
                    medium_priority.append(item)
                else:
                    low_priority.append(item)
            
            urwmsg("CONSEQUENCE FORMATTING: Priority breakdown - High: {}, Medium: {}, Low: {}".format(
                len(high_priority), len(medium_priority), len(low_priority)))
            
            final_consequences = []
            
            for item in high_priority:
                if len(final_consequences) >= MAX_CONSEQUENCES:
                    break
                final_consequences.append(item)
            
            for item in medium_priority:
                if len(final_consequences) >= MAX_CONSEQUENCES:
                    break
                final_consequences.append(item)
            
            for item in low_priority:
                if len(final_consequences) >= MAX_CONSEQUENCES:
                    break
                final_consequences.append(item)
            
            urwmsg("CONSEQUENCE FORMATTING: Selected {} out of {} available consequences".format(
                len(final_consequences), len(formatted)))
        
        try:
            result = " | ".join(final_consequences)
            
            # Add "more" indicator as plain text - URW will style it
            if not SHOW_ALL and len(formatted) > len(final_consequences):
                extra_count = len(formatted) - len(final_consequences)
                result = result + " | +{} more".format(extra_count)
                urwmsg("CONSEQUENCE FORMATTING: Added '+{} more' indicator".format(extra_count))
            
            return result
        
        except Exception as e:
            urwmsg("CONSEQUENCE FORMATTING ERROR: {}, returning basic result".format(e))
            try:
                return " | ".join(final_consequences)
            except:
                urwmsg("CRITICAL CONSEQUENCE FORMATTING ERROR: returning empty string")
                return ""

    cleanup_counter = 0
    CLEANUP_INTERVAL = 100

    class URWText(renpy.Displayable):
        """
        URW text displayable with coloring
        """
        def __init__(self, text, size=25, color="#888", prefix="WT: ", **kwargs):
            super(URWText, self).__init__(**kwargs)
            self.text = text
            self.size = size
            self.base_color = color
            self.prefix = prefix
            
            # Text processing with coloring
            full_text = self.create_enhanced_text(text, size, color, prefix)
            self.child = renpy.text.text.Text(full_text, 
                                            outlines=[(2, "#000", 0, 0)],  # Add black outline
                                            font="DejaVuSans.ttf",
                                            **kwargs)
        
        def create_enhanced_text(self, text, size, base_color, prefix):
            """Create enhanced text with coloring for different consequence types"""
            
            # Color mapping for different consequence types
            colors = {
                'increase': '#4f4',      # Green for increases (+)
                'decrease': '#f44',      # Red for decreases (-)
                'assign': '#44f',        # Blue for assignments (=)
                'jump': '#f84',          # Orange for jumps (➤)
                'call': '#8f4',          # Light green for calls (📞)
                'return': '#f48',        # Pink for returns (↩)
                'condition': '#ff8',     # Yellow for conditions (❓)
                'function': '#af4',      # Light blue for functions (🔧)
                'code': '#ccc',          # Gray for code (⚙)
                'more': '#aaa'           # Lighter gray for "more" indicator
            }
            
            # Start with size and prefix in base color
            result = "{{size={}}}{{color={}}}{}{{/color}}".format(size, base_color, prefix)
            
            # Split text by | to process each consequence separately
            parts = text.split(' | ')
            
            for i, part in enumerate(parts):
                if i > 0:
                    result += " | "  # Simple separator without color tags
                
                part_color = base_color  # Default color
                
                # Determine color based on content
                if part.startswith('+'):
                    part_color = colors['increase']
                elif part.startswith('-') and not part.startswith('-{') and 'more' not in part:
                    part_color = colors['decrease']
                elif '=' in part and '==' not in part:
                    part_color = colors['assign']
                elif part.startswith('➤'):
                    part_color = colors['jump']
                elif part.startswith('📞'):
                    part_color = colors['call']
                elif part.startswith('↩'):
                    part_color = colors['return']
                elif part.startswith('❓'):
                    part_color = colors['condition']
                elif part.startswith('🔧'):
                    part_color = colors['function']
                elif part.startswith('⚙'):
                    part_color = colors['code']
                elif 'more' in part and '+' in part:
                    part_color = colors['more']
                
                # Add colored part
                result += "{{color={}}}{}{{/color}}".format(part_color, part)
            
            
            return result
        
        def render(self, width, height, st, at):
            return self.child.render(width, height, st, at)
        
        def visit(self):
            return [self.child]
    
    def urw_tag_handler(tag, argument, contents):
        """
        URW text tag with coloring
        Usage: {urw=size:25,color:#888,prefix:WT: }consequences{/urw}
        """
        new_list = []
        
        # Parse arguments (handle both lowercase and uppercase)
        size = 25
        color = "#888"
        prefix = "WT: "
        
        if argument:
            # Convert argument to lowercase for parsing to handle case transformations
            args = argument.lower().split(',')
            for arg in args:
                arg = arg.strip()
                if arg.startswith('size:'):
                    try:
                        size = int(arg.split(':')[1])
                    except:
                        size = 25
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
            # Create enhanced URW displayable with coloring
            urw_displayable = URWText(full_text, size, color, prefix)
            new_list.append((renpy.TEXT_DISPLAYABLE, urw_displayable))
        
        return new_list

    def register_transformation_immune_tag(tag_name, handler_function):
        """
        URW utility to register a custom text tag that's immune to case transformations
        
        Args:
            tag_name (str): Base tag name (e.g., "urw")
            handler_function: The tag handler function
        
        Returns:
            list: All registered tag variations
        """
        if not tag_name or not callable(handler_function):
            urwmsg("ERROR: Invalid parameters for tag registration")
            return []
        
        registered_variants = []
        tag_name = tag_name.lower()  # Normalize to lowercase
        
        try:
            # Generate all case combinations using bit manipulation
            # For n characters, we have 2^n combinations
            total_combinations = 2 ** len(tag_name)
            
            for i in range(total_combinations):
                variant = ""
                for char_index, char in enumerate(tag_name):
                    # Use bit at position char_index to determine case
                    if (i >> char_index) & 1:
                        variant += char.upper()
                    else:
                        variant += char.lower()
                
                # Register the variant
                config.custom_text_tags[variant] = handler_function
                registered_variants.append(variant)
            
            urwmsg("✓ Successfully registered {} case-immune variants for tag '{}'".format(
                len(registered_variants), tag_name))
            
            if dukeconfig.debug:
                urwmsg("  Registered variants: {}".format(", ".join(registered_variants)))
            
            return registered_variants
            
        except Exception as e:
            urwmsg("ERROR registering transformation-immune tag '{}': {}".format(tag_name, e))
            return []

    # Register URW tag variants
    urw_variants = register_transformation_immune_tag("urw", urw_tag_handler)

    original_menu = renpy.exports.menu
    
    def universal_walkthrough_menu_enhanced(items, set_expr=None, args=None, kwargs=None, item_arguments=None, **extra_kwargs):
        """walkthrough menu wrapper"""
        global cleanup_counter
        
        urwmsg("=== UNIVERSAL WALKTHROUGH MENU v1.5 ===")
        
        cleanup_counter += 1
        if cleanup_counter >= CLEANUP_INTERVAL:
            cleanup_counter = 0
            cleanup_menu_registry()
    
        if not hasattr(persistent, 'universal_walkthrough_enabled'):
            persistent.universal_walkthrough_enabled = True
        
        if not persistent.universal_walkthrough_enabled:
            return original_menu(items, set_expr, args, kwargs, item_arguments)
    
        try:
            menu_node = find_correct_menu_node_enhanced(items)
            
            if menu_node and hasattr(menu_node, 'items'):
                enhanced_items = []
                
                # Get strategy from cache instead of node attributes
                strategy, offset = get_strategy_from_node(menu_node)
                
                urwmsg("MENU ENHANCEMENT: Using strategy '{}' with offset {}".format(strategy, offset))
                urwmsg("Menu has {} items, processing {} choices".format(len(menu_node.items), len(items)))
                
                for i, item in enumerate(items):
                    if isinstance(item, (list, tuple)) and len(item) >= 1:
                        caption_text = item[0]
                        rest = item[1:] if len(item) > 1 else ()
                    else:
                        caption_text = str(item)
                        rest = ()
                    
                    enhanced_caption = renpy.substitute(caption_text)
                    
                    # Calculate correct menu item index based on strategy
                    if strategy == 'skip_first':
                        menu_item_index = i + 1  # Skip the question, so choice 0 -> menu item 1
                        urwmsg("SKIP_FIRST: Choice {} -> Menu item {}".format(i, menu_item_index))
                    elif strategy == 'skip_last':
                        menu_item_index = i  # Use same index, last item is ignored
                        urwmsg("SKIP_LAST: Choice {} -> Menu item {}".format(i, menu_item_index))
                    else:  # exact match
                        menu_item_index = i
                        urwmsg("EXACT: Choice {} -> Menu item {}".format(i, menu_item_index))
                    
                    # Get consequences from the correct menu item
                    if menu_item_index < len(menu_node.items):
                        menu_choice = menu_node.items[menu_item_index]
                        urwmsg("Processing choice '{}' -> menu item {} with content".format(caption_text, menu_item_index))
                        
                        if len(menu_choice) >= 3 and menu_choice[2]:
                            choice_block = menu_choice[2]
                            consequences = extract_choice_consequences(choice_block)
                            
                            if consequences:
                                # Use URW-safe formatting that doesn't rely on Ren'Py color tags
                                formatted_consequences = format_consequences_urw(consequences)
                                wt_size = persistent.universal_wt_text_size if hasattr(persistent, 'universal_wt_text_size') else 25
                                
                                # Put EVERYTHING inside the URW tag - this protects the entire walkthrough
                                enhanced_caption += "\n{{urw=size:{},color:#888,prefix:WT: }}{}{{/urw}}".format(
                                    wt_size, formatted_consequences
                                )
                                urwmsg("Added URW-protected consequences to choice '{}': {}".format(caption_text, formatted_consequences))
                            else:
                                urwmsg("No consequences found for choice '{}'".format(caption_text))
                        else:
                            urwmsg("No choice block found for menu item {}".format(menu_item_index))
                    else:
                        urwmsg("WARNING: menu_item_index {} out of range (menu has {} items)".format(
                            menu_item_index, len(menu_node.items)))
                    
                    if rest:
                        enhanced_items.append((enhanced_caption,) + rest)
                    else:
                        enhanced_items.append(enhanced_caption)
                
                return original_menu(enhanced_items, set_expr, args, kwargs, item_arguments)
        
        except RENPY_CONTROL_EXCEPTIONS:
            raise
        except Exception as e:
            urwmsg("Error in enhanced walkthrough menu: {}".format(e))
        
        return original_menu(items, set_expr, args, kwargs, item_arguments)
    
    # Replace the menu function
    renpy.exports.menu = universal_walkthrough_menu_enhanced

    def clear_walkthrough_caches():
        """Safely clear walkthrough caches"""
        global menu_registry, consequence_cache, consequence_cache_access
        
        try:
            menu_registry.clear()
            consequence_cache.clear()  
            consequence_cache_access.clear()
            node_strategy_cache.clear()
            
            if dukeconfig.debug: 
                print("Walkthrough caches cleared successfully")
        except Exception as e:
            if dukeconfig.debug: 
                print("Error clearing caches: {}".format(e))

    def log_memory_usage():
        """Debug function to log memory usage"""
        if dukeconfig.debug:
            print("Menu Registry: {} entries".format(len(menu_registry)))
            print("Consequence Cache: {} entries".format(len(consequence_cache)))

    def on_quit_game():
        """Clear volatile caches"""
        clear_walkthrough_caches()

    config.quit_callbacks.append(on_quit_game)

    if not hasattr(persistent, 'universal_walkthrough_enabled'):
        persistent.universal_walkthrough_enabled = True
    
    print("Universal Ren'Py Walkthrough System v1.5 Loaded for Game: {}-v{}".format(config.name, config.version))


## Styles ##
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
