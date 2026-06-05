#!/usr/bin/env python3
"""
HelloPhobos Installer — KSA v2026.6.x (Linux native build)
===========================================================
Run from your KSA linux-x64/ directory:
    python3 Content/HelloPhobos/install.py

To uninstall:
    python3 Content/HelloPhobos/install.py --uninstall
"""

import sys, shutil, re, struct, subprocess
from pathlib import Path

KSA_ROOT  = Path(__file__).parent.parent.parent
CORE      = KSA_ROOT / "Content/Core"
MOD       = KSA_ROOT / "Content/HelloPhobos"
MANIFEST  = KSA_ROOT / "Content/manifest.toml"
ASTRO     = CORE / "Astronomicals.xml"
ASTRO_BAK = CORE / "Astronomicals.xml.hellophobos.bak"

# ── Markers so we can cleanly uninstall ───────────────────────────────────────
MARKER_LUNA_START  = '<!-- ── HelloPhobos: Luna features ── -->'
MARKER_LUNA_END    = '<!-- ── end HelloPhobos Luna features ── -->'
MARKER_PHOBOS_START= '<!-- ── HelloPhobos: Phobos decals ── -->'
MARKER_PHOBOS_END  = '<!-- ── end HelloPhobos Phobos decals ── -->'
MARKER_CLUTTER_START='<!-- ── HelloPhobos: Phobos GroundClutter ── -->'
MARKER_CLUTTER_END  ='<!-- ── end HelloPhobos GroundClutter ── -->'
MARKER_MARS_START   ='<!-- ── HelloPhobos: Mars landing targets ── -->'
MARKER_MARS_END     ='<!-- ── end HelloPhobos Mars features ── -->'

LUNA_DECALS = f"""
                {MARKER_LUNA_START}
                <Modifier Type="Decal" Name="LunaHelloMoon" Biomes="Surface,Craters,Maria">
                    <Amplitude Value="1500" />
                    <Order Value="9997" />
                    <Radius Value="300000" />
                    <Rotation Degrees="0" />
                    <Location Id="HP_LunaHelloMoonLocation">
                        <Latitude Degrees="0.674" />
                        <Longitude Degrees="16.0" />
                    </Location>
                    <AltitudeOffset Km="0" />
                    <SmoothFactor Value="0.1" />
                    <Additive Value="true" />
                    <HeightMap Id="HP_LunaHelloMoonHeightMap"
                        Path="Textures/Planets/Luna/LunaHelloMoon.png"
                        Category="Terrain"/>
                </Modifier>
                <Modifier Type="Decal" Name="LunaLandingRings" Biomes="Surface,Craters,Maria">
                    <Amplitude Value="1200" />
                    <Order Value="9996" />
                    <Radius Value="300000" />
                    <Rotation Degrees="0" />
                    <Location Id="HP_LunaRingsLocation">
                        <Latitude Degrees="0.674" />
                        <Longitude Degrees="11.0" />
                    </Location>
                    <AltitudeOffset Km="0" />
                    <SmoothFactor Value="0.05" />
                    <Additive Value="true" />
                    <HeightMap Id="HP_LunaRingsHeightMap"
                        Path="Textures/Planets/Luna/LunaLandingRings.png"
                        Category="Terrain"/>
                </Modifier>
                {MARKER_LUNA_END}
"""

PHOBOS_DECALS = f"""
                {MARKER_PHOBOS_START}
                <Modifier Type="Decal" Name="PhobosBlobCreature" Biomes="Surface">
                    <Amplitude Value="1500" />
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
                    <Amplitude Value="1200" />
                    <Order Value="9998" />
                    <Radius Value="2000" />
                    <Rotation Degrees="0" />
                    <Location Id="HP_HelloWorldLocation">
                        <Latitude Degrees="0.0" />
                        <Longitude Degrees="0.0" />
                    </Location>
                    <AltitudeOffset Km="0" />
                    <SmoothFactor Value="0.2" />
                    <Additive Value="true" />
                    <HeightMap Id="HP_HelloWorldHeightMap"
                        Path="Textures/Planets/Phobos/PhobosHelloWorld.png"
                        Category="Terrain"/>
                </Modifier>
                {MARKER_PHOBOS_END}
"""

