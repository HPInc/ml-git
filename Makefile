ifeq ($(OS),Windows_NT)
    detected_OS := Windows
else
    detected_OS := $(shell sh -c 'uname 2>/dev/null || echo Unknown')
endif

all: build test

build:
ifeq ($(detected_OS),Windows)
	.\scripts\build\compile\build.bat
else
	./scripts/build/compile/build.sh
endif

test: test.unit test.integration
test.gdrive: test.unit test.integration.gdrive

test.unit:
ifeq ($(detected_OS),Windows)
	.\scripts\run_unit_tests.bat
else
	./scripts/run_unit_tests.sh
endif

test.integration:
ifeq ($(detected_OS),Windows)
	.\scripts\run_integration_tests.bat
else
	./scripts/run_integration_tests.sh
endif

test.integration.gdrive:
ifeq ($(detected_OS),Windows)
	.\scripts\run_integration_tests.bat --gdrive
else
	./scripts/run_integration_tests.sh --gdrive
endif
