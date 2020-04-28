// Define the SIP wrapper to the core library.

%Module(name=examples.core, use_limited_api=True)

%DefaultEncoding "ASCII"

%Platforms {Linux macOS Windows}

%If (Linux)
const char *what_am_i();
%MethodCode
    sipRes = "Linux";
%End
%End

%If (macOS)
const char *what_am_i();
%MethodCode
    sipRes = "macOS";
%End
%End

%If (Windows)
const char *what_am_i();
%MethodCode
    sipRes = "Windows";
%End
%End