PHOBOS_CLUTTER = f"""        {MARKER_CLUTTER_START}
        <GroundClutter>
            <Ecotype Name="AlienCatTiny">
                <Placement Biomes="Surface">
                    <ObjectSeparation M="3.0" />
                    <GenerationRange M="170" />
                    <MinScale X="1.0" Y="1.0" Z="1.0" />
                    <MaxScale X="2.0" Y="2.0" Z="2.0" />
                    <Orientation Mode="SurfaceNormalSmooth" />
                    <MinRotation Degrees="0" />
                    <MaxRotation Degrees="360" />
                    <DistributionTexture Id="HP_AlienCatTiny_Dist"
                        Path="Textures/Planets/Phobos/GroundClutter/AlienCatTiny_Distribution.png" />
                    <DistributionTextureTiling Value="1" />
                    <UseObjectTypeTexture Value="false" />
                </Placement>
                <ClutterObject Name="AlienCatTinyMesh">
                    <LODs>
                        <LOD MinScreenSize="128">
                            <Mesh Id="HP_AlienCatT_Lod0" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod0.glb" />
                        </LOD>
                        <LOD MinScreenSize="64">
                            <Mesh Id="HP_AlienCatT_Lod1" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod1.glb" />
                        </LOD>
                        <LOD MinScreenSize="32">
                            <Mesh Id="HP_AlienCatT_Lod2" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod2.glb" />
                        </LOD>
                        <LOD MinScreenSize="16">
                            <Mesh Id="HP_AlienCatT_Lod3" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod3.glb" />
                        </LOD>
                        <LOD MinScreenSize="8">
                            <Mesh Id="HP_AlienCatT_Lod4" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod4.glb" />
                        </LOD>
                    </LODs>
                </ClutterObject>
                <Material>
                    <Diffuse Id="HP_AlienCatTDiff"
                        Path="Textures/Planets/Luna/GroundClutter/TestRocks_Diffuse.ktx2"
                        Category="Terrain"/>
                    <Normal Id="HP_AlienCatTNorm"
                        Path="Textures/Planets/Luna/GroundClutter/TestRocks_Normal.dds"
                        Category="Terrain"/>
                    <AoRoughMetal Id="HP_AlienCatTORM"
                        Path="Textures/Planets/Luna/GroundClutter/TestRocks_AoRoughMetal.dds"
                        Category="Terrain"/>
                    <UseTerrainMask Value="false" />
                    <DoubleSided Value="false" />
                    <CastShadows Value="true" />
                    <ReceiveShadows Value="true" />
                    <BiasNormalsUp Value="false" />
                    <ApplyExtraSpec Value="false" />
                    <DistanceFadeDither Value="true" />
                </Material>
            </Ecotype>
            <Ecotype Name="AlienCatGiant">
                <Placement Biomes="Surface">
                    <ObjectSeparation M="30.0" />
                    <GenerationRange M="170" />
                    <MinScale X="8.0" Y="8.0" Z="8.0" />
                    <MaxScale X="15.0" Y="15.0" Z="15.0" />
                    <Orientation Mode="SurfaceNormalSmooth" />
                    <MinRotation Degrees="0" />
                    <MaxRotation Degrees="360" />
                    <DistributionTexture Id="HP_AlienCatGiant_Dist"
                        Path="Textures/Planets/Phobos/GroundClutter/AlienCatGiant_Distribution.png" />
                    <DistributionTextureTiling Value="1" />
                    <UseObjectTypeTexture Value="false" />
                </Placement>
                <ClutterObject Name="AlienCatGiantMesh">
                    <LODs>
                        <LOD MinScreenSize="128">
                            <Mesh Id="HP_AlienCatG_Lod0" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod0.glb" />
                        </LOD>
                        <LOD MinScreenSize="64">
                            <Mesh Id="HP_AlienCatG_Lod1" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod1.glb" />
                        </LOD>
                        <LOD MinScreenSize="32">
                            <Mesh Id="HP_AlienCatG_Lod2" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod2.glb" />
                        </LOD>
                        <LOD MinScreenSize="16">
                            <Mesh Id="HP_AlienCatG_Lod3" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod3.glb" />
                        </LOD>
                        <LOD MinScreenSize="8">
                            <Mesh Id="HP_AlienCatG_Lod4" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod4.glb" />
                        </LOD>
                    </LODs>
                </ClutterObject>
                <Material>
                    <Diffuse Id="HP_AlienCatGDiff"
                        Path="Textures/Planets/Luna/GroundClutter/TestRocks_Diffuse.ktx2"
                        Category="Terrain"/>
                    <Normal Id="HP_AlienCatGNorm"
                        Path="Textures/Planets/Luna/GroundClutter/TestRocks_Normal.dds"
                        Category="Terrain"/>
                    <AoRoughMetal Id="HP_AlienCatGORM"
                        Path="Textures/Planets/Luna/GroundClutter/TestRocks_AoRoughMetal.dds"
                        Category="Terrain"/>
                    <UseTerrainMask Value="false" />
                    <DoubleSided Value="false" />
                    <CastShadows Value="true" />
                    <ReceiveShadows Value="true" />
                    <BiasNormalsUp Value="false" />
                    <ApplyExtraSpec Value="false" />
                    <DistanceFadeDither Value="true" />
                </Material>
            </Ecotype>
        </GroundClutter>
        {MARKER_CLUTTER_END}
"""

