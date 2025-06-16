############################################################
######### Universal Walkthrough System v1.2 ################
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
    developer = True

init -998 python:
    import collections.abc
    import builtins
    import re
    import weakref
    import time

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

    persistent.universal_wt_text_size = 25
    persistent.universal_wt_max_consequences = 2
    persistent.universal_wt_show_all_available = True

    consequence_cache = {}
    consequence_cache_access = {}
    MAX_CONSEQUENCE_CACHE = 200

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
            
            
            actual_line = linenumber
            
            if hasattr(renpy.game, 'context'):
                game_ctx = renpy.game.context()
                if hasattr(game_ctx, 'call_stack') and game_ctx.call_stack:
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
                except:
                    pass
            
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
            
            return {
                'filename': filename,
                'linenumber': linenumber,
                'execution_path': tuple(execution_path),
                'node_id': id(executing_node) if executing_node else None,
                'current_label': current_label,
                'timestamp': time.time()
            }
        except Exception as e:
            urwmsg("Error creating execution context: {}".format(e))
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
        """Find exact menu match - with strategy storage"""
        try:
            if not execution_context:
                return None
            
            script = renpy.game.script
            filename = execution_context['filename']
            linenumber = execution_context['linenumber']
            current_label = execution_context.get('current_label')
            
            urwmsg("Looking for menu match in {} at line {} (label: {})".format(
                filename, linenumber, current_label))
            
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

            # Process immediate candidates first (ULTRA PRECISE)
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
                
                # Store strategy on node
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
                    
                    # Store strategy on node
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
        """Register menu with enhanced context tracking"""
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
            menu_registry_access_times[menu_key] = time.time()
            
            urwmsg("Registered enhanced menu at {}:{} with fingerprint".format(
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
                            
                            menu_registry_access_times[menu_key] = time.time()
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
        try:
            urwmsg("=== ENHANCED MENU DETECTION v1.2 ===")
            
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
        """Enhanced consequence extraction"""
        choice_block_id = id(choice_block) if choice_block else 0

        cached_result = get_cached_consequences(choice_block_id)
        if cached_result is not None:
            return cached_result
        
        urwmsg("=== ENHANCED CONSEQUENCE ANALYZER ===")
        
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
                    for condition, block in stmt.entries:
                        sub_consequences = extract_choice_consequences(block)
                        if sub_consequences:
                            consequences.append(('condition', f'If {condition}', str(len(sub_consequences)), f'❓ Conditional'))
                
                # Skip visual/audio elements
                elif isinstance(stmt, (renpy.ast.Say, renpy.ast.Scene, renpy.ast.Show, renpy.ast.Hide, 
                                    renpy.ast.With, renpy.ast.ShowLayer, renpy.ast.Camera, renpy.ast.Transform,
                                    renpy.ast.Pass, renpy.ast.Label, renpy.ast.Menu, renpy.ast.UserStatement)):
                    continue
                
                else:
                    class_name = stmt.__class__.__name__
                    if class_name not in ['Play', 'Stop', 'Queue', 'Music', 'Sound', 'Voice', 'Audio',
                                        'Comment', 'Translate', 'TranslateBlock', 'EndTranslate']:
                        for attr in ['target', 'label', 'expression', 'name', 'value']:
                            if hasattr(stmt, attr):
                                value = getattr(stmt, attr)
                                if value and not str(value).startswith('_'):
                                    consequences.append(('unknown', f'{attr}: {str(value)}', '', f'{class_name.lower()} {value}'))
                                    break
            
            except Exception as e:
                urwmsg("Error processing statement {}: {}".format(i, e))
                continue
        
        cache_consequences(choice_block_id, consequences)
        return consequences

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
        """Python source parsing with AST"""
        consequences = []
        
        if not source:
            return consequences
        
        try:
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
        
        except (SyntaxError, Exception):
            pass
        
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
        """Fallback regex parsing"""
        consequences = []
        
        code_lines = [line.strip() for line in source.split('\n') if line.strip()]
        
        for line in code_lines:
            if '+=' in line:
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
            consequence_cache_access[choice_block_id] = time.time()
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
        consequence_cache_access[choice_block_id] = time.time()

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

    def format_consequences(consequences):
        """Format consequences for display"""
        if not consequences:
            return ""
    
        MAX_CONSEQUENCES = persistent.universal_wt_max_consequences
        SHOW_ALL = persistent.universal_wt_show_all_available
        
        urwmsg("CONSEQUENCE FORMATTING: MAX_CONSEQUENCES = {}, SHOW_ALL = {}".format(MAX_CONSEQUENCES, SHOW_ALL))
        urwmsg("CONSEQUENCE FORMATTING: Total consequences available = {}".format(len(consequences)))
        
        formatted = []
        colors = {
            'increase': '#4f4',
            'decrease': '#f44',
            'assign': '#44f',
            'boolean': '#4af',
            'jump': '#f84',
            'call': '#8f4',
            'return': '#f48',
            'function': '#af4',
            'condition': '#ff8',
            'code': '#ccc',
            'unknown': '#f8f'
        }
        
        arrows = {
            'jump': "{font=DejaVuSans.ttf}➤{/font}",
            'call': "{font=TwemojiCOLRv0.ttf}📞{/font}",
            'return': "{font=DejaVuSans.ttf}↩{/font}",
            'function': "{font=TwemojiCOLRv0.ttf}🔧{/font}",
            'condition': "{font=TwemojiCOLRv0.ttf}❓{/font}",
            'code': "{font=DejaVuSans.ttf}⚙{/font}"
        }
    
        # Format all consequences first - NO DUPLICATES
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
    
            # Create unique identifier for this consequence
            consequence_id = (action_type, str(content), str(value))
            if consequence_id in seen_consequences:
                continue  # Skip duplicates
            seen_consequences.add(consequence_id)
                
            color = colors.get(action_type, '#fff')
            
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
                    try:
                        decrypted_code = renpy.python.quote_eval(full_code) if full_code else value
                        formatted.append("{color=" + color + "}" + arrow + " " + str(decrypted_code) + "{/color}")
                    except:
                        formatted.append("{color=" + color + "}" + arrow + " Code{/color}")
                        
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
        
        urwmsg("CONSEQUENCE FORMATTING: Formatted {} unique consequences".format(len(formatted)))
    
        
        if SHOW_ALL:
            # Show ALL consequences when enabled, no limits
            final_consequences = formatted
            urwmsg("CONSEQUENCE FORMATTING: Show All enabled - displaying all {} consequences".format(len(final_consequences)))
        else:
            # Priority-based selection without complex ratios
            high_priority = []
            medium_priority = []
            low_priority = []
            
            for item in formatted:
                item_lower = item.lower()
                if any(keyword in item_lower for keyword in ['trust', 'love', 'relationship', 'affection', 're_', 'faith', 'points', 'money', 'health', 'reputation', '➤', '📞']):
                    high_priority.append(item)
                elif any(keyword in item_lower for keyword in ['=', '+', '-', '↩', 'true', 'false', '🔧', '⚙']):
                    medium_priority.append(item)
                else:
                    low_priority.append(item)
            
            urwmsg("CONSEQUENCE FORMATTING: Priority breakdown - High: {}, Medium: {}, Low: {}".format(
                len(high_priority), len(medium_priority), len(low_priority)))
            
            # Take consequences in priority order up to the limit
            final_consequences = []
            
            # Add high priority first
            for item in high_priority:
                if len(final_consequences) >= MAX_CONSEQUENCES:
                    break
                final_consequences.append(item)
            
            # Add medium priority
            for item in medium_priority:
                if len(final_consequences) >= MAX_CONSEQUENCES:
                    break
                final_consequences.append(item)
            
            # Add low priority if still have room
            for item in low_priority:
                if len(final_consequences) >= MAX_CONSEQUENCES:
                    break
                final_consequences.append(item)
            
            urwmsg("CONSEQUENCE FORMATTING: Selected {} out of {} available consequences".format(
                len(final_consequences), len(formatted)))
        
        # Create the result with proper error handling
        try:
            result = " | ".join(final_consequences)
            
            # Show "+X more" indicator only when there are actually more consequences hidden
            if not SHOW_ALL and len(formatted) > len(final_consequences):
                extra_count = len(formatted) - len(final_consequences)
                # Use safer string concatenation to avoid markup conflicts
                more_indicator = " {{color=#888}}{{size=16}} | +{} more{{/size}}{{/color}}".format(extra_count)
                result = result + more_indicator
                urwmsg("CONSEQUENCE FORMATTING: Added '+{} more' indicator".format(extra_count))
            
            return result
        
        except Exception as e:
            # FALLBACK: If there's any formatting error, return basic result without "+X more"
            urwmsg("CONSEQUENCE FORMATTING ERROR: {}, returning basic result".format(e))
            try:
                return " | ".join(final_consequences)
            except:
                urwmsg("CRITICAL CONSEQUENCE FORMATTING ERROR: returning empty string")
                return ""

    cleanup_counter = 0
    CLEANUP_INTERVAL = 100

    original_menu = renpy.exports.menu
    
    def universal_walkthrough_menu_enhanced(items, set_expr=None, args=None, kwargs=None, item_arguments=None, **extra_kwargs):
        """Enhanced walkthrough menu wrapper with better accuracy"""
        global cleanup_counter
        
        urwmsg("=== KNOX ENHANCED UNIVERSAL WALKTHROUGH MENU v1.2 ===")
        
        cleanup_counter += 1
        if cleanup_counter >= CLEANUP_INTERVAL:
            cleanup_counter = 0
            cleanup_menu_registry()
    
        if not hasattr(persistent, 'universal_walkthrough_enabled'):
            persistent.universal_walkthrough_enabled = True
        
        if not persistent.universal_walkthrough_enabled:
            return original_menu(items, set_expr, args, kwargs, item_arguments)
    
        try:
            # Use enhanced menu finding
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
                                formatted_consequences = format_consequences(consequences)
                                enhanced_caption += "\n{{size={}}}{{color=#888}}WT:{{/color}} ".format(
                                    persistent.universal_wt_text_size if hasattr(persistent, 'universal_wt_text_size') else 25
                                ) + formatted_consequences + "{/size}"
                                urwmsg("Added consequences to choice '{}': {}".format(caption_text, formatted_consequences))
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
                print("Enhanced walkthrough caches cleared successfully")
        except Exception as e:
            if dukeconfig.debug: 
                print("Error clearing caches: {}".format(e))

    def log_memory_usage():
        """Debug function to log memory usage"""
        if dukeconfig.developer:
            print("Menu Registry: {} entries".format(len(menu_registry)))
            print("Consequence Cache: {} entries".format(len(consequence_cache)))

    def on_quit_game():
        """Clear volatile caches"""
        clear_walkthrough_caches()

    config.quit_callbacks.append(on_quit_game)

    if not hasattr(persistent, 'universal_walkthrough_enabled'):
        persistent.universal_walkthrough_enabled = True
    
    print("Universal Ren'Py Walkthrough System v1.2 (Enhanced) Loaded")

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
                
                text "{color=#4a9eff}{size=32}{b}Universal Walkthrough System v1.2{/b}{/size}{/color}":
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
    