import os, shutil
from conans import ConanFile, tools, AutoToolsBuildEnvironment

class Log4cConan(ConanFile):
    name = "log4c"
    description = "A C library for flexible logging to files, syslog and other destinations."
    topics = "conan", "logging"
    url = "https://bitbucket.org/tjec/log4c/src/master/"
    homepage = "http://sf.net/projects/log4c"
    license = "LGPL-2.1-only"
    exports_sources = ["patches/*"]
    settings = "os", "arch", "compiler", "build_type"
    options = { "shared": [True, False],
                "fPIC": [True, False]
    }
    default_options = {"shared": False,
                       "fPIC": False
    }
    requires = "expat/2.2.9"

    _autotools = None

    @property
    def _source_subfolder(self):
        return "source_subfolder"

    def source(self):
        tools.get(**self.conan_data["sources"][self.version])
        extracted_dir = self.name + "-" + self.version
        os.rename(extracted_dir, self._source_subfolder)

    def config_options(self):
        if self.settings.os == "Windows":
            del self.options.shared

    def configure(self):
        del self.settings.compiler.libcxx
        del self.settings.compiler.cppstd

    def build_requirements(self):
        if tools.os_info.is_windows and self.settings.compiler != "Visual Studio":
            if "CONAN_BASH_PATH" not in os.environ and tools.os_info.detect_windows_subsystem() != "msys2":
                self.build_requires("msys2/20190524")

    def _build_nmake(self):
        shutil.copy("Win32.Mak", os.path.join(self._source_subfolder, "Win32.Mak"))
        tools.replace_in_file(os.path.join(self._source_subfolder, "Win32.Mak"),
                              "\nccommon = -c ",
                              "\nccommon = -c -DLIBJPEG_BUILDING {}".format("" if self.options.shared else "-DLIBJPEG_STATIC "))
        with tools.chdir(self._source_subfolder):
            shutil.copy("jconfig.vc", "jconfig.h")
            make_args = [
                "nodebug=1" if self.settings.build_type != 'Debug' else "",
            ]
            # set flags directly in makefile.vc
            # cflags are critical for the library. ldflags and ldlibs are only for binaries
            if self.settings.compiler.runtime in ["MD", "MDd"]:
                tools.replace_in_file("makefile.vc", "(cvars)", "(cvarsdll)")
                tools.replace_in_file("makefile.vc", "(conlibs)", "(conlibsdll)")
            else:
                tools.replace_in_file("makefile.vc", "(cvars)", "(cvarsmt)")
                tools.replace_in_file("makefile.vc", "(conlibs)", "(conlibsmt)")
            target = "libjpeg.dll.lib" if self.options.shared else "libjpeg.lib"
            with tools.vcvars(self.settings):
                self.run("nmake -f makefile.vc {} {}".format(" ".join(make_args), target))

    def _configure_autotools(self):
        """For unix and mingw environments"""
        if self._autotools:
            return self._autotools
        self._autotools = AutoToolsBuildEnvironment(self, win_bash=tools.os_info.is_windows)
        config_args = [
            "--prefix={}".format(tools.unix_path(self.package_folder)),
        ]
        if self.options.shared:
            config_args.extend(["--enable-shared=yes", "--enable-static=no"])
        else:
            config_args.extend(["--enable-shared=no", "--enable-static=yes"])

        if self.settings.os == "Windows":
            mingw_arch = {
                "x86_64": "x86_64",
                "x86": "i686",
            }
            build_triplet = host_triplet = "{}-w64-mingw32".format(mingw_arch[str(self.settings.arch)])
            config_args.extend([
                "--build={}".format(build_triplet),
                "--host={}".format(host_triplet),
            ])

        self._autotools.configure(configure_dir=self._source_subfolder, args=config_args)
        return self._autotools

    def build(self):
        for patch in self.conan_data["patches"][self.version]:
            tools.patch(**patch)
        if self.settings.compiler == "Visual Studio":
            self._build_nmake()
        else:
            autotools = self._configure_autotools()
            autotools.make()

    def package(self):
        self.copy(pattern="COPYING", dst="licenses", src=self._source_subfolder)
        if self.settings.compiler == "Visual Studio":
            self.copy(pattern="log4c.h", dst="include", src=os.path.join(self._source_subfolder, "src"), keep_path=False)
            self.copy(pattern="*.h", dst="include/log4c", src=os.path.join(self._source_subfolder, 'src', 'log4c'), keep_path=False)
            self.copy(pattern="*.lib", dst="lib", src=self._source_subfolder, keep_path=False)
            self.copy(pattern="*.dll", dst="bin", src=self._source_subfolder, keep_path=False)
        else:
            autotools = self._configure_autotools()
            autotools.install()
            tools.rmdir(os.path.join(self.package_folder, "lib", "pkgconfig"))


    def package_info(self):
        if self.settings.compiler == "Visual Studio":
            lib = "log4c"
            if self.options.shared:
                lib += ".dll.lib"
            self.cpp_info.libs = [lib]
        else:
            self.cpp_info.libs = ["log4c"]

