# Random Profile Images

This folder contains images that will be randomly selected and displayed as your profile picture on the about page.

## How to add more images:

1. Add your image files to this folder (e.g., `yue_3.png`, `yue_4.png`, etc.)
2. Update the `images` array in `_includes/random_profile_image.liquid`
3. Add the new image filenames to both the server-side and client-side arrays

## Current images:
- `yue_1.png`
- `yue_2.png`

## How it works:
- The random selection happens both server-side (using Jekyll) and client-side (using JavaScript)
- Each time someone visits your about page, a random image will be selected
- The image will change on page refresh
- The system uses a fallback approach to ensure it works reliably

## Supported formats:
- PNG
- JPG/JPEG
- GIF
- WebP

## Notes:
- Make sure all images have similar dimensions for consistent display
- The random selection is based on the current timestamp for server-side selection
- Client-side JavaScript provides additional randomization 