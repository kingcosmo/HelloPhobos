# HelloPhobos — KSA Mod

Adds alien life forms to Phobos using KSA's native GroundClutter system —
the same GPU-driven scatter pipeline used for Luna's rocks and Earth's grass.

## Mod structure

```
Content/HelloPhobos/
├── mod.toml                              ← mod manifest
├── Astronomicals.xml                     ← adds GroundClutter to Phobos
├── generate_assets.py                    ← creates placeholder GLBs + textures
├── Meshes/Planets/Phobos/GroundClutter/
│   ├── AlienA_Lod0.glb  ..  AlienA_Lod4.glb   (Rock-Crawler)
│   └── AlienB_Lod0.glb  ..  AlienB_Lod4.glb   (Dust Drifter)
└── Textures/Planets/Phobos/GroundClutter/
    ├── Aliens_Diffuse.dds
    ├── Aliens_Normal.dds
    ├── Aliens_AoRoughMetal.dds
    ├── AlienA_Distribution.dds           ← uniform scatter (everywhere)
    └── AlienB_Distribution.dds           ← colony blobs (sparse patches)
```

---

## Install

```bash
KSA=/data/cosmo/Downloads/ksa/linux-x64/Content

# Copy mod folder
cp -r HelloPhobos_v3/  $KSA/HelloPhobos/

# Register in manifest.toml
cat >> $KSA/manifest.toml << 'EOF'

[[mods]]
id = "HelloPhobos"
enabled = true
EOF
```

---

## Generate placeholder assets

```bash
cd $KSA/HelloPhobos/

# Meshes only (pure stdlib, no dependencies)
python3 generate_assets.py

# Meshes + textures (needs Pillow)
pip install pillow --break-system-packages
python3 generate_assets.py
```

The placeholders work immediately. AlienA will be a squat olive ellipsoid,
AlienB a tall purple capsule. Replace with proper Blender exports when ready.

---

## Test without any custom assets

The fastest way to confirm the mod loads is to temporarily borrow Luna's
existing rock meshes. Edit `Astronomicals.xml` and replace all Phobos mesh
paths with Luna ones:

```xml
<!-- swap this: -->
<Mesh Id="HP_AlienA_Lod0" Path="Meshes/Planets/Phobos/GroundClutter/AlienA_Lod0.glb" />
<!-- for this: -->
<Mesh Id="HP_AlienA_Lod0" Path="Meshes/Planets/Luna/GroundClutter/Rock0Lod0.glb" />
```

And similarly point the Material textures at Luna's atlas:
```xml
<Diffuse Id="HP_AliensDiffuse" Path="Textures/Planets/Luna/GroundClutter/TestRocks_Diffuse.ktx2" Category="Terrain"/>
<Normal  Id="HP_AliensNormal"  Path="Textures/Planets/Luna/GroundClutter/TestRocks_Normal.dds"   Category="Terrain"/>
<AoRoughMetal Id="HP_AliensAoRoughMetal" Path="Textures/Planets/Luna/GroundClutter/TestRocks_AoRoughMetal.dds" Category="Terrain"/>
```

Luna rocks on Phobos — ugly but proves the pipeline works before investing
time in custom meshes.

---

## How the schema works (verified from Core source)

```
<Assets>                              ← root element of Astronomicals.xml
  <MinorBody Id="Phobos" ...>         ← engine merges with Core's definition
    <GroundClutter>                   ← sibling of <Terrain>, not nested in it
      <Ecotype Name="...">
        <Placement Biomes="Surface">  ← "Surface" = Phobos's only biome
          <ObjectSeparation M="4.0"/> ← metres between instances
          <GenerationRange M="170"/>  ← generation radius around camera
          <MinScale .../> <MaxScale .../>
          <Orientation Mode="SurfaceNormalSmooth"/>
          <MinRotation .../> <MaxRotation .../>
          <DistributionTexture Id="..." Path="..."/>
          <DistributionTextureTiling Value="50"/>
          <UseObjectTypeTexture Value="false"/>
        </Placement>
        <ClutterObject Name="...">
          <LODs>
            <LOD MinScreenSize="128"> <Mesh Id="..." Path="..."/> </LOD>
            <LOD MinScreenSize="64">  ... </LOD>
            <LOD MinScreenSize="32">  ... </LOD>
            <LOD MinScreenSize="16">  ... </LOD>
            <LOD MinScreenSize="8">   ... </LOD>
          </LODs>
        </ClutterObject>
        <Material>
          <Diffuse      Id="..." Path="..." Category="Terrain"/>
          <Normal       Id="..." Path="..." Category="Terrain"/>
          <AoRoughMetal Id="..." Path="..." Category="Terrain"/>
          <DoubleSided Value="false"/>
          <CastShadows Value="true"/>
          <ReceiveShadows Value="true"/>
          <DistanceFadeDither Value="true"/>
          ...
        </Material>
      </Ecotype>
    </GroundClutter>
  </MinorBody>
</Assets>
```

All `Id=""` values must be globally unique. This mod prefixes everything
with `HP_` to avoid clashing with Core.

---

## Making proper alien meshes in Blender

1. Model your creature (keep it simple — the GroundClutter system renders
   thousands of instances, so low-poly is correct)
2. Create 5 LOD versions: Lod0 (~500 tris) → Lod4 (~20 tris or flat quad)
3. Export: File → Export → glTF 2.0, Format: GLB, include normals
4. Name: `AlienA_Lod0.glb` etc.
5. Author PBR textures as a texture atlas (both alien types on one sheet):
   - Diffuse: RGB base colour
   - Normal: RGB normal map (OpenGL convention: G=up)
   - AoRoughMetal: R=AO, G=Roughness, B=Metallic (packed)
   - Distribution: single-channel greyscale density map (512×512 recommended)

For DDS conversion on Linux:
```bash
# Using ImageMagick
convert input.png -define dds:compression=dxt1 output.dds

# Or leave as .png and update paths in Astronomicals.xml — KSA may accept both
```

---

## Next steps

- **HELLO WORLD sign**: Add a `<Modifier Type="Decal">` inside Phobos's
  `<Terrain><ProceduralModifiers>` block in a separate Astronomicals.xml
  entry — this is how Luna's `TestDecal` works. Paint your text into a
  heightmap PNG and reference it with `<HeightMap>` + `<Location>`.

- **More creature types**: Add more `<ClutterObject>` entries inside an
  Ecotype, or add more Ecotypes with their own distribution maps.

- **Animated aliens**: GroundClutter currently renders static meshes. For
  animated creatures you'll need a C# code mod hooking into the entity
  system — the `AlienCreature.cs` from v1 of this mod is the starting point.
