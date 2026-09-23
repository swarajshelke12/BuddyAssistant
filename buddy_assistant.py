#!/usr/bin/env python3
"""
Buddy Agent — Voice-Controlled Laptop Operator
Primary entry point for Buddy Agent.
"""

from hermes_assistant import BuddyAgent, Hermes, run_test_mode

if __name__ == "__main__":
    import sys
    if "--test" in sys.argv:
        run_test_mode()
    else:
        BuddyAgent().run()
