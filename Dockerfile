# FROM public.ecr.aws/lambda/python:3.13

# RUN pip install --no-cache-dir -U pip

# COPY requirements.txt ./

# RUN pip install --no-cache-dir -r requirements.txt && \
#     pip cache purge && \
#     rm -rf /root/.cache/pip/* && \
#     rm -rf /tmp/*

# COPY lambda_function.py ./

# CMD [ "lambda_function.lambda_handler" ]







# Build stage - use a standard Python image with build tools
FROM python:3.13-slim as builder

# Install build dependencies
RUN apt-get update && \
    apt-get install -y gcc g++ python3-dev && \
    rm -rf /var/lib/apt/lists/*

# Install Python packages to a target directory
COPY requirements.txt .
RUN pip install --no-cache-dir -U pip && \
    pip install --no-cache-dir --target /opt/python -r requirements.txt

# Runtime stage - use Lambda base image
FROM public.ecr.aws/lambda/python:3.13

# Copy installed packages from builder
COPY --from=builder /opt/python /opt/python
ENV PYTHONPATH=/opt/python:$PYTHONPATH

# Copy lambda function
COPY lambda_function.py ${LAMBDA_TASK_ROOT}

CMD ["lambda_function.lambda_handler"]