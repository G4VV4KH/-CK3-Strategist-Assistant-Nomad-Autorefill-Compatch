# Reproducing the military-window merge

With Git and Python installed, run from the repository root:

    python tests/verify_merge.py --vanilla "<CK3 game directory>" --strategist "<Strategist Assistant 0.1.2 runtime>" --nomad "<Nomad Autorefill 0.1.3 runtime>"

The check verifies a single shared runtime path and compares the shipped file with a clean three-way merge. It normalizes line endings. The shipping GUI was also exercised in CK3 1.21.0.3 with both parent mods in an English nomadic campaign. Fourteen checks covered reinforcement preferences, army planning controls and actual calendar ticks. Views outside this scenario were not part of that test.
