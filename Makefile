.PHONY: all build run check table clean
all: build run check table
build: ; python3 bench.py build
run: ; python3 bench.py run
quick: ; python3 bench.py run --quick
check: ; python3 bench.py check
table: ; python3 bench.py table
clean: ; rm -rf build
