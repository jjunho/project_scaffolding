.PHONY: fmt lint test build check bump-version

# Version is passed from root Makefile
VERSION ?= 0.0.0

fmt:
	@echo "▶ Haskell fmt (ormolu)..."
	@stack exec -- ormolu --mode inplace $(shell find . -name '*.hs')

lint:
	@echo "▶ Haskell lint..."
	@stack exec -- hlint .

test:
	@echo "▶ Haskell test..."
	@stack test

build:
	@echo "▶ Haskell build..."
	@stack build

haddock:
	@echo "▶ Haskell haddock check (100% coverage required)..."
	@if stack exec -- stack haddock --no-haddock-deps 2>&1 | grep -v "Import" | grep -E "^ *([0-9]{1,2})% \("; then \
		echo "❌ Haddock coverage is not 100%"; \
		exit 1; \
	else \
		echo "✅ Haddock coverage 100%"; \
	fi

check: fmt lint
	@echo "▶ Haskell check (test + haddock)..."
	@# Run stack test, capture output to file to analyze twice
	@stack exec -- stack test --haddock --no-haddock-deps 2>&1 | tee /tmp/stack-output

clean:
	@echo "▶ Haskell clean..."
	@stack clean

bump-version:
	@echo "▶ Bumping backend version to $(VERSION)..."
	@sed -i "s/^version: .*/version: $(VERSION)/" package.yaml
