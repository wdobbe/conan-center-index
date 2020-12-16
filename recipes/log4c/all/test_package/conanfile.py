import os.path

from conans import ConanFile, CMake, tools


class Log4cTestConan(ConanFile):
    settings = "os", "compiler", "build_type", "arch"
    generators = "cmake"

    def build(self):
        cmake = CMake(self)
        cmake.configure()
        cmake.build()

    def test(self):
        if not tools.cross_building(self):
            bin_path = os.path.join("bin", "example1")
            command = bin_path + " 1"
            self.run(command, run_environment=True)
