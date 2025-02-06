#!/usr/bin/env bash

set -euo pipefail
! [ -z "${DEBUG}" ] && set -x

BUCKET_NAME="${BUCKET_NAME:-xe-models}"
DOCKER_REGISTRY="${DOCKER_REGISTRY:-docker-auth-registry-dev.fly.dev}"

function getModel() {
  # usage: getModel <model-kind> <model-name>
  local kind=$1
  local name=$2

  if [[ -z "${kind}" || -z "${name}" ]]; then
    echo "usage: getModel <model-kind> <model-name>"
    exit 1
  fi

  local model_fname="${kind}/${name}"

  if [[ -f "${model_fname}" ]]; then
    echo "Model ${model_fname} already exists."
    return
  fi

  aws s3 cp "s3://${BUCKET_NAME}/${model_fname}" "./${model_fname}"
}

function buildModel() {
  # usage: buildModel <model-kind> <model-name>
  local kind=$1
  local name=$2
  local name_without_extension="${name%.*}"

  if [[ -z "${kind}" || -z "${name}" ]]; then
    echo "usage: buildModel <model-kind> <model-name>"
    exit 1
  fi

  echo "Building model ${kind}/${name}..."

  dockerfileFname="Dockerfile.${kind}.${name_without_extension}"
  dockerTag="$(echo "comfyui/${kind}/${name_without_extension}" | tr '[:upper:]' '[:lower:]' | tr ' ' '-')"

  cat > "${dockerfileFname}" <<EOF
FROM scratch
COPY ${kind}/${name} /opt/comfyui/models/${kind}/${name}
EOF

  docker build -t "${DOCKER_REGISTRY}/${dockerTag}" -f "${dockerfileFname}" .
  docker push "${DOCKER_REGISTRY}/${dockerTag}"
}

for checkpoints in $(aws s3 ls "s3://${BUCKET_NAME}/checkpoints/" | awk '{print $4}'); do
  getModel checkpoints "${checkpoints}"
  buildModel checkpoints "${checkpoints}"
done

for embeddings in $(aws s3 ls "s3://${BUCKET_NAME}/embeddings/" | awk '{print $4}'); do
  getModel embeddings "${embeddings}"
  buildModel embeddings "${embeddings}"
done

for loras in $(aws s3 ls "s3://${BUCKET_NAME}/loras/" | awk '{print $4}'); do
  getModel loras "${loras}"
  buildModel loras "${loras}"
done

for vae in $(aws s3 ls "s3://${BUCKET_NAME}/vae/" | awk '{print $4}'); do
  getModel vae "${vae}"
  buildModel vae "${vae}"
done