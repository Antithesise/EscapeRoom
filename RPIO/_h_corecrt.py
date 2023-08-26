__all__ = [
    "defined", "restrict", "_CRT_WIDE", "__FILE__", "__FUNCTION__", "_CONST_RETURN",
    "_UCRT_DISABLED_WARNING_4412", "_UCRT_EXTRA_DISABLED_WARNINGS", "_UCRT_DISABLED_WARNINGS",
    "_UCRT_DISABLE_CLANG_WARNINGS", "_UCRT_RESTORE_CLANG_WARNINGS", "_ACRTIMP", "_ACRTIMP_ALT",
    "_DCRTIMP", "_CRTRESTRICT", "_CRTALLOCATOR", "_CRT_JIT_INTRINSIC", "_CRT_GUARDOVERFLOW",
    "_CRT_HYBRIDPATCHABLE", "_CRT_INLINE_PURE_SECURITYCRITICAL_ATTRIBUTE", "_WConst_return",
    "_CRT_ALIGN", "_Check_return_opt_", "_Check_return_wat_", "__crt_typefix", "_ARGMAX",
    "_TRUNCATE", "_CRT_INT_MAX", "_CRT_SIZE_MAX", "__FILEW__", "__FUNCTIONW__", "NULL",
    "_CRT_FUNCTIONS_REQUIRED", "_NO_INLINING", "_CRT_UNUSED", "_CRT_HAS_CXX17"
]

#from RPIO._h_vcruntime import *

from typing import Any, NamedTuple


defined = set(dir())


restrict = None
_CRT_WIDE = lambda x: None
__FILE__ = None
__FUNCTION__ = None
_CONST_RETURN = None

#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# Warning Suppression
#
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

# C4412: function signature contains type '_locale_t';
#        C++ objects are unsafe to pass between pure code and mixed or native. (/Wall)
if "_UCRT_DISABLED_WARNING_4412" not in defined:
    if "_M_CEE_PURE" in defined:
        _UCRT_DISABLED_WARNING_4412 = 4412
    else:
        _UCRT_DISABLED_WARNING_4412 = None

# Use _UCRT_EXTRA_DISABLED_WARNINGS to add additional warning suppressions to UCRT headers.
if "_UCRT_EXTRA_DISABLED_WARNINGS" not in defined:
    _UCRT_EXTRA_DISABLED_WARNINGS = None


# C4324: structure was padded due to __declspec(align()) (/W4)
# C4514: unreferenced inline function has been removed (/Wall)
# C4574: 'MACRO' is defined to be '0': did you mean to use '#if MACRO'? (/Wall)
# C4710: function not inlined (/Wall)
# C4793: 'function' is compiled as native code (/Wall and /W1 under /clr:pure)
# C4820: padding after data member (/Wall)
# C4995: name was marked #pragma deprecated
# C4996: __declspec(deprecated)
# C28719: Banned API, use a more robust and secure replacement.
# C28726: Banned or deprecated API, use a more robust and secure replacement.
# C28727: Banned API.
if "_UCRT_DISABLED_WARNINGS" not in defined:
    _UCRT_DISABLED_WARNINGS = [4324, _UCRT_DISABLED_WARNING_4412, 4514, 4574, 4710, 4793, 4820, 4995, 4996, 28719, 28726, 28727, _UCRT_EXTRA_DISABLED_WARNINGS]

if "_UCRT_DISABLE_CLANG_WARNINGS" not in defined:
    if "__clang__" in defined:
    # warning: declspec(deprecated) [-Wdeprecated-declarations]
    # warning: __declspec attribute 'allocator' is not supported [-Wignored-attributes]
    # warning: '#pragma optimize' is not supported [-Wignored-pragma-optimize]
    # warning: unknown pragma ignored [-Wunknown-pragmas]
        _UCRT_DISABLE_CLANG_WARNINGS = [_Pragma("clang diagnostic push"), _Pragma("clang diagnostic ignored \"-Wdeprecated-declarations\""), _Pragma("clang diagnostic ignored \"-Wignored-attributes\""), _Pragma("clang diagnostic ignored \"-Wignored-pragma-optimize\""), _Pragma("clang diagnostic ignored \"-Wunknown-pragmas\"")]
    else:
        _UCRT_DISABLE_CLANG_WARNINGS = None

if "_UCRT_RESTORE_CLANG_WARNINGS" not in defined:
    if "__clang__" in defined:
        _UCRT_RESTORE_CLANG_WARNINGS = _Pragma("clang diagnostic pop")
    else:
        _UCRT_RESTORE_CLANG_WARNINGS = None


#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# Annotation Macros
#
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
if "_ACRTIMP" not in defined:
    if "_CRTIMP" in defined and "_VCRT_DEFINED_CRTIMP" not in defined:
        _ACRTIMP = _CRTIMP
    elif "_CORECRT_BUILD" not in defined and "_DLL" in defined:
        _ACRTIMP = dllimport
    else:
        _ACRTIMP = None

# If you need the ability to remove __declspec(import) from an API, to support static replacement,
# declare the API using _ACRTIMP_ALT instead of _ACRTIMP.
if "_ACRTIMP_ALT" not in defined:
    if "_ACRTIMP" in defined:
        _ACRTIMP_ALT = _ACRTIMP
    else:
        _ACRTIMP_ALT = None

