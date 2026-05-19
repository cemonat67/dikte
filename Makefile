.PHONY: validate status run

validate:
	./scripts/validate_repo.sh

status:
	git status
	git log --oneline -5

run:
	python3 -m uvicorn backend.main:app --reload --host 127.0.0.1 --port 8001
