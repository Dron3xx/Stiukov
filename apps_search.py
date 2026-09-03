import winreg
import os
import ctypes


# Version.dll stores metadata inside Windows executables, but it exposes that
# metadata through C functions rather than a Python object. ctypes lets this
# script call those functions directly without adding another Windows package.
version = ctypes.WinDLL("Version.dll")

# Tell ctypes the exact native signature so Python passes strings, integers,
# pointers, and the output buffer in the format expected by Windows.
version.GetFileVersionInfoW.argtypes = [
    ctypes.c_wchar_p,   # lpFileName
    ctypes.c_uint32,    # dwHandle
    ctypes.c_uint32,    # dwLen
    ctypes.c_void_p     # lpData
]

# Windows returns a success/failure integer from this function.
version.GetFileVersionInfoW.restype = ctypes.c_int

# This call is made before reading the version resource because the resource
# size varies between executable files and must be allocated dynamically.
version.GetFileVersionInfoSizeW.argtypes = [
    ctypes.c_wchar_p,
    ctypes.POINTER(ctypes.c_uint32)
]

# A zero size indicates that the executable has no readable version resource.
version.GetFileVersionInfoSizeW.restype = ctypes.c_uint32

# VerQueryValueW receives the loaded resource, a path inside that resource,
# and pointers where Windows writes the address and size of the result.
version.VerQueryValueW.argtypes = [
    ctypes.c_void_p,
    ctypes.c_wchar_p,
    ctypes.POINTER(ctypes.c_void_p),
    ctypes.POINTER(ctypes.c_uint)
]

# Windows reports whether the resource query succeeded as an integer.
version.VerQueryValueW.restype = ctypes.c_int

# App Paths contains executable locations registered for the current user, so
# it can find installed applications without searching every disk directory.
reg_path = r"Software\Microsoft\Windows\CurrentVersion\App Paths"

def read_file_metadata(file_path):
    try:
        # Windows needs an output variable for the file handle, even though the
        # handle is not used later by GetFileVersionInfoSizeW.
        handle = ctypes.c_uint32()

        # Ask Windows how many bytes are required for this file's complete
        # version resource. A fixed-size buffer would fail for larger files.
        size = version.GetFileVersionInfoSizeW(
            file_path,
            ctypes.byref(handle)
        )
        print(size)

        if size == 0:
            raise Exception("GetFileVersionInfoSizeW failed")

        else:
            # Store the native version resource in writable memory so its
            # address can be passed to the later VerQueryValueW calls.
            pBlock = ctypes.create_string_buffer(size)

            # Load the resource bytes into pBlock. The zero handle means the
            # file path is used directly; the size matches the allocation above.
            print(version.GetFileVersionInfoW(file_path, 0, size, pBlock))

            # VerQueryValueW writes a pointer to the requested value here and
            # writes that value's byte length into the separate size variable.
            buffer = ctypes.c_void_p()
            bufpoint = ctypes.byref(buffer)

            point = ctypes.c_uint()
            poipoint = ctypes.byref(point)

            # First query the translation table. It tells us which language and
            # code page must be included in the localized StringFileInfo path.
            result = version.VerQueryValueW(
                pBlock,
                r"\VarFileInfo\Translation",
                bufpoint,
                poipoint
            )

            print(result)
            print("buffer:", buffer)
            print("buffer.value:", buffer.value)
            print("point:", point.value)

            # The translation table contains pairs of 16-bit values. Defining
            # the native layout lets ctypes read those values from the pointer.
            class LANGANDCODEPAGE(ctypes.Structure):
                _fields_ = [
                    ("wLanguage", ctypes.c_ushort),
                    ("wCodePage", ctypes.c_ushort)
                ]

            translation = ctypes.cast(buffer, ctypes.POINTER(LANGANDCODEPAGE))
            language = translation.contents.wLanguage
            codepage = translation.contents.wCodePage

            print("Language:", language)
            print("CodePage:", codepage)

            # Resource paths use four-digit hexadecimal language and code-page
            # identifiers, not their decimal Python representations.
            print("Language HEX:", f"{language:04x}")
            print("CodePage HEX:", f"{codepage:04x}")

            # StringFileInfo is the localized text section. FileDescription is
            # the human-readable application name stored inside that section.
            sub_block = f"\\StringFileInfo\\{language:04x}{codepage:04x}\\FileDescription"

            print("SubBlock:", sub_block)

            # Querying text uses the same pointer pattern as the translation
            # lookup: Windows returns the address and length through pointers.
            sub_block_buffer = ctypes.c_void_p()
            sub_block_bufpoint = ctypes.byref(sub_block_buffer)

            sub_block_point = ctypes.c_uint()
            sub_block_poipoint = ctypes.byref(sub_block_point)

            # Retrieve the description using the language-specific resource
            # path assembled above.
            sub_block_result = version.VerQueryValueW(
                pBlock,
                sub_block,
                sub_block_bufpoint,
                sub_block_poipoint
            )

            # The returned address points to a wide-character string, so cast
            # it before reading the value as normal Python text.
            sub_block_value = ctypes.cast(sub_block_buffer, ctypes.c_wchar_p).value
            print("SubBlock Result:", sub_block_result)
            print("SubBlock Value:", sub_block_value)

    except Exception as error:
        print("Version info error:", error)

    
def search_registry_apps():
    # Enumerate App Paths because registered applications can be found even
    # when their installation folders are unknown to the disk scanner.
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, reg_path, 0, winreg.KEY_READ) as parent_key:
        i = 0
        apps = {}
        print("START")
        while True:
            try:
                # Each registry subkey represents one registered application.
                sub_key = winreg.EnumKey(parent_key, i)

                with winreg.OpenKey(parent_key, sub_key, 0, winreg.KEY_READ) as child_key:
                
                    # The unnamed registry value stores the executable path;
                    # registration may wrap that path in quotation marks.
                    value, _ = winreg.QueryValueEx(child_key, "")
                    value = value.lstrip('"').rstrip('"')
                    print("VALUE:", value)
                    print("sub_key:", sub_key)
                    print(os.path.exists(value))
                    print(os.path.isfile(value))
                    print(version)
                    read_file_metadata(value)
                i += 1
            except OSError:
                break

def search_disk():
    # Registry entries do not cover every executable, so recursively inspect
    # the configured library folders as a second discovery source.
    path = {
        "steam": r"D:\SteamLibrary\steamapps\common",
        "blizzard": r"D:\Blizzard",
        "cracks": r"D:\Cracks",
        "xbox": r"D:\XboxGames"
    }
    print(os.path.exists(path["steam"]))
    print(os.path.exists(path["blizzard"]))
    print(os.path.exists(path["cracks"]))
    print(os.path.exists(path["xbox"]))
    i = 0
    for name, value in path.items():
        if os.path.exists(value):
            # os.walk visits nested game/application folders without requiring
            # a separate search for every possible installation depth.
            for root, dirs, files in os.walk(value):
                for file in files:
                    if file.endswith(".exe"):
                        # Metadata is read only for executables because the
                        # Version.dll resource belongs to the file itself.
                        file_path = os.path.join(root,file)
                        print(f"Found executable: {file_path}")
                        read_file_metadata(file_path)
                        i += 1
                        print(i)

def analyze_apps():
    # Run both the registry and configured-folder searches together.
    search_registry_apps()
    search_disk()

# Run the disk scan when this script is executed.
search_disk()