if "_DCRTIMP" not in defined:
    if "_CRTIMP" in defined and "_VCRT_DEFINED_CRTIMP" not in defined:
        _DCRTIMP = _CRTIMP
    elif "_CORECRT_BUILD" not in defined and "_DLL" in defined:
        _DCRTIMP = dllimport
    else:
        _DCRTIMP = None

    if "_CRTRESTRICT" not in defined:
        _CRTRESTRICT = None

else:
    _CRTRESTRICT = restrict

if "_MSC_VER" in defined and _MSC_VER >= 1900 and "_CORECRT_BUILD" not in defined:
    _CRTALLOCATOR = allocator
else:
    _CRTALLOCATOR = None

if {"_M_CEE", "_M_X64"}.issubset(defined):
    # This is only needed when managed code is calling the native APIs,
    # targeting the 64-bit runtime.
    _CRT_JIT_INTRINSIC = jitintrinsic
else:
    _CRT_JIT_INTRINSIC = None

# __declspec(guard(overflow)) enabled by /sdl compiler switch for CRT allocators
if "_GUARDOVERFLOW_CRT_ALLOCATORS" in defined:
    _CRT_GUARDOVERFLOW = guard(overflow)
else:
    _CRT_GUARDOVERFLOW = None

if {"_DLL", "_M_HYBRID"}.issubset(defined) and bool({"_CORECRT_BUILD", "_VCRT_BUILD"}.intersection(defined)):
    _CRT_HYBRIDPATCHABLE = hybrid_patchable
else:
    _CRT_HYBRIDPATCHABLE = None

# The CLR requires code calling other SecurityCritical code or using SecurityCritical types
# to be marked as SecurityCritical.
# _CRT_SECURITYCRITICAL_ATTRIBUTE covers this for internal function definitions.
# _CRT_INLINE_PURE_SECURITYCRITICAL_ATTRIBUTE is for inline pure functions defined in the header.
# This is clr:pure-only because for mixed mode we compile inline functions as native.
if "_M_CEE_PURE" in defined:
    _CRT_INLINE_PURE_SECURITYCRITICAL_ATTRIBUTE = "[System::Security::SecurityCritical]"
else:
    _CRT_INLINE_PURE_SECURITYCRITICAL_ATTRIBUTE = None

_WConst_return = _CONST_RETURN # For backwards compatibility

if "_CRT_ALIGN" not in defined:
    if "__midl" in defined:
        _CRT_ALIGN = lambda x: x
    else:
        _CRT_ALIGN = lambda x: align(x)

if {"_PREFAST_", "_CA_SHOULD_CHECK_RETURN"}.issubset(defined):
    _Check_return_opt_ = _Check_return_
elif "_Check_return_opt_" not in defined:
    _Check_return_opt_ = None

if {"_PREFAST_", "_CA_SHOULD_CHECK_RETURN_WER"}.issubset(defined):
    _Check_return_wat_ = _Check_return_
elif "_Check_return_wat_" not in defined:
    _Check_return_wat_ = None

if {"__midl", "MIDL_PASS"}.isdisjoint(defined) and "_PREFAST_" in defined:
    __crt_typefix = type("SAL_typefix(" + _CRT_STRINGIZE(type) + ")")
else:
    __crt_typefix = type



#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+
#
# Miscellaneous Stuff
#
#-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+-+

_ARGMAX =   100
_TRUNCATE = -1
_CRT_INT_MAX = 2147483647
_CRT_SIZE_MAX = -1

__FILEW__ =     _CRT_WIDE(__FILE__)
__FUNCTIONW__ = _CRT_WIDE(__FUNCTION__)


if "NULL" not in defined:
    NULL = 0

# CRT headers are included into some kinds of source files where only data type
# definitions and macro definitions are required but function declarations and
# inline function definitions are not.  These files include assembly files, IDL
# files, and resource files.  The tools that process these files often have a
# limited ability to process C and C++ code.  The _CRT_FUNCTIONS_REQUIRED macro
# is defined to 1 when we are compiling a file that actually needs functions to
# be declared (and defined, where applicable), and to 0 when we are compiling a
# file that does not.  This allows us to suppress declarations and definitions
# that are not compilable with the aforementioned tools.
if "_CRT_FUNCTIONS_REQUIRED" not in defined:
    if bool({"__assembler", "__midl", "RC_INVOKED"}.intersection(defined)):
        _CRT_FUNCTIONS_REQUIRED = 0
    else:
        _CRT_FUNCTIONS_REQUIRED = 1

if {"_CRT_FUNCTIONS_REQUIRED", "_NO_INLINING"}.isdisjoint(defined):
    _NO_INLINING = None # Suppress <tchar.h> inlines

if "_CRT_UNUSED" not in defined:
    _CRT_UNUSED = lambda x: x

if "_CRT_HAS_CXX17" not in defined:
    if "_MSVC_LANG" in defined:
        if _MSVC_LANG > 201402:
            _CRT_HAS_CXX17 = 1
        else: # _MSVC_LANG > 201402
            _CRT_HAS_CXX17 = 0
    else: # _MSVC_LANG
        _CRT_HAS_CXX17 = 0