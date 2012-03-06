"""
Copyright (c) 2012, CCL Forensics
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:
    * Redistributions of source code must retain the above copyright
      notice, this list of conditions and the following disclaimer.
    * Redistributions in binary form must reproduce the above copyright
      notice, this list of conditions and the following disclaimer in the
      documentation and/or other materials provided with the distribution.
    * Neither the name of the CCL Forensics nor the
      names of its contributors may be used to endorse or promote products
      derived from this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL CCL FORENSICS BE LIABLE FOR ANY
DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
(INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND
ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
(INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""

# This example parses the "IconState.plist" file from an iOS device detailing
# the apps displayed on the Springboard homescreen.

import sys
import ccl_bplist

# Open the file specified at the command line
# ccl_bplist expects to see a binary stream, we'll also make it read-only
# hence the "rb" in our arguments.
f = open(sys.argv[1], "rb")

# Pass the file object to the "load" function in ccl_bplist. This gives us
# a python object representing the contents of the file.
plist = ccl_bplist.load(f)

# The IconState file's top level is a dictionary, and we're interested in
# the key "iconLists". This contains an array of arrays (each inner array
# representing a screen in the Springboard).
screens = plist["iconLists"]

# We can iterate through these screens in a for-loop
for screen in screens:
    # the variable "screen" will be an array containing both strings 
    # (denothing apps placed directly on the homescreen) and dictionaries
    # (which are folders on the homescreen). We can again iterate through
    # these elements in a for-loop
    for homescreen_element in screen:
        # Check if the element is a string - if so we can just print out
        # the name of the App, else if it's a dictionary we have to handle
        # it a little differently.
        if isinstance(homescreen_element, str):
            # String: just print out the app's name.
            print(homescreen_element)
        elif isinstance(homescreen_element, dict):
            # Dictionary: is a folder containing apps # the dictionary 
            # contains 2 keys:
            # "displayName": the name of the folder
            # "iconLists": an array of arrays - just as we've already seen
            
            # We can get the folder name directly:
            folder_name = homescreen_element["displayName"]
            print("Folder: " + folder_name)

            # And then iterate through the array of arrays under the 
            # "iconLists" key.
            folder_screens = homescreen_element["iconLists"]
            
            for folder_screen in folder_screens:
                for folder_element in folder_screen:
                    print("+\t" + folder_element)





