writeInfoLine ("progress…")
do ("Create Sound as pure tone...", "tone", 1, 0, 100, 44100, 440, 0.2, 0.01, 0.01)
stopwatch
do ("To Pitch...", 0, 75, 600)
appendInfoLine ("With progress bar: ", stopwatch)
do ("Create Sound as pure tone...", "tone", 1, 0, 100, 44100, 440, 0.2, 0.01, 0.01)
stopwatch
noprogress do ("To Pitch...", 0, 75, 600)
appendInfoLine ("Without progress bar: ", stopwatch)
