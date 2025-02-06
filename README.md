# AI model storage in docker images example

AI models are big and downloading them at runtime can add latency to your cold start times. What if you could just bake them into your production images? This example shows you how to do that with [your own Docker registry](https://www.tigrisdata.com/docs/apps/docker-registry/) on top of Tigris.

This example is built on top of [ComfyUI](https://www.comfy.org/). It generates placeholder avatar images in the style of [Gravatar](https://docs.gravatar.com/api/avatars/images/) and can be used as a drop-in replacement for Gravatar in your web applications.

## Docker registry

Follow the directions [to create your own Docker registry](https://www.tigrisdata.com/docs/apps/docker-registry/) on top of Tigris. The domain name of your registry is where you will push images to. In this article, I'll refer to this registry host as `registry.domain.tld`.

### Building the base runner image

Build and push the ComfyUI image:

```text
docker build -t registry.domain.tld/base/comfyui comfyui
docker push registry.domain.tld/base/comfyui
```

### Building model images

I've put all the models for this demo in the public bucket `xe-models`. If you want to use your own models, upload them into a bucket [with the directory structure ComfyUI expects](https://docs.comfy.org/essentials/core-concepts/models). Then build and push all of the model images:

```text
cd models
DOCKER_REGISTRY=registry.domain.tld bash fetch-and-build.sh
```

### Building avatargen image

Go into the `server` folder and run this command on the Dockerfile:

```bash
cat Dockerfile | sed 's$docker-auth-registry-dev.fly.dev$registry.domain.tld$g' > Dockerfile.run
```

Then build and push your image:

```text
docker build -t registry.domain.tld/apps/avatargen --file Dockerfile.run .
docker push registry.domain.tld/apps/avatargen
```

## Deploying

This example needs at least 16 gigabytes of vram (video memory / framebuffer) to run. From my understanding, it can work on a GPU with as little as 12 gigabytes of vram, but it has only been tested on an AWS [`g4dn.xlarge`](https://instances.vantage.sh/aws/ec2/g4dn.xlarge) with a Tesla T4 (16 gigabytes of video memory). Choose a deployment target that gives you at least that much video memory. Here's what you'd need with a few common providers:

| Cloud         | Instance type                       |
| :------------ | :---------------------------------- |
| AWS           | `g4dn.xlarge` or larger             |
| Digital Ocean | `H100x1` or larger                  |
| Runpod        | Tesla V100 or higher (n>=16GB vram) |

All the generated avatar images are going to be stored in a bucket. [Create a private bucket](https://www.tigrisdata.com/docs/buckets/create-bucket/) (such as `tigris-example`) and [an access key](https://www.tigrisdata.com/docs/iam/create-access-key/) with Editor permissions on that bucket.

Make sure your deployment environment has logged into your registry.

Avatargen is configured with environment variables. Here are the environment variables that Avatargen reads from.

| Name                    | Description                                              |
| :---------------------- | :------------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | Your Tigris access key ID (`tid_`)                       |
| `AWS_SECRET_ACCESS_KEY` | Your Tigris secret access key (`tsec_`)                  |
| `AWS_ENDPOINT_URL_S3`   | Set this to `https://fly.storage.tigris.dev` for Tigris. |
| `AWS_REGION`            | Set this to `auto` for Tigris.                           |
| `BUCKET_NAME`           | Where avatar images should be cached.                    |

Launch it somehow, and then open up the URL in your favorite browser!

When it's up, the demo should look like this:

![A screenshot of "Avatargen" with a picture of a brown-haired anime woman in a futuristic hoodie](./img/example.png)

Type words into the text box, wait a few seconds, and the computer will surprise you!
