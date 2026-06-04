#!/usr/bin/env python3
"""
HelloPhobos installer
=====================
Run from your KSA linux-x64/ directory:
    python3 Content/HelloPhobos/install.py

What this does:
  1. Patches Core/Astronomicals.xml to add HELLO WORLD + blob decals to Phobos
  2. Copies Core's Luna meshes/textures into HelloPhobos/ (avoids redistribution)
  3. Registers HelloPhobos in Content/manifest.toml

To uninstall:
    python3 Content/HelloPhobos/install.py --uninstall
"""

import sys, shutil, json, re
from pathlib import Path

KSA_ROOT = Path(__file__).parent.parent.parent   # linux-x64/
CORE     = KSA_ROOT / "Content/Core"
MOD      = KSA_ROOT / "Content/HelloPhobos"
MANIFEST = KSA_ROOT / "Content/manifest.toml"
ASTRO    = CORE / "Astronomicals.xml"
ASTRO_BAK= CORE / "Astronomicals.xml.hellophobos.bak"

DECALS = '''
                <!-- ── HelloPhobos mod: orbit-visible terrain features ── -->
                <Modifier Type="Decal" Name="PhobosBlobCreature" Biomes="Surface">
                    <Amplitude Value="400" />
                    <Order Value="9999" />
                    <Radius Value="3000" />
                    <Rotation Degrees="0" />
                    <Location Id="HP_BlobLocation">
                        <Latitude Degrees="0.0" />
                        <Longitude Degrees="0.0" />
                    </Location>
                    <AltitudeOffset Km="0" />
                    <SmoothFactor Value="0.3" />
                    <Additive Value="true" />
                    <HeightMap Id="HP_BlobHeightMap"
                        Path="Textures/Planets/Phobos/PhobosBlob.png"
                        Category="Terrain"/>
                </Modifier>

                <Modifier Type="Decal" Name="PhobosHelloWorld" Biomes="Surface">
                    <Amplitude Value="350" />
                    <Order Value="9998" />
                    <Radius Value="2000" />
                    <Rotation Degrees="0" />
                    <Location Id="HP_HelloWorldLocation">
                        <Latitude Degrees="0.0" />
                        <Longitude Degrees="180.0" />
                    </Location>
                    <AltitudeOffset Km="0" />
                    <SmoothFactor Value="0.2" />
                    <Additive Value="true" />
                    <HeightMap Id="HP_HelloWorldHeightMap"
                        Path="Textures/Planets/Phobos/PhobosHelloWorld.png"
                        Category="Terrain"/>
                </Modifier>
                <!-- ── end HelloPhobos ── -->
'''

MARKER_START = "<!-- ── HelloPhobos mod: orbit-visible terrain features ── -->"
MARKER_END   = "<!-- ── end HelloPhobos ── -->"


def patch_astronomicals():
    text = ASTRO.read_text(encoding="utf-8")
    if MARKER_START in text:
        print("  Core/Astronomicals.xml already patched — skipping.")
        return

    # Back up original
    shutil.copy2(ASTRO, ASTRO_BAK)
    print(f"  Backed up to {ASTRO_BAK.name}")

    # Find closing </ProceduralModifiers> inside Phobos block
    # Search from the PhobosImpacts modifier onwards
    phobos_start = text.find('<MinorBody Id="Phobos"')
    if phobos_start == -1:
        sys.exit("ERROR: Could not find Phobos MinorBody in Core/Astronomicals.xml")

    # Find first </ProceduralModifiers> after Phobos block start
    close_tag = "</ProceduralModifiers>"
    insert_pos = text.find(close_tag, phobos_start)
    if insert_pos == -1:
        sys.exit("ERROR: Could not find </ProceduralModifiers> in Phobos block")

    patched = text[:insert_pos] + DECALS + text[insert_pos:]
    ASTRO.write_text(patched, encoding="utf-8")
    print("  Core/Astronomicals.xml patched with Phobos decals.")


