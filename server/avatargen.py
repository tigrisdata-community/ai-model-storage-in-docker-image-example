import os
import random
import sys
from typing import Sequence, Mapping, Any, Union
import torch
import boto3
import random
from flask import Flask, jsonify, request, redirect


app = Flask(__name__)


def get_value_at_index(obj: Union[Sequence, Mapping], index: int) -> Any:
    """Returns the value at the given index of a sequence or mapping.

    If the object is a sequence (like list or string), returns the value at the given index.
    If the object is a mapping (like a dictionary), returns the value at the index-th key.

    Some return a dictionary, in these cases, we look for the "results" key

    Args:
        obj (Union[Sequence, Mapping]): The object to retrieve the value from.
        index (int): The index of the value to retrieve.

    Returns:
        Any: The value at the given index.

    Raises:
        IndexError: If the index is out of bounds for the object and the object is not a mapping.
    """
    try:
        return obj[index]
    except KeyError:
        return obj["result"][index]


def find_path(name: str, path: str = None) -> str:
    """
    Recursively looks at parent folders starting from the given path until it finds the given name.
    Returns the path as a Path object if found, or None otherwise.
    """
    # If no path is given, use the current working directory
    if path is None:
        path = os.getcwd()

    # Check if the current directory contains the name
    if name in os.listdir(path):
        path_name = os.path.join(path, name)
        print(f"{name} found: {path_name}")
        return path_name

    # Get the parent directory
    parent_directory = os.path.dirname(path)

    # If the parent directory is the same as the current directory, we've reached the root and stop the search
    if parent_directory == path:
        return None

    # Recursively call the function with the parent directory
    return find_path(name, parent_directory)


def add_comfyui_directory_to_sys_path() -> None:
    """
    Add 'ComfyUI' to the sys.path
    """
    comfyui_path = find_path("ComfyUI")
    if comfyui_path is not None and os.path.isdir(comfyui_path):
        sys.path.append(comfyui_path)
        print(f"'{comfyui_path}' added to sys.path")


def add_extra_model_paths() -> None:
    """
    Parse the optional extra_model_paths.yaml file and add the parsed paths to the sys.path.
    """
    try:
        from server import load_extra_path_config
    except ImportError:
        print(
            "Could not import load_extra_path_config from main.py. Looking in utils.extra_config instead."
        )
        try:
            from utils.extra_config import load_extra_path_config
        except ImportError:
            return


    extra_model_paths = find_path("extra_model_paths.yaml")

    if extra_model_paths is not None:
        load_extra_path_config(extra_model_paths)
    else:
        print("Could not find the extra_model_paths config file.")


add_comfyui_directory_to_sys_path()
add_extra_model_paths()


def import_custom_nodes() -> None:
    """Find all custom nodes in the custom_nodes folder and add those node objects to NODE_CLASS_MAPPINGS

    This function sets up a new asyncio event loop, initializes the PromptServer,
    creates a PromptQueue, and initializes the custom nodes.
    """
    import asyncio
    import execution
    from nodes import init_extra_nodes
    import server

    # Creating a new event loop and setting it as the default loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    # Creating an instance of PromptServer with the loop
    server_instance = server.PromptServer(loop)
    execution.PromptQueue(server_instance)

    # Initializing custom nodes
    init_extra_nodes()


from nodes import (
    VAEDecode,
    KSampler,
    NODE_CLASS_MAPPINGS,
    VAELoader,
    VAEEncode,
    CheckpointLoaderSimple,
    CLIPTextEncode,
    EmptyLatentImage,
    LoraLoader,
)


