# VHS tape — renders docs/demo.gif
#
# To regenerate the demo GIF:
#   brew install vhs       # or: go install github.com/charmbracelet/vhs@latest
#   vhs docs/demo.tape
#
# Output: docs/demo.gif (committed to the repo so README renders it).
# The simulation script is deterministic — no real Gmail auth needed.

Output docs/demo.gif

Set FontSize 14
Set Width 900
Set Height 560
Set Theme "Catppuccin Mocha"
Set Padding 20
Set TypingSpeed 20ms

Hide
Type "clear" Enter
Show

Type "bash docs/demo.sh" Enter
Sleep 14s