def unpatch_astronomicals():
    if not ASTRO_BAK.exists():
        print("  No backup found — Core/Astronomicals.xml not modified by this installer.")
        return
    shutil.copy2(ASTRO_BAK, ASTRO)
    ASTRO_BAK.unlink()
    print("  Core/Astronomicals.xml restored from backup.")


def copy_core_assets():
    """Copy Luna rock assets from Core into our mod folder.
    These are needed at runtime but can't be redistributed in the package.
    """
    copies = [
        # (source relative to CORE, dest relative to MOD)
        ("Textures/Planets/Luna/GroundClutter/TestRocks_Diffuse.ktx2",
         "Textures/Planets/Luna/GroundClutter/TestRocks_Diffuse.ktx2"),
        ("Textures/Planets/Luna/GroundClutter/TestRocks_Normal.dds",
         "Textures/Planets/Luna/GroundClutter/TestRocks_Normal.dds"),
        ("Textures/Planets/Luna/GroundClutter/TestRocks_AoRoughMetal.dds",
         "Textures/Planets/Luna/GroundClutter/TestRocks_AoRoughMetal.dds"),
        ("Meshes/Planets/Luna/GroundClutter/Rock0Lod0.glb",
         "Meshes/Planets/Luna/GroundClutter/Rock0Lod0.glb"),
        ("Meshes/Planets/Luna/GroundClutter/Rock0Lod1.glb",
         "Meshes/Planets/Luna/GroundClutter/Rock0Lod1.glb"),
        ("Meshes/Planets/Luna/GroundClutter/Rock0Lod2.glb",
         "Meshes/Planets/Luna/GroundClutter/Rock0Lod2.glb"),
        ("Meshes/Planets/Luna/GroundClutter/Rock0Lod3.glb",
         "Meshes/Planets/Luna/GroundClutter/Rock0Lod3.glb"),
        ("Meshes/Planets/Luna/GroundClutter/Rock0Lod4.glb",
         "Meshes/Planets/Luna/GroundClutter/Rock0Lod4.glb"),
    ]
    for src_rel, dst_rel in copies:
        src = CORE / src_rel
        dst = MOD  / dst_rel
        if not src.exists():
            print(f"  WARN: Core asset not found: {src_rel} — skipping")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
    print(f"  Copied {len(copies)} Core assets into HelloPhobos/")


def remove_core_assets():
    for d in ["Meshes/Planets/Luna", "Textures/Planets/Luna"]:
        p = MOD / d
        if p.exists():
            shutil.rmtree(p)
    print("  Removed copied Core assets from HelloPhobos/")


def copy_decal_textures():
    """Copy decal PNGs into Core texture path (generated on dwalin)."""
    phobos_tex = CORE / "Textures/Planets/Phobos"
    phobos_tex.mkdir(parents=True, exist_ok=True)
    for name in ["PhobosBlob.png", "PhobosHelloWorld.png"]:
        src = MOD / "Textures/Planets/Phobos" / name
        dst = phobos_tex / name
        if src.exists():
            shutil.copy2(src, dst)
            print(f"  Copied {name} → Core/Textures/Planets/Phobos/")
        elif dst.exists():
            print(f"  {name} already in Core/Textures/Planets/Phobos/")
        else:
            print(f"  WARN: {name} not found in mod or Core — run generate_textures.py")


def remove_decal_textures():
    for name in ["PhobosBlob.png", "PhobosHelloWorld.png"]:
        p = CORE / "Textures/Planets/Phobos" / name
        if p.exists():
            p.unlink()
            print(f"  Removed Core/Textures/Planets/Phobos/{name}")


def patch_manifest():
    text = MANIFEST.read_text()
    if 'id = "HelloPhobos"' in text:
        print("  manifest.toml already contains HelloPhobos — skipping.")
        return
    with open(MANIFEST, "a") as f:
        f.write('\n[[mods]]\nid = "HelloPhobos"\nenabled = true\n')
    print("  manifest.toml updated.")


