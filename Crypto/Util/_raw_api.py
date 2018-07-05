# ===================================================================
#
# Copyright (c) 2014, Legrandin <helderijs@gmail.com>
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
#
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in
#    the documentation and/or other materials provided with the
#    distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS
# "AS IS" AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT
# LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS
# FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL THE
# COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING,
# BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN
# ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE
# POSSIBILITY OF SUCH DAMAGE.
# ===================================================================

import os
import imp

from Crypto.Util.py3compat import byte_string

try:
    from cffi import FFI

    ffi = FFI()
    null_pointer = ffi.NULL

    def load_lib(name, cdecl):
        """Load a shared library and return a handle to it.

        @name,  either an absolute path or the name of a library
                in the system search path.

        @cdecl, the C function declarations.
        """

        lib = ffi.dlopen(name)
        ffi.cdef(cdecl)
        return lib

    def c_ulong(x):
        """Convert a Python integer to unsigned long"""
        return x

    c_ulonglong = c_ulong

    def c_size_t(x):
        """Convert a Python integer to size_t"""
        return x

    def create_string_buffer(size):
        """Allocate the given amount of bytes"""
        return ffi.new("char[]", size)

    def get_c_string(c_string):
        """Convert a C string into a Python byte sequence"""
        return ffi.string(c_string)

    def get_raw_buffer(buf):
        """Convert a C buffer into a Python byte sequence"""
        return ffi.buffer(buf)[:]

    class VoidPointer(object):
        """Model a newly allocated pointer to void"""

        def __init__(self):
            self._pp = ffi.new("void *[1]")

        def get(self):
            return self._pp[0]

        def address_of(self):
            return self._pp

    Array = ffi.new("char[1]").__class__.__bases__

    backend = "cffi"

except ImportError:
    from ctypes import (CDLL, c_void_p, byref, c_ulong, c_ulonglong, c_size_t,
                        create_string_buffer)
    from ctypes.util import find_library
    from _ctypes import Array

    null_pointer = None

    def load_lib(name, cdecl):
        import platform
        bits, linkage = platform.architecture()
        if "." not in name and not linkage.startswith("Win"):
            full_name = find_library(name)
            if full_name is None:
                raise OSError("Cannot load library '%s'" % name)
            name = full_name
        return CDLL(name)

    def get_c_string(c_string):
        return c_string.value

    def get_raw_buffer(buf):
        return buf.raw

    class VoidPointer(object):
        """Model a newly allocated pointer to void"""

        def __init__(self):
            self._p = c_void_p()

        def get(self):
            return self._p

        def address_of(self):
            return byref(self._p)

    backend = "ctypes"

class SmartPointer(object):
    """Class to hold a non-managed piece of memory"""

    def __init__(self, raw_pointer, destructor):
        self._raw_pointer = raw_pointer
        self._destructor = destructor

    def get(self):
        return self._raw_pointer

    def release(self):
        rp, self._raw_pointer = self._raw_pointer, None
        return rp

    def __del__(self):
        if hasattr(self, "_raw_pointer") and self._raw_pointer is not None:
            self._destructor(self._raw_pointer)
            self._raw_pointer = None


def _get_mod_name(name, c_extension):

    comps = name.split(".")
    if comps[0] != "Crypto":
        raise ValueError("Only available for modules under 'Crypto'")

    comps = comps[1:-1] + [comps[-1] + c_extension]

    util_lib, _ = os.path.split(os.path.abspath(__file__))
    root_lib = os.path.join(util_lib, "..")

    return os.path.join(root_lib, *comps)


def load_pycryptodome_raw_lib(name, cdecl):
    """Load a shared library and return a handle to it.

    @name,  the name of the library expressed as a PyCryptodome module,
            for instance Crypto.Cipher._raw_cbc.

    @cdecl, the C function declarations.
    """

    for ext, mod, typ in imp.get_suffixes():
        if typ == imp.C_EXTENSION:
            try:
                return load_lib(_get_mod_name(name, ext), cdecl)
            except OSError:
                pass
    raise OSError("Cannot load native module '%s'" % name)

def expect_byte_string(data):
    if not byte_string(data) and not isinstance(data, Array):
        raise TypeError("Only byte strings can be passed to C code")
