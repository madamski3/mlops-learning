LOCAL_TAG:=$(shell date +"%Y-%m-%d_%H%M")
LOCAL_IMAGE_NAME:=ride-prediction-service:${LOCAL_TAG}

REMOTE_URI="891612547191.dkr.ecr.us-east-2.amazonaws.com/duration-model"
REMOTE_TAG="v2"
REMOTE_IMAGE_NAME=${REMOTE_URI}:${REMOTE_TAG}


code_formatting:
	echo "Formatting code..."
	isort .
	black .
	pylint --recursive=y .

unit_tests: code_formatting
	echo "Running unit tests..."
	pytest tests/

integration_tests: unit_tests
	echo "Running integration tests..."
	integration_tests/run.sh

build: integration_tests
	echo "Building local Docker image for deployment..."
	docker build -t ${LOCAL_IMAGE_NAME} .

deploy: build
	echo "Deploying application..."
	# Add deployment commands here

	docker tag ${LOCAL_IMAGE_NAME} ${REMOTE_IMAGE_NAME}
	docker push ${REMOTE_IMAGE_NAME}
