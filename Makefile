.PHONY: clean clean_env data lint environment serve_nb sync_data_to_s3 sync_data_from_s3 github_remote

#################################################################################
# GLOBALS                                                                       #
#################################################################################
SHELL := /bin/bash

PROJECT_DIR := $(shell dirname $(realpath $(lastword $(MAKEFILE_LIST))))
BUCKET = None
PROJECT_NAME = veoibd-synapse-data-manager
PYTHON_INTERPRETER = python3
CONDA_ENV_NAME = veoibd_synapse
CONDA_ROOT = $(shell conda info --root)
CONDA_ENV_DIR = $(CONDA_ROOT)/envs/$(CONDA_ENV_NAME)
CONDA_ENV_PY = $(CONDA_ENV_DIR)/bin/python

ifeq (,$(shell which conda))
HAS_CONDA=False
else
HAS_CONDA=True
endif


ifeq (,$(shell which aria2c))
HAS_ARIA=False
else
HAS_ARIA=True
endif

ifeq (${CONDA_DEFAULT_ENV},$(CONDA_ENV_NAME))
PROJECT_CONDA_ACTIVE=True
else
PROJECT_CONDA_ACTIVE=False
endif


#################################################################################
# COMMANDS                                                                      #
#################################################################################

error_if_active_conda_env:
ifeq (True,$(PROJECT_CONDA_ACTIVE))
$(error "This project's conda env is active." )
endif

serve_nb:
	source activate $(CONDA_ENV_NAME); \
	jupyter notebook --notebook-dir notebooks


install: install_python install_r

uninstall: error_if_active_conda_env uninstall_python


install_python:
ifeq ($(CONDA_ENV_PY), $(shell which python))
	@echo "Project conda env already installed."
else
	conda create -n $(CONDA_ENV_NAME) --file requirements.txt --yes  && \
	source activate $(CONDA_ENV_NAME) && \
	python -m ipykernel install --user --name $(CONDA_ENV_NAME) --display-name "$(CONDA_ENV_NAME)" && \
	pip install -e .
endif


uninstall_python:
	source activate $(CONDA_ENV_NAME); \
	rm -rf $$(jupyter --data-dir)/kernels/$(CONDA_ENV_NAME); \
	rm -rf $(CONDA_ENV_DIR)




install_r:
	source activate $(CONDA_ENV_NAME) && \
	conda install --file requirements.r.txt --yes && \
	rm -rf $(CONDA_ENV_DIR)/share/jupyter/kernels/ir && \
	R -e "IRkernel::installspec(name = '$(CONDA_ENV_NAME)_R', displayname = '$(CONDA_ENV_NAME)_R')"

github_remote:
	bash github/push_to_new_remote.sh




## Install Python Dependencies
requirements: test_environment
	pip install -r requirements.txt

## Make Dataset
data:
	source activate $(CONDA_ENV_NAME); \
	python src/python/data/make_dataset.py

## Delete all compiled Python files
clean_bytecode:
	find . -name "__pycache__" -type d -exec rm -r {} \; ; \
	find . -name "*.pyc" -exec rm {} \;

## Lint using flake8
lint:
	flake8 --exclude=lib/,bin/,docs/conf.py .

## Upload Data to S3
sync_data_to_s3:
	aws s3 sync data/ s3://$(BUCKET)/data/

## Download Data from S3
sync_data_from_s3:
	aws s3 sync s3://$(BUCKET)/data/ data/

## Set up python interpreter environment
create_environment:
ifeq (True,$(HAS_CONDA))
		@echo ">>> Detected conda, creating conda environment."
ifeq (3,$(findstring 3,$(PYTHON_INTERPRETER)))
	conda create --name $(PROJECT_NAME) python=3.5
else
	conda create --name $(PROJECT_NAME) python=2.7
endif
		@echo ">>> New conda env created. Activate with:\nsource activate $(PROJECT_NAME)"
else
	@pip install -q virtualenv virtualenvwrapper
	@echo ">>> Installing virtualenvwrapper if not already intalled.\nMake sure the following lines are in shell startup file\n\
	export WORKON_HOME=$$HOME/.virtualenvs\nexport PROJECT_HOME=$$HOME/Devel\nsource /usr/local/bin/virtualenvwrapper.sh\n"
	@bash -c "source `which virtualenvwrapper.sh`;mkvirtualenv $(PROJECT_NAME) --python=$(PYTHON_INTERPRETER)"
	@echo ">>> New virtualenv created. Activate with:\nworkon $(PROJECT_NAME)"
endif

## Test python environment is setup correctly
test_environment:
	$(PYTHON_INTERPRETER) test_environment.py

#################################################################################
# Utils                                                                         #
#################################################################################
patch_viper_env_yml:
	diff -Naur viper/envs/environment.yml patches/viper/environment.yml > patches/viper/environment.yml.patch


#################################################################################
# PROJECT RULES                                                                 #
#################################################################################



#################################################################################
# Self Documenting Commands                                                     #
#################################################################################

.DEFAULT_GOAL := show-help

# Inspired by <http://marmelab.com/blog/2016/02/29/auto-documented-makefile.html>
# sed script explained:
# /^##/:
# 	* save line in hold space
# 	* purge line
# 	* Loop:
# 		* append newline + line to hold space
# 		* go to next line
# 		* if line starts with doc comment, strip comment character off and loop
# 	* remove target prerequisites
# 	* append hold space (+ newline) to line
# 	* replace newline plus comments by `---`
# 	* print line
# Separate expressions are necessary because labels cannot be delimited by
# semicolon; see <http://stackoverflow.com/a/11799865/1968>
.PHONY: show-help
show-help:
	@echo "$$(tput bold)Available rules:$$(tput sgr0)"
	@echo
	@sed -n -e "/^## / { \
		h; \
		s/.*//; \
		:doc" \
		-e "H; \
		n; \
		s/^## //; \
		t doc" \
		-e "s/:.*//; \
		G; \
		s/\\n## /---/; \
		s/\\n/ /g; \
		p; \
	}" ${MAKEFILE_LIST} \
	| LC_ALL='C' sort --ignore-case \
	| awk -F '---' \
		-v ncol=$$(tput cols) \
		-v indent=19 \
		-v col_on="$$(tput setaf 6)" \
		-v col_off="$$(tput sgr0)" \
	'{ \
		printf "%s%*s%s ", col_on, -indent, $$1, col_off; \
		n = split($$2, words, " "); \
		line_length = ncol - indent; \
		for (i = 1; i <= n; i++) { \
			line_length -= length(words[i]) + 1; \
			if (line_length <= 0) { \
				line_length = ncol - indent - length(words[i]) - 1; \
				printf "\n%*s ", -indent, " "; \
			} \
			printf "%s ", words[i]; \
		} \
		printf "\n"; \
	}' \
	| more $(shell test $(shell uname) = Darwin && echo '--no-init --raw-control-chars')
