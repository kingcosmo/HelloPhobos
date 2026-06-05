# HelloPhobos — KSA Mod v0.1.0
### A First Modding Expedition into Kitten Space Agency

---

## Installation

```bash
# 1. Copy mod folder to KSA Content directory
cp -r HelloPhobos/  /path/to/ksa/linux-x64/Content/

# 2. Run installer from KSA root
cd /path/to/ksa/linux-x64
python3 Content/HelloPhobos/install.py

# 3. Launch KSA
./KSA
```

**Requirements:** Python 3.10+, Pillow (`pip install pillow --break-system-packages`)

To uninstall: `python3 Content/HelloPhobos/install.py --uninstall`

---

## What's in the Mod

### Phobos
| Feature | Type | Location | Status |
|---|---|---|---|
| HELLO WORLD text | Terrain decal | lat=0, lon=0 | ✓ Working |
| Alien blob creature | Terrain decal | lat=0, lon=0 | ✓ Working |
| HelloWorld landmark | Navigation marker | lat=0, lon=0 | ✓ Working |
| AlienBlob landmark | Navigation marker | lat=0, lon=0 | ✓ Working |
| Small alien rocks | GroundClutter | Phobos surface | ✓ Working (rock placeholder mesh) |
| Giant alien rocks | GroundClutter | Phobos surface | ✓ Working (rock placeholder mesh) |

### Luna
| Feature | Type | Location | Status |
|---|---|---|---|
| HELLO MOON text | Terrain decal | lat=0.674, lon=16.0 | ✓ Working (height only) |
| Landing rings | Terrain decal | lat=0.674, lon=11.0 | ✓ Working (height only) |
| HelloMoon landmark | Navigation marker | lat=0.674, lon=16.0 | ✓ Working |
| LandingRings landmark | Navigation marker | lat=0.674, lon=11.0 | ✓ Working |
| TestDecalSite landmark | Navigation marker | lat=0, lon=0 | ✓ Working |

### Starting Situations
| System | Description | Status |
|---|---|---|
| Phobos Alien Encounter | Low Phobos orbit, Gemini7 above HelloWorld | ✓ Working |

---

## KSA Modding Findings (v2026.6.x)

This mod was developed through extensive reverse-engineering of KSA's data
format during June 2025. These findings are intended to help the KSA modding
community.

### What Works

**1. Terrain Decals**
The most powerful confirmed modding feature. Add `<Modifier Type="Decal">` 
inside a body's `<Terrain><ProceduralModifiers>` block.

```xml
<Modifier Type="Decal" Name="MyDecal" Biomes="Surface">
    <Amplitude Value="1200" />     <!-- metres of terrain raise -->
    <Order Value="9999" />          <!-- higher = renders on top -->
    <Radius Value="2000" />         <!-- metres radius on surface -->
    <Rotation Degrees="0" />
    <Location Id="MyLocation">
        <Latitude Degrees="0.0" />
        <Longitude Degrees="0.0" />
    </Location>
    <AltitudeOffset Km="0" />
    <SmoothFactor Value="0.2" />    <!-- 0=sharp, 1=smooth -->
    <Additive Value="true" />
    <HeightMap Id="MyHeightMapId"
        Path="Textures/Planets/Phobos/MyHeightmap.png"
        Category="Terrain"/>
</Modifier>
```

**HeightMap format:** Must be RGBA PNG (not greyscale L mode). White pixels
raise terrain, black pixels leave terrain flat. The same format as
`Core/Textures/Planets/Luna/TestDecalHeight.png` (128×128 RGBA).

**Key discovery:** Decals must specify `Biomes=` matching the body's defined
biomes. Luna has `Surface`, `Craters`, `Maria`. Phobos has only `Surface`.
Without the Biomes attribute, the decal silently fails.

**Key discovery:** Decals must be inserted into the CORRECT body's
`<ProceduralModifiers>` block. A common mistake is inserting into a
neighbouring body's block — the XML is large and the blocks are easy to
confuse. Always verify by checking line context.

**2. Landmarks**
Simple named navigation markers in the map view.

```xml
<Landmark Id="MyLandmark">
    <Latitude Degrees="0.674" />
    <Longitude Degrees="16.0" />
</Landmark>
```

Must be placed at the body level (sibling of `<MeanRadius>`, `<Mass>` etc),
NOT inside `<Terrain>`. The Apollo landing sites show the correct pattern.

**3. GroundClutter (confirmed schema)**
The GroundClutter scatter system works for Earth and Luna in Core and CAN
be added to other bodies. The schema is:

