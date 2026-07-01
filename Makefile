TICKER ?= NVDA
DATE   ?= $(shell date +%F)

UNIVERSE ?= universe.txt

.PHONY: run debug universe help

## run:      analyze a ticker (usage: make run TICKER=AAPL)
run:
	python run.py $(TICKER) --date $(DATE)

## debug:    same as run but streams the agent debate
debug:
	python run.py $(TICKER) --date $(DATE) --debug

## universe: analyze every ticker in universe.txt and print a ranked summary
universe:
	python run.py --universe $(UNIVERSE) --date $(DATE)

## help:  list targets
help:
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## //'
