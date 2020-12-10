import cv2
import numpy as np

from settings import THICKNESS, SOLIDITY, RGB_SCALE, CMYK_SCALE


def create_mask_frame(frame, round_chamfer, spacing, radius):
    height, width = frame.shape[:2]

    mask_image = np.zeros((height, width), np.uint8)
    boundary_image = mask_image.copy()

    # Draw four rounded corners
    if round_chamfer == "round":
        boundary_image = cv2.ellipse(boundary_image, (radius + spacing, radius + spacing), (radius, radius), 180, 0,
                                     90, 255, THICKNESS)
        boundary_image = cv2.ellipse(boundary_image, (int(width - radius - spacing), radius + spacing),
                                     (radius, radius), 270, 0, 90, 255, THICKNESS)
        boundary_image = cv2.ellipse(boundary_image, (radius + spacing, int(height - radius - spacing)),
                                     (radius, radius), 90, 0, 90, 255, THICKNESS)
        boundary_image = cv2.ellipse(boundary_image, (int(width - radius - spacing), int(height - radius - spacing)),
                                     (radius, radius), 0, 0, 90, 255, THICKNESS)
    else:
        boundary_image = cv2.line(boundary_image, (radius + spacing, spacing), (spacing, radius + spacing), 255,
                                  THICKNESS)
        boundary_image = cv2.line(boundary_image, (width - radius - spacing, spacing),
                                  (width - spacing, radius + spacing), 255, THICKNESS)
        boundary_image = cv2.line(boundary_image, (spacing, height - radius - spacing),
                                  (radius + spacing, height - spacing), 255, THICKNESS)
        boundary_image = cv2.line(boundary_image, (width - spacing, height - radius - spacing),
                                  (width - radius - spacing, height - spacing), 255, THICKNESS)

    # Draw four edges
    boundary_image = cv2.line(boundary_image, (radius + spacing, spacing), (int(width - radius - spacing), spacing),
                              255, THICKNESS)
    boundary_image = cv2.line(boundary_image, (spacing, radius + spacing), (spacing, int(height - radius - spacing)),
                              255, THICKNESS)
    boundary_image = cv2.line(boundary_image, (radius + spacing, height - spacing),
                              (int(width - radius - spacing), height - spacing), 255, THICKNESS)
    boundary_image = cv2.line(boundary_image, (width - spacing, radius + spacing),
                              (width - spacing, int(height - radius - spacing)), 255, THICKNESS)
    # cv2.imshow("boundary image", boundary_image)
    # cv2.waitKey()
    contour, _ = cv2.findContours(boundary_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    boundary = sorted(contour, key=cv2.contourArea, reverse=True)[0]

    return mask_image, boundary


def get_round_chamfer_image(frame, radius, round_chamfer="round"):

    mask_image, boundary = create_mask_frame(frame=frame, radius=radius, round_chamfer=round_chamfer, spacing=0)
    mask = cv2.drawContours(mask_image, [boundary], -1, 255, -1)

    binary_mask = mask.copy()
    binary_mask[mask == 0] = 0
    binary_mask[mask == 255] = 1

    bgr_blur_mask = cv2.cvtColor(mask, cv2.COLOR_GRAY2BGR).astype(np.float)
    blur_edge_frame = (bgr_blur_mask / 255.0 * frame).astype(np.uint8)

    b, g, r = cv2.split(blur_edge_frame)
    round_chamfer_image = cv2.merge([b, g, r, mask])

    # Generate masks for proper blending

    # cv2.imshow("round image", transparent_png)
    # cv2.waitKey()

    return round_chamfer_image


def add_spot_channel(frame, ch_num, zoom_value, zoom_ret, round_chamfer, radius, round_chamfer_image):
    if zoom_ret == "in":
        zoom_value = 0

    mask_frame, boundary = create_mask_frame(frame=frame, spacing=zoom_value, round_chamfer=round_chamfer,
                                             radius=radius)
    mask = cv2.drawContours(mask_frame, [boundary], -1, 255, -1)

    binary_mask = mask.copy()
    binary_mask[mask == 0] = 0
    binary_mask[mask == 255] = 1

    mask_bgr_frame = cv2.cvtColor(mask_frame, cv2.COLOR_GRAY2BGR)
    red_frame = cv2.drawContours(mask_bgr_frame, [boundary], -1, (0, 0, 255), -1)
    r_c_b, r_c_g, r_c_r, _ = cv2.split(round_chamfer_image)

    # cv2.imshow("red frame", red_frame)
    # cv2.waitKey()
    spoted_frame = cv2.addWeighted(cv2.merge([r_c_b, r_c_g, r_c_r]), 1 - SOLIDITY, red_frame, SOLIDITY, 0)

    if ch_num == 2:
        green_frame = cv2.drawContours(mask_bgr_frame, [boundary], -1, (0, 255, 0), -1)
        spoted_frame = cv2.addWeighted(spoted_frame, 1 - SOLIDITY, green_frame, SOLIDITY, 0)

    spot_b, spot_g, spot_r = cv2.split(spoted_frame)
    spot_png_frame = cv2.merge([spot_b, spot_g, spot_r, binary_mask])
    # cv2.imshow("spot frame", spot_png_frame)
    # cv2.waitKey()

    return spot_png_frame


def convert_rbg_cmyk(frame):
    b, g, r, _ = cv2.split(frame)
    bgr_frame = cv2.merge([b, g, r])
    bgr_dash = bgr_frame.astype(np.float) / 255.

    # Calculate K as (1 - whatever is biggest out of Rdash, Gdash, Bdash)
    k = 1 - np.max(bgr_dash, axis=2)

    # Calculate C
    c = (1 - bgr_dash[..., 2] - k) / (1 - k)

    # Calculate M
    m = (1 - bgr_dash[..., 1] - k) / (1 - k)

    # Calculate Y
    y = (1 - bgr_dash[..., 0] - k) / (1 - k)

    # Combine 4 channels into single image and re-scale back up to uint8
    cmyk = (np.dstack((c, m, y, k)) * 255).astype(np.uint8)
    # cv2.imwrite("t.tiff", cmyk)
    #
    # cv2.imshow("cmyk frame", cmyk)
    # cv2.waitKey()

    return cmyk


if __name__ == '__main__':
    f_frame = cv2.imread("/media/main/Data/Task/ImageProcessingApp/example-1.png")
    r_frame = cv2.resize(f_frame, None, fx=0.5, fy=0.5)
    r_c_image = get_round_chamfer_image(frame=r_frame,
                                        radius=30, round_chamfer="chamfer")
    spot_img = add_spot_channel(frame=r_frame, radius=30, round_chamfer="chamfer", ch_num=2, zoom_value=20,
                                zoom_ret="out", round_chamfer_image=r_c_image)
    convert_rbg_cmyk(spot_img)
