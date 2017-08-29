#!/usr/bin/env python

"""
Fucntions for handling build and repackaging of clients.
Code 95% jacked from GRR. Rewritten to be standalone 
https://github.com/google/grr/blob/1a631a36b5bff2dd561f91ecc03624900ebb7297/grr/lib/build.py
"""

import cStringIO
import zipfile
import struct

def MakeSelfExtractingZip():
    """
    Repack the installer into the payload.
    """

    #create buffer for zip 
    zip_data = cStringIO.StringIO()
    #create zip file
    output_zip = zipfile.ZipFile(zip_data, mode="w", compression=zipfile.ZIP_DEFLATED)
    
    #open hello.txt and replace text with name
    hello_str = open("hello.txt", "rb").read()
    hello_str = hello_str.replace("{{INSERT NAME HERE}}", "Mike")

    #add files to zip file
    output_zip.writestr("hello.txt", hello_str, compress_type=zipfile.ZIP_STORED)
    output_zip.writestr("hello.exe", open("hello.exe", "rb").read(), compress_type=zipfile.ZIP_STORED)

    # The zip file comment is used by the self extractor to run
    # the installation script
    output_zip.comment = "$AUTORUN$>%s" % "hello.exe"
    output_zip.close()

    with open("out.exe", "wb") as fd:
        # First write the installer stub
        stub_data = cStringIO.StringIO()
        unzipsfx_stub = "unzipsfx-amd64.exe"
        stub_raw = open(unzipsfx_stub, "rb").read()

        # Check stub has been compiled with the requireAdministrator manifest.
        if "level=\"requireAdministrator" not in stub_raw:
            raise RuntimeError( "Bad unzip binary in use. Not compiled with the"
                                "requireAdministrator manifest option.")

        stub_data.write(stub_raw)

        # If in verbose mode, modify the unzip bins PE header to run in console
        # mode for easier debugging.
        SetPeSubsystem(stub_data, console=True)

        # Now patch up the .rsrc section to contain the payload.
        end_of_file = zip_data.tell() + stub_data.tell()

        # This is the IMAGE_SECTION_HEADER.Name which is also the start of
        # IMAGE_SECTION_HEADER.
        offset_to_rsrc = stub_data.getvalue().find(".rsrc")

        # IMAGE_SECTION_HEADER.PointerToRawData is a 32 bit int.
        stub_data.seek(offset_to_rsrc + 20)
        start_of_rsrc_section = struct.unpack("<I", stub_data.read(4))[0]

        # Adjust IMAGE_SECTION_HEADER.SizeOfRawData to span from the old start to
        # the end of file.
        stub_data.seek(offset_to_rsrc + 16)
        stub_data.write(struct.pack("<I", end_of_file - start_of_rsrc_section))

        # Concatenate stub and zip file.
        out_data = cStringIO.StringIO()
        out_data.write(stub_data.getvalue())
        out_data.write(zip_data.getvalue())

        # Then write the actual output file.
        fd.write(out_data.getvalue())


    print "Deployable binary generated at {0}".format("out.exe")

    return True

def SetPeSubsystem(fd, console=True):
    """Takes file like obj and returns (offset, value) for the PE subsystem."""
    current_pos = fd.tell()
    fd.seek(0x3c)  # _IMAGE_DOS_HEADER.e_lfanew
    header_offset = struct.unpack("<I", fd.read(4))[0]
    # _IMAGE_NT_HEADERS.OptionalHeader.Subsystem ( 0x18 + 0x44)
    subsystem_offset = header_offset + 0x5c
    fd.seek(subsystem_offset)
    if console:
        fd.write("\x03")
    else:
        fd.write("\x02")
    fd.seek(current_pos)

if __name__=="__main__" :
    MakeSelfExtractingZip()