def generate_image(prompt: str, negative_prompt: str):
    import_custom_nodes()
    with torch.inference_mode():
        checkpointloadersimple = CheckpointLoaderSimple()
        checkpointloadersimple_4 = checkpointloadersimple.load_checkpoint(
            ckpt_name="counterfeitV30_v30.safetensors"
        )

        emptylatentimage = EmptyLatentImage()
        emptylatentimage_5 = emptylatentimage.generate(
            width=512, height=512, batch_size=1
        )

        loraloader = LoraLoader()
        loraloader_51 = loraloader.load_lora(
            lora_name="pastelMixStylizedAnime_pastelMixLoraVersion.safetensors",
            strength_model=1,
            strength_clip=1,
            model=get_value_at_index(checkpointloadersimple_4, 0),
            clip=get_value_at_index(checkpointloadersimple_4, 1),
        )

        loraloader_61 = loraloader.load_lora(
            lora_name="ligne_claire_anime.safetensors",
            strength_model=1,
            strength_clip=1,
            model=get_value_at_index(loraloader_51, 0),
            clip=get_value_at_index(loraloader_51, 1),
        )

        cliptextencode = CLIPTextEncode()
        cliptextencode_6 = cliptextencode.encode(
            text=f"(masterpiece, best quality), {prompt}",
            clip=get_value_at_index(loraloader_61, 1),
        )

        vaeloader = VAELoader()
        vaeloader_12 = vaeloader.load_vae(vae_name="sdVAEForAnime_v10.pt")

        cliptextencode_38 = cliptextencode.encode(
            text=f"embedding:easynegative, embedding:negative_hand-neg, embedding:7dirtywords, {negative_prompt}",
            clip=get_value_at_index(loraloader_61, 1),
        )

        ksampler = KSampler()
        ksampler_3 = ksampler.sample(
            seed=random.randint(1, 2**64),
            steps=26,
            cfg=6,
            sampler_name="dpmpp_2m",
            scheduler="karras",
            denoise=1,
            model=get_value_at_index(loraloader_61, 0),
            positive=get_value_at_index(cliptextencode_6, 0),
            negative=get_value_at_index(cliptextencode_38, 0),
            latent_image=get_value_at_index(emptylatentimage_5, 0),
        )

        vaedecode = VAEDecode()
        vaedecode_47 = vaedecode.decode(
            samples=get_value_at_index(ksampler_3, 0),
            vae=get_value_at_index(vaeloader_12, 0),
        )

        imagesharpen = NODE_CLASS_MAPPINGS["ImageSharpen"]()
        imagesharpen_85 = imagesharpen.sharpen(
            sharpen_radius=1,
            sigma=1,
            alpha=1,
            image=get_value_at_index(vaedecode_47, 0),
        )

        saveimages3 = NODE_CLASS_MAPPINGS["SaveImageS3"]()

        vaedecode_42 = vaedecode.decode(
            samples=get_value_at_index(ksampler_3, 0),
            vae=get_value_at_index(vaeloader_12, 0),
        )

        saveimages3_89 = saveimages3.save_images(
            filename_prefix="waifu", images=get_value_at_index(vaedecode_42, 0)
        )

        return get_value_at_index(saveimages3_89, 0)
    

def generate_presigned_url(bucket_name: str, object_name: str, expiration: int = 3600):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=os.environ["AWS_ACCESS_KEY_ID"],
        aws_secret_access_key=os.environ["AWS_SECRET_ACCESS_KEY"],
        endpoint_url=os.environ["AWS_ENDPOINT_URL_S3"],
        region_name=os.environ.get("AWS_REGION", None),
    )

    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except Exception as e:
        print(f"Error generating presigned URL: {e}")
        return None

    return response


