CONTAINER_NAME := "test_tromzo"
IMAGE_NAME := "tromzo:latest"
PORT := "8080"
POOL_SIZE := "10"


create_makefile:
	@echo "PORT=$(PORT)" > ./backend/.env
	@echo "POOL_SIZE=$(POOL_SIZE)" >> ./backend/.env

build: create_makefile
	@docker build . -t tromzo:latest

test: build
	@docker run --rm -it tromzo:latest pytest -v

run: build
	if [[ $$(docker ps -aq -f name=$(CONTAINER_NAME)) ]]; then \
        docker start $(CONTAINER_NAME); \
    else \
        docker run -p $(PORT):$(PORT) -d --name $(CONTAINER_NAME) $(IMAGE_NAME); \
    fi


.PHONY: create_makefile test run

