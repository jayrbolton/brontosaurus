.PHONY: test

test:
		PYTHONPATH=. poetry run pytest -s -vv test
