FROM docker-auth-registry-dev.fly.dev/base/comfyui:latest AS runtime

COPY --link --from=docker-auth-registry-dev.fly.dev/comfyui/checkpoints/counterfeitv30_v30 / /
COPY --link --from=docker-auth-registry-dev.fly.dev/comfyui/embeddings/7dirtywords / /
COPY --link --from=docker-auth-registry-dev.fly.dev/comfyui/embeddings/easynegative / /
COPY --link --from=docker-auth-registry-dev.fly.dev/comfyui/embeddings/negative_hand-neg / /
COPY --link --from=docker-auth-registry-dev.fly.dev/comfyui/loras/ligne_claire_anime / /
COPY --link --from=docker-auth-registry-dev.fly.dev/comfyui/loras/pastelmixstylizedanime_pastelmixloraversion / /
COPY --link --from=docker-auth-registry-dev.fly.dev/comfyui/loras/reimulora-02 / /
COPY --link --from=docker-auth-registry-dev.fly.dev/comfyui/loras/ukiyo-e_1740-1840 / /
COPY --link --from=docker-auth-registry-dev.fly.dev/comfyui/loras/vaporwave / /
COPY --link --from=docker-auth-registry-dev.fly.dev/comfyui/vae/sdvaeforanime_v10 / /

RUN pip install Flask \
  && git clone https://github.com/TemryL/ComfyS3 /opt/comfyui/custom_nodes/comfys3 \
  && pip install -r /opt/comfyui/custom_nodes/comfys3/requirements.txt \
  && rm -rf /opt/comfyui/custom_nodes/comfys3/.git \
  && rm /opt/comfyui/custom_nodes/comfys3/.env \
  && touch /opt/comfyui/custom_nodes/comfys3/.env \
  && git clone https://github.com/Ttl/ComfyUi_NNLatentUpscale /opt/comfyui/custom_nodes/ComfyUi_NNLatentUpscale \
  && rm -rf /opt/comfyui/custom_nodes/ComfyUi_NNLatentUpscale/.git

COPY avatargen.py .
COPY startup.sh .

CMD ["/opt/comfyui/startup.sh"]