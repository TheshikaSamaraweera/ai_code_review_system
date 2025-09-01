# AI Code Reviewer System Architecture

## High-Level Overview
- **Input**: Code file path via CLI in `main.py`.
- **Core Logic**: Hybrid analysis (rules, static tools, LLM) with iterative refinement.
- **Output**: Reports, refactored code, summaries.
- **Key Modules**: Agents (base_agent.py, code_smell_agent.py, etc.), Controls (enhanced_control_agent.py, recursive_controller.py), Utils (language_detector.py, etc.).
- **Dependencies**: Gemini LLM, LangGraph, static tools (pylint, etc.).
- **Noted Issues**: Python-centric (e.g., AST in agents); sequential execution; global memory.

## Detailed Flow Diagram (Text-Based)
Start (main.py):
  - Load code from file (utils/file_loader.py)
  - Detect language (utils/language_detector.py)
  - Analyze project context (utils/context_analyzer.py)
  - Phase 1: Initial Analysis (enhanced_control_agent.py)
    - Run QualityAgent (quality_agent.py) → LLM prompt for score/issues
    - Create temp file → Run StaticAnalysis (static_analysis_agent.py) → Subprocess tools (pylint, bandit, etc.)
    - Merge issues (error_comparator_agent.py) → Similarity check + deduplicate
    - Refine issues (critic_agent.py) → LLM critique
    - Display initial report (format_initial_analysis_report in main.py)
  - User Prompt: Proceed to refinement? (Y/N)
  If No: End with original code.
  If Yes: Phase 2: Iterative Refinement (recursive_controller.py via LangGraph)
    - Initialize state (CodeState with code, api_key, thresholds, etc.)
    - Loop (refinement_step):
      - Re-analyze quality + static + merge + critic
      - Prioritize issues (prioritize_issues)
      - Refactor (refactor_agent.py) → LLM-based fixes
      - Evaluate new score/issues
      - If conditions met (e.g., optimization criteria): Run OptimizationAgent (optimization_agent.py) → LLM suggestions → Refactor again
      - Update best code/score if improved
      - Check stopping criteria (should_continue: iterations, score >= threshold, no issues, stagnation, convergence)
    - Apply fixes interactively (cli/apply_fixes.py) → User feedback → Remember in memory
  - Final: Display session summary (memory/session_memory.py), save if chosen.
End.

## Refinements Suggested
- Add parallel execution for independent agents (e.g., quality and static).
- Make language handling dynamic (e.g., skip Python AST for non-Py code).
- Centralize error logging.