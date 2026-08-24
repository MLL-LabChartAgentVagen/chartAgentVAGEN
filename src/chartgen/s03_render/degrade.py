"""Making the image worse, and moving every recorded box with it.

Only degradations whose geometry has a closed form are allowed. A box is mapped
through the same matrix the pixels went through, so the annotation stays exact
however bad the image gets. A degradation with no analytic transform -- a warp, a
fold, a hand-drawn overlay -- does not go in the pipeline at all.

    jpeg, noise, blur    the geometry is unchanged
    downscale            a scale
    rotate               an affine map
    perspective          a homography

After a rotation or a perspective change the bounding box of a shape is slightly
larger than the shape, because a box is axis-aligned and the shape is no longer.
That is a known and bounded error, and the record says which transform produced it.
"""

from __future__ import annotations

from dataclasses import replace
from pathlib import Path
from typing import Callable, Sequence

import numpy as np

from ..common.geometry import Box, Matrix, apply, homography, identity, rotate, scale
from ..common.rng import derive
from ..interfaces.record import RenderOutput
from ..interfaces.style import Degradation

STAGE = "s03_degrade"

#: Degradations that leave every pixel where it was.
GEOMETRIC_IDENTITY = frozenset({"none", "jpeg", "noise", "blur"})

#: How far the amount is allowed to move things: degrees of rotation, and the
#: fraction of the width a corner may travel under a perspective change.
MAX_ROTATION = 3.0
MAX_PERSPECTIVE = 0.06

#: Range the downscale factor is taken from.
DOWNSCALE = (0.5, 0.9)


def matrix_for(kind: str, amount: float, size: tuple[int, int]) -> Matrix:
    """The transform this degradation applies to the image, and therefore to the boxes."""
    w, h = size
    if kind in GEOMETRIC_IDENTITY:
        return identity()
    if kind == "downscale":
        factor = DOWNSCALE[0] + amount * (DOWNSCALE[1] - DOWNSCALE[0])
        return scale(factor, factor)
    if kind == "rotate":
        return rotate(MAX_ROTATION * (2 * amount - 1), w / 2, h / 2)
    if kind == "perspective":
        d = MAX_PERSPECTIVE * amount * w
        src = [(0, 0), (w, 0), (w, h), (0, h)]
        dst = [(d, d / 2), (w - d, 0), (w, h - d / 2), (0 + d / 2, h)]
        return homography(src, dst)
    raise ValueError(f"no geometry defined for degradation {kind!r}")


def degrade_image(img: np.ndarray, kind: str, amount: float, matrix: Matrix,
                  rng: np.random.Generator) -> np.ndarray:
    """Apply the degradation to the pixels. The matrix is the one the boxes get."""
    import cv2

    h, w = img.shape[:2]
    if kind == "noise":
        noise = rng.normal(0.0, 4.0 + 16.0 * amount, img.shape)
        return np.clip(img.astype(np.float32) + noise, 0, 255).astype(np.uint8)
    if kind == "blur":
        radius = int(1 + 4 * amount) * 2 + 1
        return cv2.GaussianBlur(img, (radius, radius), 0)
    if kind == "downscale":
        factor = float(matrix[0, 0])
        small = cv2.resize(img, (max(1, int(w * factor)), max(1, int(h * factor))),
                           interpolation=cv2.INTER_AREA)
        return small
    if kind in ("rotate", "perspective"):
        return cv2.warpPerspective(img, matrix.astype(np.float64), (w, h),
                                   borderValue=(255, 255, 255))
    return img


def _write(img: np.ndarray, path: Path, kind: str, amount: float) -> Path:
    """Write the degraded image beside the original rather than over it.

    The undegraded rendering is what the geometry was recorded against, and
    overwriting it would make degrading twice compound silently.
    """
    from PIL import Image

    picture = Image.fromarray(img)
    if kind == "jpeg":
        out = path.with_name(f"{path.stem}_jpeg.jpg")
        picture.save(out, quality=int(40 + 55 * (1 - amount)), subsampling=1)
        return out
    out = path.with_name(f"{path.stem}_{kind}{path.suffix}")
    picture.save(out)
    return out


def apply_to(rendered: RenderOutput, degradation: Degradation, *,
             seed: int = 0) -> RenderOutput:
    """Degrade one image and map every box in its record through the same transform."""
    return apply_to_all([rendered], degradation, seed=seed)[0]


def apply_to_all(rendered: Sequence[RenderOutput], degradation: Degradation, *,
                 seed: int = 0) -> list[RenderOutput]:
    """Degrade one image once, for every record that points at it.

    Records that share a page share an image. Degrading each of them in turn would
    degrade the page as many times as there are figures on it, and every record but
    the first would map its boxes through a transform that had already been applied.
    """
    if not rendered or degradation.kind == "none":
        return list(rendered)

    from ..common.readback import load_image

    first = rendered[0]
    path = Path(first.image_path)
    matrix = matrix_for(degradation.kind, degradation.amount, first.image_size)
    rng = derive(seed, STAGE, first.figure_id, degradation.kind)
    img = degrade_image(load_image(path), degradation.kind, degradation.amount, matrix, rng)
    out_path = _write(img, path, degradation.kind, degradation.amount)
    size = (int(img.shape[1]), int(img.shape[0]))
    move: Callable[[Box], Box] = lambda box: apply(matrix, box)
    return [_moved(r, move, matrix, out_path, size, degradation) for r in rendered]


def _moved(rendered: RenderOutput, move, matrix: Matrix, out_path: Path,
           size: tuple[int, int], degradation: Degradation) -> RenderOutput:
    """One record after the transform, saying what was actually done to its image.

    Records that share a page share one degradation -- the page is degraded once, not
    once per figure on it -- so the ones that did not choose it have their style
    corrected to the one that ran. A record whose style names a degradation its image
    never had would be describing a different image.
    """
    return replace(
        rendered,
        style=replace(rendered.style, degradation=degradation),
        image_path=str(out_path),
        image_size=size,
        panels=tuple(replace(p, box=move(p.box), axes=tuple(
            replace(a, pixel_range=_move_range(matrix, a)) for a in p.axes))
            for p in rendered.panels),
        marks=tuple(replace(m, box=move(m.box),
                            label_box=move(m.label_box) if m.label_box else None)
                    for m in rendered.marks),
        legend=tuple(replace(e, box=move(e.box)) for e in rendered.legend),
        elements=tuple(replace(e, box=move(e.box)) for e in rendered.elements),
        degradations=rendered.degradations + (degradation,),
    )


def _move_range(matrix: Matrix, axis) -> tuple[float, float]:
    """An axis's pixel range under the transform.

    Taken along the axis's own direction: a horizontal axis moves with x, a vertical
    one with y. Under a rotation the two are no longer independent, which is why a
    rotated figure keeps its boxes exactly and its axis ranges only approximately --
    and why the record says a rotation was applied.
    """
    from ..common.geometry import apply_point

    horizontal = axis.role == "x"
    a = apply_point(matrix, axis.pixel_range[0], 0.0) if horizontal else \
        apply_point(matrix, 0.0, axis.pixel_range[0])
    b = apply_point(matrix, axis.pixel_range[1], 0.0) if horizontal else \
        apply_point(matrix, 0.0, axis.pixel_range[1])
    i = 0 if horizontal else 1
    return (float(a[i]), float(b[i]))