```xml
<GroundClutter>
    <Ecotype Name="MyCreatures">
        <Placement Biomes="Surface">
            <ObjectSeparation M="5.0" />
            <GenerationRange M="170" />
            <MinScale X="1.0" Y="1.0" Z="1.0" />
            <MaxScale X="3.0" Y="3.0" Z="3.0" />
            <Orientation Mode="SurfaceNormalSmooth" />
            <MinRotation Degrees="0" />
            <MaxRotation Degrees="360" />
            <DistributionTexture Id="UniqueId"
                Path="Textures/..." />
            <DistributionTextureTiling Value="50" />
            <UseObjectTypeTexture Value="false" />
        </Placement>
        <ClutterObject Name="MyMesh">
            <LODs>
                <LOD MinScreenSize="128">
                    <Mesh Id="UniqueId" Path="Meshes/..." />
                </LOD>
                <!-- LODs at 64, 32, 16, 8 -->
            </LODs>
        </ClutterObject>
        <Material>
            <Diffuse Id="UniqueId" Path="Textures/..." Category="Terrain"/>
            <Normal  Id="UniqueId" Path="Textures/..." Category="Terrain"/>
            <AoRoughMetal Id="UniqueId" Path="..." Category="Terrain"/>
            <!-- Render flags -->
        </Material>
    </Ecotype>
</GroundClutter>
```

**Material textures MUST be DDS or KTX2 format.** PNG is silently ignored.
The working Core textures use:
- Diffuse: BC7 KTX2 (4096×4096)
- Normal: ATI2/BC5 DDS (4096×4096)  
- AoRoughMetal: DXT1/BC1 DDS (4096×4096)

**Distribution texture** is greyscale (L mode PNG acceptable), controlling
instance density. White=maximum density, black=no instances.
`DistributionTextureTiling` controls how many times the texture tiles across
the body surface.

**4. Custom Systems and Situations**
Add `systems = ["MySystem.xml"]` to `mod.toml`. System XML follows the same
pattern as Core's `SolSystem.xml`. Situations define orbital parameters.

**Important:** As of v2026.6, situations work for Earth-parent orbits and
Phobos-parent orbits. Luna-parent orbits produce NaN orbital energy errors
(suspected physics calculation issue with Luna's reference frame in the
Ecliptic definition frame).

**5. Mod Asset Path Resolution**
All texture/mesh paths in a mod's `Astronomicals.xml` are resolved relative
to the MOD's own folder, not Core. `Path="Textures/Foo.ktx2"` resolves to
`Content/HelloPhobos/Textures/Foo.ktx2`.

This means you cannot reference Core assets directly from a mod XML.
You must either copy them into your mod folder (permitted for runtime use,
not redistribution) or the installer must copy them at install time.

---

### What Doesn't Work (Yet)

**1. GroundClutter from mod Astronomicals.xml does not merge with Core**
When a mod defines `<GroundClutter>` in its own `Astronomicals.xml`, the
engine does not merge it with Core's definition — it is silently ignored.
Only GroundClutter defined in Core's `Astronomicals.xml` registers and logs
`Ecotype: Name VRAM Usage: N MB`.

**Workaround:** The installer injects GroundClutter directly into
Core/Astronomicals.xml. This works but is fragile across KSA updates.

**2. Terrain decals are height-only**
The `<Modifier Type="Decal">` system modifies terrain height (displacement)
but does not support colour/albedo changes. Text and shapes are visible as
terrain relief (raised bumps/ridges) but look like natural terrain features.

To add colour to a decal region, the biome system would need to be used —
painting a custom biome ID map texture to assign a different material to the
decal area. This requires editing `Luna_Biome_ID.ktx2` (BC7 KTX2 format),
which is technically possible but complex.

**3. Orbital sprite texture editing (Luna_Diffuse.ktx2) causes crashes**
The orbital-distance view of planets uses BC7-compressed KTX2 cubemap
textures. Editing these and recompressing with available Linux tools (ISPC
Texture Compressor) produces BC7 blocks that crash KSA's Vulkan image
allocator (`Vma Failed to create image`). The original encoder used by the
KSA developers produces different BC7 block patterns that the driver accepts.

This means features painted onto the orbital sprite texture are currently
not achievable without the original encoder or a compatible replacement.

