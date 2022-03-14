
-- WezTerm
-- https://wezfurlong.org/wezterm/

local wezterm = require 'wezterm'

return {
  -- Color scheme
  -- https://wezfurlong.org/wezterm/config/appearance.html
  --
  -- Dracula
  -- https://draculatheme.com
  --color_scheme = 'Dracula',

  --color_scheme = "nord-light",
  -- wezterm.get_builtin_color_schemes()

	warn_about_missing_glyphs = false,
	enable_scroll_bar = true,
}
