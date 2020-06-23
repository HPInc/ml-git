ifeq ($(OS),Windows_NT)
    detected_OS := Windows
else
    detected_OS := $(shell sh -c 'uname 2>/dev/null || echo Unknown')
endif

.PHONY: all
all: test build

.PHONY: clean
clean:
ifeq ($(detected_OS),Windows)
	IF EXIST "%CD%\dist\" RMDIR /S /Q %CD%\dist
	IF EXIST "%CD%\build\" RMDIR /S /Q %CD%\build
else
	rm -rf dist build
endif

.PHONY: build
build: clean
ifeq ($(detected_OS),Windows)
	.\scripts\build\compile\build.bat
else
	./scripts/build/compile/build.sh
endif

.PHONY: test
test: test.unit test.integration

.PHONY: test.gdrive
test.gdrive: test.unit test.integration.gdrive

.PHONY: test.unit
test.unit:
ifeq ($(detected_OS),Windows)
	.\scripts\run_unit_tests.bat
else
	./scripts/run_unit_tests.sh
endif

.PHONY: test.integration
test.integration:
ifeq ($(detected_OS),Windows)
	.\scripts\run_integration_tests.bat
else
	./scripts/run_integration_tests.sh
endif

.PHONY: test.integration.gdrive
test.integration.gdrive:
ifeq ($(detected_OS),Windows)
	.\scripts\run_integration_tests.bat --gdrive
else
	./scripts/run_integration_tests.sh --gdrive
endif