MARS_DECALS = f"""
                {MARKER_MARS_START}
                <Modifier Type="Decal" Name="MarsJezeroRings" Biomes="SandOnly,SandAndCliffs,VallesMarineris">
                    <Amplitude Value="5000" />
                    <Order Value="9997" />
                    <Radius Value="200000" />
                    <Rotation Degrees="0" />
                    <Location Id="HP_JezeroLocation">
                        <Latitude Degrees="18.4" />
                        <Longitude Degrees="77.6" />
                    </Location>
                    <AltitudeOffset Km="0" />
                    <SmoothFactor Value="0.05" />
                    <Additive Value="true" />
                    <HeightMap Id="HP_MarsJezeroRingsHM"
                        Path="Textures/Planets/Mars/MarsJezeroRings.png"
                        Category="Terrain"/>
                </Modifier>
                <Modifier Type="Decal" Name="MarsJezeroText" Biomes="SandOnly,SandAndCliffs,VallesMarineris">
                    <Amplitude Value="4000" />
                    <Order Value="9996" />
                    <Radius Value="150000" />
                    <Rotation Degrees="0" />
                    <Location Id="HP_JezeroTextLocation">
                        <Latitude Degrees="18.4" />
                        <Longitude Degrees="72.0" />
                    </Location>
                    <AltitudeOffset Km="0" />
                    <SmoothFactor Value="0.1" />
                    <Additive Value="true" />
                    <HeightMap Id="HP_MarsJezeroTextHM"
                        Path="Textures/Planets/Mars/MarsJezeroText.png"
                        Category="Terrain"/>
                </Modifier>
                <Modifier Type="Decal" Name="MarsIsidisRings" Biomes="SandOnly,SandAndCliffs,VallesMarineris">
                    <Amplitude Value="5000" />
                    <Order Value="9995" />
                    <Radius Value="200000" />
                    <Rotation Degrees="0" />
                    <Location Id="HP_IsidisLocation">
                        <Latitude Degrees="4.0" />
                        <Longitude Degrees="87.0" />
                    </Location>
                    <AltitudeOffset Km="0" />
                    <SmoothFactor Value="0.05" />
                    <Additive Value="true" />
                    <HeightMap Id="HP_MarsIsidisRingsHM"
                        Path="Textures/Planets/Mars/MarsIsidisRings.png"
                        Category="Terrain"/>
                </Modifier>
                {MARKER_MARS_END}
"""

