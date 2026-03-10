# Zero@Production Backup Naming Standard

Format:

file.bak_<module>_<change>_<state>_<timestamp>

Example:

executive.html.bak_ceo_modal_highlight_added_stable_20260308_115500
executive.html.bak_ceo_scenario_hover_before_patch_20260308_121000
executive.html.bak_signal_map_js_refactor_after_patch_20260308_121500

Fields:

module
- ceo_modal
- cfo_layer
- signal_map
- executive_dashboard

change
- highlight_added
- hover_upgrade
- risk_pulse
- narrative_update
- layout_fix

state
- before
- after
- stable
- rollback

Rules

before  → before editing code
after   → after editing but not fully verified
stable  → tested working state
rollback → safe point for returning