def unpatch_manifest():
    text = MANIFEST.read_text()
    # Remove the HelloPhobos block
    cleaned = re.sub(
        r'\n\[\[mods\]\]\nid = "HelloPhobos"\nenabled = (true|false)\n',
        '', text)
    MANIFEST.write_text(cleaned)
    print("  HelloPhobos removed from manifest.toml.")


def generate_textures():
    """Generate the decal PNGs if not already present."""
    blob = MOD / "Textures/Planets/Phobos/PhobosBlob.png"
    hw   = MOD / "Textures/Planets/Phobos/PhobosHelloWorld.png"
    if blob.exists() and hw.exists():
        return
    print("  Generating decal textures...")
    (MOD / "Textures/Planets/Phobos").mkdir(parents=True, exist_ok=True)
    try:
        from PIL import Image, ImageDraw, ImageFont, ImageFilter
        import math, random

        # Blob
        size = 512
        img = Image.new("RGBA", (size, size), (0,0,0,0))
        draw = ImageDraw.Draw(img)
        cx, cy = size//2, size//2
        base_r = size * 0.38
        rng = random.Random(42)
        harmonics = [(1,0.12),(2,0.09),(3,0.07),(4,0.05),(5,0.04),(7,0.03)]
        phases = [rng.uniform(0, 2*math.pi) for _ in harmonics]
        def blob_r(theta):
            r = base_r
            for (freq,amp),phase in zip(harmonics,phases):
                r += base_r * amp * math.sin(freq*theta+phase)
            return r
        N = 256
        pts = [(cx+blob_r(2*math.pi*i/N)*math.cos(2*math.pi*i/N),
                cy+blob_r(2*math.pi*i/N)*math.sin(2*math.pi*i/N)) for i in range(N)]
        draw.polygon(pts, fill=(255,255,255,255))
        img = img.filter(ImageFilter.GaussianBlur(radius=8))
        img.save(str(blob))

        # Hello World (mirrored)
        img2 = Image.new("RGBA", (size, size), (0,0,0,0))
        draw2 = ImageDraw.Draw(img2)
        font = None
        for fp in ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                   "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
            try: font = ImageFont.truetype(fp, 72); break
            except: pass
        if not font: font = ImageFont.load_default()
        for i, word in enumerate(["HELLO","WORLD"]):
            bb = draw2.textbbox((0,0), word, font=font)
            tw,th = bb[2]-bb[0], bb[3]-bb[1]
            x,y = (size-tw)//2, 80+i*(th+30)
            for dx in range(-4,5):
                for dy in range(-4,5):
                    draw2.text((x+dx,y+dy), word, fill=(180,180,180,255), font=font)
            draw2.text((x,y), word, fill=(255,255,255,255), font=font)
        img2 = img2.filter(ImageFilter.GaussianBlur(radius=3))
        img2 = img2.transpose(Image.FLIP_LEFT_RIGHT)
        img2.save(str(hw))
        print("  Decal textures generated.")
    except ImportError:
        print("  WARN: Pillow not installed. Install with:")
        print("        pip install pillow --break-system-packages")
        print("  Then re-run this installer.")


def install():
    print("\nHelloPhobos Installer")
    print("=" * 40)
    generate_textures()
    copy_decal_textures()
    patch_astronomicals()
    copy_core_assets()
    patch_manifest()
    print("\n✓ Installation complete!")
    print("  Launch KSA and navigate to Phobos.")
    print("  HELLO WORLD is at lat=0 lon=180")
    print("  The blob is at lat=0 lon=0 (Mars-facing)")


def uninstall():
    print("\nHelloPhobos Uninstaller")
    print("=" * 40)
    unpatch_astronomicals()
    remove_core_assets()
    remove_decal_textures()
    unpatch_manifest()
    print("\n✓ Uninstallation complete. KSA restored to vanilla state.")


if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        uninstall()
    else:
        install()