def generate_textures():
    """Generate PNG heightmap textures for terrain decals."""
    from PIL import Image, ImageDraw, ImageFont, ImageFilter
    import math, random

    phobos_tex = CORE / "Textures/Planets/Phobos"
    luna_tex   = CORE / "Textures/Planets/Luna"
    phobos_tex.mkdir(parents=True, exist_ok=True)

    # Phobos Blob (organic amoeba shape)
    size = 512
    img = Image.new("RGBA", (size, size), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    cx, cy = size//2, size//2
    base_r = size * 0.38
    rng = random.Random(42)
    harmonics = [(1,.12),(2,.09),(3,.07),(4,.05),(5,.04),(7,.03)]
    phases = [rng.uniform(0, 2*math.pi) for _ in harmonics]
    def blob_r(theta):
        r = base_r
        for (freq,amp),phase in zip(harmonics,phases):
            r += base_r*amp*math.sin(freq*theta+phase)
        return r
    pts = [(cx+blob_r(2*math.pi*i/256)*math.cos(2*math.pi*i/256),
            cy+blob_r(2*math.pi*i/256)*math.sin(2*math.pi*i/256))
           for i in range(256)]
    draw.polygon(pts, fill=(255,255,255,255))
    img = img.filter(ImageFilter.GaussianBlur(radius=8))
    img.save(str(phobos_tex / "PhobosBlob.png"))

    # Phobos HelloWorld text (mirrored to correct decal projection)
    img2 = Image.new("RGBA", (size,size), (0,0,0,0))
    draw2 = ImageDraw.Draw(img2)
    font = None
    for fp in ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
               "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
        try: font = ImageFont.truetype(fp, 72); break
        except: pass
    if not font: font = ImageFont.load_default()
    for i, word in enumerate(["HELLO","WORLD"]):
        bb = draw2.textbbox((0,0),word,font=font)
        tw,th = bb[2]-bb[0],bb[3]-bb[1]
        x=(size-tw)//2; y=80+i*(th+30)
        for dx in range(-4,5):
            for dy in range(-4,5):
                draw2.text((x+dx,y+dy),word,fill=(180,180,180,255),font=font)
        draw2.text((x,y),word,fill=(255,255,255,255),font=font)
    img2 = img2.filter(ImageFilter.GaussianBlur(radius=3))
    img2 = img2.transpose(Image.FLIP_LEFT_RIGHT)
    img2.save(str(phobos_tex / "PhobosHelloWorld.png"))

    # Luna HelloMoon text
    img3 = Image.new("RGBA", (512,512), (0,0,0,0))
    draw3 = ImageDraw.Draw(img3)
    for i, word in enumerate(["HELLO","MOON"]):
        bb = draw3.textbbox((0,0),word,font=font)
        tw,th = bb[2]-bb[0],bb[3]-bb[1]
        x=(512-tw)//2; y=100+i*(th+40)
        for dx in range(-5,6):
            for dy in range(-5,6):
                draw3.text((x+dx,y+dy),word,fill=(160,160,160,255),font=font)
        draw3.text((x,y),word,fill=(255,255,255,255),font=font)
    img3 = img3.filter(ImageFilter.GaussianBlur(radius=4))
    img3 = img3.transpose(Image.FLIP_LEFT_RIGHT)
    img3.save(str(luna_tex / "LunaHelloMoon.png"))

    # Luna Landing Rings (concentric circles, RGBA)
    img4 = Image.new("RGBA", (512,512), (0,0,0,255))
    draw4 = ImageDraw.Draw(img4)
    cx4, cy4 = 256, 256
    for outer_f, inner_f, v in [(0.48,0.42,255),(0.35,0.29,220),
                                  (0.22,0.17,200),(0.11,0.07,230),(0.04,0,255)]:
        or_=int(outer_f*512); ir_=int(inner_f*512)
        draw4.ellipse([cx4-or_,cy4-or_,cx4+or_,cy4+or_],fill=(v,v,v,255))
        if inner_f>0:
            draw4.ellipse([cx4-ir_,cy4-ir_,cx4+ir_,cy4+ir_],fill=(0,0,0,255))
    for ang in [0,90,180,270]:
        a=math.radians(ang)
        arm=int(0.08*512); r=int(0.48*512); w=int(0.02*512)
        x1=int(cx4+r*math.sin(a)); y1=int(cy4-r*math.cos(a))
        x2=int(cx4+(r+arm)*math.sin(a)); y2=int(cy4-(r+arm)*math.cos(a))
        draw4.line([(x1,y1),(x2,y2)],fill=(255,255,255,255),width=max(2,w))
    img4 = img4.filter(ImageFilter.GaussianBlur(radius=3))
    img4.save(str(luna_tex / "LunaLandingRings.png"))

    # Mars landing target textures
    mars_tex = CORE / "Textures/Planets/Mars"
    mars_tex.mkdir(parents=True, exist_ok=True)

    def make_rings_rgba(filename):
        img = Image.new("RGBA", (512,512), (0,0,0,255))
        draw = ImageDraw.Draw(img)
        cx2, cy2 = 256, 256
        for outer_f, inner_f, v in [(0.48,0.42,255),(0.35,0.29,220),
                                     (0.22,0.17,200),(0.11,0.07,230),(0.04,0,255)]:
            or_=int(outer_f*512); ir_=int(inner_f*512)
            draw.ellipse([cx2-or_,cy2-or_,cx2+or_,cy2+or_],fill=(v,v,v,255))
            if inner_f>0:
                draw.ellipse([cx2-ir_,cy2-ir_,cx2+ir_,cy2+ir_],fill=(0,0,0,255))
        for ang2 in [0,90,180,270]:
            a2=math.radians(ang2); r2=int(0.48*512); arm2=int(0.10*512)
            x1=int(cx2+r2*math.sin(a2)); y1=int(cy2-r2*math.cos(a2))
            x2=int(cx2+(r2+arm2)*math.sin(a2)); y2=int(cy2-(r2+arm2)*math.cos(a2))
            draw.line([(x1,y1),(x2,y2)],fill=(255,255,255,255),width=max(3,512//60))
        img = img.filter(ImageFilter.GaussianBlur(radius=4))
        img.save(str(mars_tex/filename))

    def make_text_rgba(filename, lines):
        img = Image.new("RGBA",(512,512),(0,0,0,0))
        draw = ImageDraw.Draw(img)
        fnt = None
        for fp in ["/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
                   "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"]:
            try: fnt=ImageFont.truetype(fp,80); break
            except: pass
        if not fnt: fnt=ImageFont.load_default()
        for i,word in enumerate(lines):
            bb=draw.textbbox((0,0),word,font=fnt)
            tw,th=bb[2]-bb[0],bb[3]-bb[1]
            x=(512-tw)//2; y=60+i*(th+30)
            for dx in range(-5,6):
                for dy in range(-5,6):
                    draw.text((x+dx,y+dy),word,fill=(160,160,160,255),font=fnt)
            draw.text((x,y),word,fill=(255,255,255,255),font=fnt)
        img=img.filter(ImageFilter.GaussianBlur(radius=3))
        img=img.transpose(Image.FLIP_LEFT_RIGHT)
        img.save(str(mars_tex/filename))

    make_rings_rgba("MarsJezeroRings.png")
    make_rings_rgba("MarsIsidisRings.png")
    make_text_rgba("MarsJezeroText.png", ["JEZERO","CRATER"])
    make_text_rgba("MarsIsidisText.png", ["ISIDIS","PLANITIA"])

    print("  Textures generated")


def copy_core_assets():
    """Copy Core Luna assets into mod folder (not redistributed in package)."""
    copies = [
        (CORE/"Textures/Planets/Luna/GroundClutter/TestRocks_Diffuse.ktx2",
         MOD/"Textures/Planets/Luna/GroundClutter/TestRocks_Diffuse.ktx2"),
        (CORE/"Textures/Planets/Luna/GroundClutter/TestRocks_Normal.dds",
         MOD/"Textures/Planets/Luna/GroundClutter/TestRocks_Normal.dds"),
        (CORE/"Textures/Planets/Luna/GroundClutter/TestRocks_AoRoughMetal.dds",
         MOD/"Textures/Planets/Luna/GroundClutter/TestRocks_AoRoughMetal.dds"),
    ]
    for src, dst in copies:
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    # Luna rock GLBs
    for i in range(5):
        src = CORE/f"Meshes/Planets/Luna/GroundClutter/Rock0Lod{i}.glb"
        dst = MOD/f"Meshes/Planets/Luna/GroundClutter/Rock0Lod{i}.glb"
        if src.exists():
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
    print("  Core assets copied")


def patch_astronomicals():
    text = ASTRO.read_text(encoding="utf-8")
    if MARKER_LUNA_START in text:
        print("  Core/Astronomicals.xml already patched")
        return

    shutil.copy2(ASTRO, ASTRO_BAK)
    print(f"  Backed up to {ASTRO_BAK.name}")

    # 1. Luna decals — insert before TestDecal (confirmed inside Luna block)
    insert_before = '<Modifier Type="Decal" Name="TestDecal" Biomes="Maria">'
    pos = text.find(insert_before)
    if pos == -1:
        sys.exit("ERROR: TestDecal not found in Luna block")
    text = text[:pos] + LUNA_DECALS + text[pos:]

    # 2. Phobos decals — insert before </ProceduralModifiers> in Phobos block
    phobos_start = text.find('<MinorBody Id="Phobos"')
    close = "</ProceduralModifiers>"
    pos2 = text.find(close, phobos_start)
    text = text[:pos2] + PHOBOS_DECALS + text[pos2:]

    # 3. Phobos GroundClutter — insert after </BiomeMaterials> in Phobos block
    phobos_start = text.find('<MinorBody Id="Phobos"')
    bm_close = "</BiomeMaterials>"
    pos3 = text.find(bm_close, phobos_start) + len(bm_close)
    text = text[:pos3] + "\n" + PHOBOS_CLUTTER + text[pos3:]

    # 4. Mars decals — insert before </ProceduralModifiers> in Mars block
    mars_start = text.find('<AtmosphericBody Id="Mars"')
    if mars_start == -1:
        mars_start = text.find('<PlanetaryBody Id="Mars"')
    mars_proc_close = "</ProceduralModifiers>"
    pos4 = text.find(mars_proc_close, mars_start)
    text = text[:pos4] + MARS_DECALS + text[pos4:]

    # 5. Luna landmarks — after Apollo15
    anchor = '<Landmark Id="Apollo15">'
    ap_pos = text.find(anchor)
    close_lm = text.find("</Landmark>", ap_pos) + len("</Landmark>")
    luna_lm = """
        <Landmark Id="HelloMoon">
            <Latitude Degrees="0.674" />
            <Longitude Degrees="16.0" />
        </Landmark>
        <Landmark Id="LandingRings">
            <Latitude Degrees="0.674" />
            <Longitude Degrees="11.0" />
        </Landmark>
        <Landmark Id="TestDecalSite">
            <Latitude Degrees="0.0" />
            <Longitude Degrees="0.0" />
        </Landmark>"""
    text = text[:close_lm] + luna_lm + text[close_lm:]

    # 5. Mars landmarks — after Spirit landmark
    spirit_pos = text.find('<Landmark Id="Spirit">')
    close_spirit = text.find("</Landmark>", spirit_pos) + len("</Landmark>")
    mars_lm = """
        <Landmark Id="JezeroCrater">
            <Latitude Degrees="18.4" />
            <Longitude Degrees="77.6" />
        </Landmark>
        <Landmark Id="IsidisPlanitia">
            <Latitude Degrees="4.0" />
            <Longitude Degrees="87.0" />
        </Landmark>"""
    text = text[:close_spirit] + mars_lm + text[close_spirit:]

    # 7. Phobos landmarks — after </Rotation> in Phobos block
    phobos_start = text.find('<MinorBody Id="Phobos"')
    rot_close = text.find("</Rotation>", phobos_start) + len("</Rotation>")
    phobos_lm = """
        <Landmark Id="HelloWorld">
            <Latitude Degrees="0.0" />
            <Longitude Degrees="0.0" />
        </Landmark>
        <Landmark Id="AlienBlob">
            <Latitude Degrees="0.0" />
            <Longitude Degrees="0.0" />
        </Landmark>"""
    text = text[:rot_close] + phobos_lm + text[rot_close:]

    ASTRO.write_text(text, encoding="utf-8")

    r = subprocess.run(["xmllint","--noout",str(ASTRO)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        shutil.copy2(ASTRO_BAK, ASTRO)
        sys.exit(f"XML validation failed — restored backup\n{r.stderr}")
    print("  Core/Astronomicals.xml patched")


def unpatch_astronomicals():
    if not ASTRO_BAK.exists():
        print("  No backup found")
        return
    shutil.copy2(ASTRO_BAK, ASTRO)
    ASTRO_BAK.unlink()
    print("  Core/Astronomicals.xml restored")


def patch_manifest():
    text = MANIFEST.read_text()
    if 'id = "HelloPhobos"' in text:
        print("  manifest.toml already registered")
        return
    with open(MANIFEST,"a") as f:
        f.write('\n[[mods]]\nid = "HelloPhobos"\nenabled = true\n')
    print("  manifest.toml updated")


def unpatch_manifest():
    text = MANIFEST.read_text()
    cleaned = re.sub(
        r'\n\[\[mods\]\]\nid = "HelloPhobos"\nenabled = (true|false)\n',
        '', text)
    MANIFEST.write_text(cleaned)
    print("  HelloPhobos removed from manifest.toml")


def remove_core_assets():
    for d in [MOD/"Meshes/Planets/Luna",
              MOD/"Textures/Planets/Luna"]:
        if d.exists():
            shutil.rmtree(d)
    print("  Core asset copies removed")


def install():
    print("\nHelloPhobos Installer")
    print("=" * 50)
    try:
        from PIL import Image
        generate_textures()
    except ImportError:
        print("  WARN: Pillow not installed — textures not regenerated")
        print("        pip install pillow --break-system-packages")
        if not (CORE/"Textures/Planets/Phobos/PhobosBlob.png").exists():
            sys.exit("  ERROR: Textures missing. Install Pillow and re-run.")

    copy_core_assets()
    patch_astronomicals()
    patch_manifest()

    print(f"""
✓ Installation complete!

WHAT'S INSTALLED:
  Phobos — HELLO WORLD terrain text visible from close orbit
           Alien blob creature terrain feature
           Landmarks: HelloWorld, AlienBlob
           GroundClutter: small and giant alien rock creatures

  Luna   — HELLO MOON terrain text (lon=16, lat=0.674)
           Landing rings challenge target (lon=11, lat=0.674)
           Landmarks: HelloMoon, LandingRings, TestDecalSite

  Starting situations:
           PhobosAliens  — low Phobos orbit above HelloWorld site
           MarsLanding   — low Mars orbit, start near Jezero Crater

KNOWN LIMITATIONS (KSA pre-alpha):
  - GroundClutter from mod Astronomicals.xml does not merge with Core
    (creatures use Core/Astronomicals.xml insertion — rock placeholders)
  - Terrain decals modify height only (no colour change)
  - Luna surface features subtle due to existing terrain variation
  - Orbital visibility of Luna features requires close approach

Launch KSA and select 'Phobos Alien Encounter' from the system menu.
""")


def uninstall():
    print("\nHelloPhobos Uninstaller")
    print("=" * 50)
    unpatch_astronomicals()
    remove_core_assets()
    unpatch_manifest()
    print("\n✓ Uninstalled. KSA restored to vanilla state.")


if __name__ == "__main__":
    if "--uninstall" in sys.argv:
        uninstall()
    else:
        install()
