# Avatargen

![](./static/img/example.jpg)

This is an example app built on top of [ComfyUI](https://www.comfy.org/) that generates placeholder avatar images in the style of [Gravatar](https://docs.gravatar.com/api/avatars/images/). Usage is simple:

```html
<img
  src="https://url.of.deployment/avatar/{md5sum(user_email)}"
  width="64"
  height="64"
/>
```

Generated images are cached in Tigris so that they don't need to be generated twice.

This is just a trivial example, but it shows how you can build your own complicated workflow with models stored in the Docker image, preventing you from having to download your models at runtime.

See the top-level documentation for more information.

## Deployment

This image requires at least 16 gigabytes of vram to function. It may work with less, but it has only been tested on a Tesla T4 (16 gigabytes of vram).

### Environment variables

| Name                    | Description                                              |
| :---------------------- | :------------------------------------------------------- |
| `AWS_ACCESS_KEY_ID`     | Your Tigris access key ID (`tid_`)                       |
| `AWS_SECRET_ACCESS_KEY` | Your Tigris secret access key (`tsec_`)                  |
| `AWS_ENDPOINT_URL_S3`   | Set this to `https://fly.storage.tigris.dev` for Tigris. |
| `AWS_REGION`            | Set this to `auto` for Tigris.                           |
| `BUCKET_NAME`           | Where avatar images should be cached.                    |

Without these variables, the application will not start and will crashloop.
