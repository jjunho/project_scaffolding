.PHONY: fmt lint test build check bump-version

VERSION ?= 0.0.0

fmt:
	@echo "▶ Elm fmt..."
	@# elm-format src/ --yes

lint:
	@echo "▶ Elm lint..."
	@# elm-review

test:
	@echo "▶ Elm test..."
	@# elm-test

build:
	@echo "▶ Elm build..."
	@mkdir -p dist
	@elm make src/Main.elm --output=dist/index.html

check: fmt lint test build

clean:
	@echo "▶ Elm clean..."
	@rm -rf elm-stuff dist

bump-version:
	@echo "▶ Elm versioning is manual in elm.json (package) or git tag (app)."
