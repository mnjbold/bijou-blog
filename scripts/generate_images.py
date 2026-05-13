import cloudinary
import cloudinary.uploader
import requests
import urllib.parse
import time
import json
from pathlib import Path

cloudinary.config(
    cloud_name="dxyodhkwk",
    api_key="949438979649962",
    api_secret="MeZ2CUsOpF0lhOBM9RiUT2nBUfs",
    secure=True
)

def generate_and_upload(prompt, public_id, width=1200, height=630):
    """Generate image via Pollinations and upload to Cloudinary"""
    encoded = urllib.parse.quote(prompt)
    seed = abs(hash(prompt)) % 99999
    url = f"https://image.pollinations.ai/prompt/{encoded}?width={width}&height={height}&nologo=true&model=flux&seed={seed}"
    print(f"Generating: {public_id}")
    print(f"  URL: {url[:80]}...")
    # Download
    resp = requests.get(url, timeout=120)
    resp.raise_for_status()
    print(f"  Downloaded {len(resp.content)} bytes")
    # Upload to Cloudinary
    result = cloudinary.uploader.upload(
        resp.content,
        public_id=public_id,
        folder="bijou-blog",
        overwrite=True,
        resource_type="image"
    )
    cdn_url = result["secure_url"]
    print(f"  Uploaded: {cdn_url}")
    return cdn_url

# Define all images
IMAGES = {
    "why-ai-agents-will-replace-workflows": {
        "cover": ("futuristic AI neural network agents flowing through digital circuits, dark background, gold accent lights, cinematic, ultra detailed, 8k", 1200, 630),
        "inline-1": ("robot hands typing on keyboard with holographic workflow diagrams floating, dark moody tech aesthetic", 800, 450),
        "inline-2": ("human silhouette merging with digital AI agent, transformation visualization, dark gold color scheme", 800, 450),
    },
    "building-bold-connect-from-zero": {
        "cover": ("modern startup founders working late night in Kuala Lumpur office with city skyline, laptop screens glowing, cinematic", 1200, 630),
        "inline-1": ("recruitment platform UI on multiple screens showing candidate profiles, modern dark UI design", 800, 450),
        "inline-2": ("startup pitch deck presentation in sleek modern boardroom Malaysia aesthetic night scene", 800, 450),
    },
    "malaysia-startup-scene-2026": {
        "cover": ("Kuala Lumpur KLCC Twin Towers golden hour digital data visualization overlaid futuristic cityscape", 1200, 630),
        "inline-1": ("diverse young Malaysian tech founders collaborating co-working space modern vibrant atmosphere", 800, 450),
        "inline-2": ("Southeast Asia tech startup ecosystem map visualization glowing nodes connections", 800, 450),
    }
}

results = {}
for slug, images in IMAGES.items():
    results[slug] = {}
    for img_type, (prompt, w, h) in images.items():
        public_id = f"posts/{slug}/{img_type}"
        try:
            url = generate_and_upload(prompt, public_id, w, h)
            results[slug][img_type] = url
            time.sleep(2)  # be nice to the API
        except Exception as e:
            print(f"ERROR {public_id}: {e}")
            results[slug][img_type] = None

print("\n=== FINAL URLS ===")
print(json.dumps(results, indent=2))

# Save results to file for use by update script
output_path = Path("/tmp/bijou-blog/scripts/image_urls.json")
with open(output_path, "w") as f:
    json.dump(results, f, indent=2)
print(f"\nURLs saved to {output_path}")
