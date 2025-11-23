from pathlib import Path
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
from qrcode.image.styles.colormasks import RadialGradiantColorMask
from PIL import Image, ImageDraw, ImageFont
import os

# --- CONFIGURATION ---
profile_link = "https://github.com/Deepashprojects"
text_to_show = "Scan to visit my GitHub Profile"
filename = "professional_qr.png"
temp_filename = "temp_qr.png"
logo_path = None  # Set to "logo.png" if you want to embed a small logo (recommended size ~40-80 px)

# 1. Create the base QR Code
qr = qrcode.QRCode(
    version=None,  # automatic size
    error_correction=qrcode.constants.ERROR_CORRECT_H,
    box_size=10,
    border=4,
)
qr.add_data(profile_link)
qr.make(fit=True)

# 2. Generate the Styled Image and SAVE it immediately
qr_object = qr.make_image(
    image_factory=StyledPilImage,
    module_drawer=RoundedModuleDrawer(),
    color_mask=RadialGradiantColorMask(
        back_color=(255, 255, 255),
        center_color=(0, 128, 255),
        edge_color=(0, 0, 128),
    ),
)

# Save to temporary file and ensure cleanup on error
temp_path = Path(temp_filename)
try:
    qr_object.save(temp_path)

    # 3. Open the temporary file as a Standard Image
    with Image.open(temp_path) as qr_img:
        qr_img = qr_img.convert("RGB")
        width, height = qr_img.size

        # Optional: embed a small logo in the center
        if logo_path:
            try:
                with Image.open(logo_path) as logo:
                    logo = logo.convert("RGBA")
                    # scale logo to be at most 20% of QR width
                    max_logo_w = int(width * 0.20)
                    logo_ratio = logo.width / logo.height
                    logo_size = (max_logo_w, int(max_logo_w / logo_ratio))
                    logo = logo.resize(logo_size, Image.LANCZOS)

                    # compute position and paste with mask
                    lx = (width - logo.width) // 2
                    ly = (height - logo.height) // 2
                    qr_img.paste(logo, (lx, ly), logo)
            except Exception:
                pass

        # 4. Setup the Canvas (Make room for text)
        text_area = 60
        final_img = Image.new("RGB", (width, height + text_area), "white")
        final_img.paste(qr_img, (0, 0))

        # 5. Add the Text
        draw = ImageDraw.Draw(final_img)
        # try a few common fonts then fallback
        font = None
        for candidate in [
            "arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/Library/Fonts/Arial.ttf",
        ]:
            try:
                font = ImageFont.truetype(candidate, 20)
                break
            except Exception:
                font = None
        if font is None:
            font = ImageFont.load_default()

        text_bbox = draw.textbbox((0, 0), text_to_show, font=font)
        text_width = text_bbox[2] - text_bbox[0]
        x_position = int((width - text_width) / 2)
        y_position = height + int((text_area - (text_bbox[3] - text_bbox[1])) / 2)

        draw.text((x_position, y_position), text_to_show, fill=(0, 0, 128), font=font)

        # 6. Save Final
        final_img.save(filename)
        print(f"✅ Success! Created Professional QR: {filename}")
finally:
    # Remove the temp file to keep folder clean
    try:
        if temp_path.exists():
            temp_path.unlink()
    except Exception:
        pass