def hallucinate_prompt(hash_str):
    sb = []
    
    # First character determines gender
    if '0' < hash_str[0] <= '5':
        sb.append("1girl, ")
    else:
        sb.append("1guy, ")
    
    # Second character determines hair color
    if hash_str[1] in '0123':
        sb.append("blonde, ")
    elif hash_str[1] in '4567':
        sb.append("brown hair, ")
    elif hash_str[1] in '89ab':
        sb.append("red hair, ")
    elif hash_str[1] in 'cdef':
        sb.append("black hair, ")
    
    # Third character determines setting
    if '0' < hash_str[2] <= '5':
        sb.append("coffee shop, ")
    else:
        sb.append("landscape, outdoors, ")
    
    # Fourth character determines clothing
    if '0' < hash_str[3] <= '5':
        sb.append("hoodie, ")
    else:
        sb.append("sweatsuit, ")
    
    # Fifth character determines style
    if hash_str[4] in '0123':
        sb.append("<lora:cdi:1>, ")
    elif hash_str[4] in '4567':
        sb.append("breath of the wild, ")
    elif hash_str[4] in '89ab':
        sb.append("genshin impact, ")
    elif hash_str[4] in 'cdef':
        sb.append("arknights, ")
    
    # Sixth character determines art style
    if '0' < hash_str[5] <= '5':
        sb.append("watercolor, ")
    else:
        sb.append("matte painting, ")
    
    # Seventh character determines detail level
    if hash_str[6] in '0123':
        sb.append("highly detailed, ")
    elif hash_str[6] in '4567':
        sb.append("ornate, ")
    elif hash_str[6] in '89ab':
        sb.append("thick lines, ")
    elif hash_str[6] in 'cdef':
        sb.append("3d render, ")
    
    # Eighth character determines hairstyle
    if hash_str[7] in '0123':
        sb.append("short hair, ")
    elif hash_str[7] in '4567':
        sb.append("long hair, ")
    elif hash_str[7] in '89ab':
        sb.append("ponytail, ")
    elif hash_str[7] in 'cdef':
        sb.append("pigtails, ")
    
    # Ninth character determines expression
    if hash_str[8] in '0123':
        sb.append("smile, ")
    elif hash_str[8] in '4567':
        sb.append("frown, ")
    elif hash_str[8] in '89ab':
        sb.append("laughing, ")
    elif hash_str[8] in 'cdef':
        sb.append("angry, ")
    
    # Tenth character determines outerwear
    if hash_str[9] in '0123':
        sb.append("sweater, ")
    elif hash_str[9] in '4567':
        sb.append("tshirt, ")
    elif hash_str[9] in '89ab':
        sb.append("suitjacket, ")
    elif hash_str[9] in 'cdef':
        sb.append("armor, ")
    
    # Eleventh character determines eye color
    if hash_str[10] in '0123':
        sb.append("blue eyes, ")
    elif hash_str[10] in '4567':
        sb.append("red eyes, ")
    elif hash_str[10] in '89ab':
        sb.append("brown eyes, ")
    elif hash_str[10] in 'cdef':
        sb.append("hazel eyes, ")
    
    # Twelfth character determines heterochromia
    if hash_str[11] == '0':
        sb.append("heterochromia, ")
    
    # Thirteenth character determines time of day
    if hash_str[12] in '0123':
        sb.append("morning, ")
    elif hash_str[12] in '4567':
        sb.append("afternoon, ")
    elif hash_str[12] in '89ab':
        sb.append("evening, ")
    elif hash_str[12] in 'cdef':
        sb.append("nighttime, ")
    
    # Fourteenth character determines additional style
    if hash_str[13] == '0':
        sb.append("<lora:genshin:1>, genshin, ")
    
    # Fifteenth character determines artistic influence
    if hash_str[14] in '0123':
        sb.append("vtuber, ")
    elif hash_str[14] in '4567':
        sb.append("anime, ")
    elif hash_str[14] in '89ab':
        sb.append("studio ghibli, ")
    elif hash_str[14] in 'cdef':
        sb.append("cloverworks, ")
    
    # Extract seed portion and convert to integer
    seed_portion = hash_str[-9:-1]
    try:
        seed = int(seed_portion, 16)
    except ValueError:
        seed = random.randint(0, 2**32 - 1)
    
    # Final addition to the prompt
    sb.append("pants")
    
    # Return the concatenated string and seed
    return ''.join(sb), seed


@app.route("/", methods=["GET"])
def read_root():
    return jsonify({"Hello": "World"})


@app.route("/health-check", methods=["GET"])
def health_check():
    return jsonify({"status": "READY"})


@app.route("/avatar/<hash_str>", methods=["GET"])
def generate_from_hash(hash_str):
    prompt, seed = hallucinate_prompt(hash_str)
    image_response = generate_image(prompt, "person in distance, worst quality, low quality, medium quality, deleted, lowres, comic, bad anatomy, bad hands, text, error, missing fingers, extra digit, fewer digits, cropped, jpeg artifacts, signature, watermark, username, blurry")

    redirect_url = generate_presigned_url(
        os.getenv("BUCKET_NAME", "comfyui"), image_response[0]
    )

    return redirect(redirect_url, code=302)


@app.route("/generate", methods=["POST"])
def generate():
    content_type = request.headers.get('Content-Type')
    if (content_type == 'application/json'):
        json = request.json
    else:
        return 'Content-Type not supported!'
    
    image_response = generate_image(json["prompt"], json["negative_prompt"])

    return jsonify({
        "fname": image_response,
        "url": generate_presigned_url(
            os.getenv("BUCKET_NAME", "comfyui"), image_response[0]
        ),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)