**4. Skinned mesh GLBs rejected by GroundClutter**
The KSA_Cat character mesh (`KSA_Cat.gltf`) includes a full skeletal rig.
When used as a GroundClutter ClutterObject mesh, it appears to be silently
rejected or causes rendering issues. GroundClutter expects static (non-
skinned) GLB geometry. Simple sphere/capsule GLBs generated by Python also
appear to be rejected, possibly due to BC7 block format mismatches in the
material pipeline.

**5. Luna-parent orbital situations produce NaN**
Situation `<Orbit>` with a vehicle `Parent="Luna"` causes
`unclassifiable orbital energy: NaN` regardless of SemiMajorAxis value.
All working starting situations use `Parent="Earth"`. This may be a
coordinate frame issue with the Luna-Ecliptic reference frame transformation.

---

### Architecture Discoveries

**Mod loading:** Each enabled mod contributes its `assets` XML files.
The engine loads `Astronomicals.xml` from ALL mods. However, if a mod
defines a body (`<MinorBody Id="Phobos">`) that Core already defines,
the engine takes Core's definition and the mod's additions are merged for
SOME features (decals via `assets` XML work) but not others (GroundClutter
does not merge).

**Asset ID uniqueness:** All `Id=""` attributes across ALL loaded mods must
be globally unique. Prefix all IDs with your mod identifier (e.g. `HP_`).

**Cubemap face orientation:** KSA uses the following convention for planet
diffuse cubemap textures:
- Face 4 (+Z): lon near 0° (Mars-facing side of Phobos, near-side of Luna)
- Face 5 (-Z): lon near 180°
- Face 0 (+X): lon near 90°
- Face 1 (-X): lon near 270°
- Convention: x=cos(lat)×sin(lon), y=sin(lat), z=cos(lat)×cos(lon)

Verified by calibration against Apollo 11 (lat=0.674°, lon=23.473°) which
maps to face 4 (+Z) at approximately UV(0.41, 0.49).

**Console commands discovered:**
- `followq <celestial>` — follow and tidally lock to celestial surface
- `gotoJ <lat> <lon>` — jump camera to lat/lon on nearby body
- `altitude <value> <units>` — set camera altitude (ms, kms, aus)
- `camera <mode>` — set camera mode (map, orbit)
- `simspeed <n>` — set simulation speed multiplier
- `control <vehicle_id>` — switch controlled vehicle

These can be added to `mod.toml` `[console] onLoad = [...]` to run at startup.

---

### Future Mod Development Roadmap

See the companion document `ROADMAP.md` for the full vision of an alien
civilisation mod suite built on top of KSA. The key architectural insight
is that a Python daemon running alongside KSA (communicating via a thin
C# bridge mod) can implement the simulation and AI logic that KSA's native
mod API doesn't yet expose.

**Priority items pending KSA API maturity:**
1. GroundClutter merging from mod XMLs (currently Core-only)
2. Custom character/entity spawning API
3. Luna-parent orbital situations
4. Biome texture hot-reload for coloured surface markings
5. Surface-placed (non-orbital) vessel starting positions

---

## File Structure

```
HelloPhobos/
├── install.py                    ← Run this to install/uninstall
├── mod.toml                      ← Mod manifest
├── Astronomicals.xml             ← Mod-level (placeholder, see install.py)
├── Situations.xml                ← PhobosHelloWorldSituation
├── PhobosSystem.xml              ← "Phobos Alien Encounter" starting system
├── Meshes/
│   └── Planets/
│       ├── Luna/GroundClutter/   ← Copied from Core at install time
│       └── Phobos/GroundClutter/ ← AlienCat LOD GLBs (kitten mesh)
└── Textures/
    ├── Planets/
    │   ├── Phobos/GroundClutter/ ← Alien skin textures (PNG — not used yet)
    │   └── Phobos/               ← Decal heightmaps (generated at install)
    └── Planets/Luna/GroundClutter/ ← Copied from Core at install time
```

Files added to Core at install time:
```
Core/Textures/Planets/Phobos/
    PhobosBlob.png
    PhobosHelloWorld.png
Core/Textures/Planets/Luna/
    LunaHelloMoon.png
    LunaLandingRings.png
Core/Astronomicals.xml           ← Patched (backup at .hellophobos.bak)
```

---

## Credits

Developed on dwalin (Debian Linux, RTX 4070) using:
- KSA v2026.6.2.4531 (native Linux build)
- Python 3.13, Pillow, zstandard, bcdec, ISPC Texture Compressor
- xmllint, ktx-software v4.3.2

Special thanks to the KSA developers for building a genuinely mod-friendly
game architecture — the data-driven XML content system made this exploration
possible even in pre-alpha.
