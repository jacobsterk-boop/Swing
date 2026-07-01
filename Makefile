TICKER ?= NVDA
DATE   ?= $(shell date +%F)

.PHONY: run debug help

## run:   analyze a ticker (usage: make run TICKER=AAPL)
run:
	python run.py $(TICKER) --date $(DATE)

## debug: same as run but streams the agent debate
debug:
	python run.py $(TICKER) --date $(DATE) --debug

## help:  list targets
help:
	@grep -E '^## ' $(MAKEFILE_LIST) | sed 's/## //'
