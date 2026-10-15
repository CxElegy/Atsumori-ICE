# ACNH (v2.0) Island Designer / Terraforming: Fundamentals

**C** = CONFIRMED, **U** = UNSURE. "HID src" = HappyIslandDesigner at commit 68afa9f (Mar 2026): https://github.com/eugeneration/HappyIslandDesigner

Short source keys:
- NP-ID = https://nookipedia.com/wiki/Island_Designer
- G8-TF = https://game8.co/games/Animal-Crossing-New-Horizons/archives/284501
- G8-WF = https://game8.co/games/Animal-Crossing-New-Horizons/archives/289409
- G8-CL = https://game8.co/games/Animal-Crossing-New-Horizons/archives/316295
- G8-RV = https://game8.co/games/Animal-Crossing-New-Horizons/archives/316298
- G8-IN = https://game8.co/games/Animal-Crossing-New-Horizons/archives/286502
- G8-BR = https://game8.co/games/Animal-Crossing-New-Horizons/archives/284596
- GG-CL = https://www.gamerguides.com/animal-crossing-new-horizons/guide/your-island/terraforming/cliff-construction
- GG-WS = https://www.gamerguides.com/animal-crossing-new-horizons/guide/your-island/terraforming/waterscaping
- iM = https://www.imore.com/animal-crossing-new-horizons-terraforming-guide

## 1. Map geometry

| Fact | Tag | Source |
|---|---|---|
| The map is 7×6 acres (42 acres). | C | https://nookipedia.com/wiki/Town ; HID src `app/constants.ts` (`horizontalBlocks=7, verticalBlocks=6`) |
| One acre is 16×16 tiles, so the whole map is 112×96 tiles. | C | HID src `constants.ts` (`horizontalDivisions=16`), `app/ui/edgeTiles.ts` ("7 * 16 = 112", "6 * 16 = 96"); https://www.laps4.com/preguntas-y-respuestas/cuanto-mide-la-isla-de-animal-crossing-new-horizons-1 |
| The outer ring of acres (x=0, x=6, y=0, y=5) is shoreline/sea "edge tiles". That leaves a 5×4-acre interior of **80×64 tiles** that you can freely terraform. The edge acres still hold some land at their inner edge. | C (ring) / U (exact usable inner-edge strip) | HID src `edgeTiles.ts` ("Edge tiles occupy: x=0 and x=6, y=0 and y=5") |
| The airport is always on the south shoreline. Its east-west position varies. HID footprint: 10×6. | C | https://nookipedia.com/wiki/Town ; HID src `edgeTileAssets.ts` (`airport` only in `bottom`), `amenities.ts` (`Size(10,6)`) |
| There are 2 river mouths: both on the south shore, or 1 south plus 1 east or west. Never north. | C | https://nookipedia.com/wiki/Town ; HID src `edgeTileAssets.ts` (`left_river`, `right_river`, `bottom_river` only) |
| Edge features by side. North: secret beach and big rocks. East/west: peninsula, river mouth or rocks. South: airport, river. Bottom-left or bottom-right corner: wooden pier/dock (HID 7×2). | C | HID src `edgeTileAssets.ts` (`top_secret_beach`, `left/right_peninsula`, `left/right_rock`, `bottom_left_dock`/`bottom_right_dock`); https://nookipedia.com/wiki/Town ("north side has very large rocks and a tiny section of beach") |
| Resident Services is fixed (HID: 6×4 building on a 12×10 plaza). You cannot terraform the plaza. | C | G8-TF ("All facilities can be moved except Airport and Resident Services"); NP-ID (restricted: RS Plaza, Airport Dock); HID src `amenities.ts` (`Rectangle(0,0,12,10)`) |
| You cannot reshape the beach, the beach rocks or the river mouths (estuaries). You cannot dig water on the beach or on the beach border. | C | NP-ID; G8-TF ("can't modify the beach… estuaries"); GG-WS ("estuaries… permanent"); iM |
| Paths on the beach: Nookipedia says you must stand on grass except for the Custom Design path ("can be used anywhere"). The HID blog says the sand path also works on the beach. | C (custom) / U (sand) | NP-ID; https://happyislanddesigner.com/blog/terraforming-tips |

## 2. Cliffs

| Fact | Tag | Source |
|---|---|---|
| Natural islands have 3 levels. With the permit you can build a 4th tier, but you cannot climb it (the Ladder refuses), you cannot place items on it, and inclines cannot reach it. "4 levels" counts the ground as level 1. | C | https://nookipedia.com/wiki/Cliff ; G8-TF; G8-CL; https://nookipedia.com/wiki/Incline |
| You build and remove cliffs from the lower level, facing the tile. You cannot destroy a cliff while standing on top of it. | C | GG-CL; iM |
| A cliff can't be removed while water or objects (flowers, trees) are on top of it. | C | NP-ID |
| Pressing A on a cliff corner rounds it to a 45° half-tile, which cannot hold items or flowers. Pressing again removes the tile. 3×3 or larger: all corners round. 2×3: one side only. 2×2: opposite corners only (a "leaf"). | C | iM; G8-CL; NP-ID |
| Minimum width: 2 tiles for a single-level cliff. A 1×1 cliff needs a glitch. | C (2 agreeing; Game8 + Switchblade) | G8-WF ("at least 2 spaces wide for a single-level cliff"); https://www.switchbladegaming.com/cozy-games/animal-crossing-island-design-guide/ ; https://animalcrossingworld.com/2020/07/plant-trees-on-cliff-edges-in-animal-crossing-new-horizons-with-this-handy-glitch/ |
| Stacking: an upper tier must sit at least 1 tile in from the lower cliff edge (a 1-tile ledge). So a two-level cliff needs a lower tier at least 4 wide (1 + 2 + 1). | C | GG-CL ("must have one tile between the other cliff edge"); NP-ID ("not right at the edge"); G8-WF ("lower cliff… at least 4 spaces wide") |
| Cliffs cannot be created near trees, rocks, buildings, bridges, inclines or furniture, or on the beach or rocks. A tree must be at least 1 tile away. | C | NP-ID; GG-CL ("cannot place cliffs within one tile of a tree"); iM |
| Cliffs cannot be built directly next to Resident Services or too close to the airport. | U (no number given) | https://happyislanddesigner.com/blog/terraforming-tips |
| Cliffs can touch water (rivers along cliff bases, waterfalls through them). Some rounding is refused as "too close to bodies of water". | C / U (rounding: user comment) | G8-RV; G8-CL comments; HID src `layerDefinition.ts` ("rivers cut through cliffs") |

## 3. Waterscaping

| Fact | Tag | Source |
|---|---|---|
| Pressing A digs a water tile or fills one in. Pressing A on an edge rounds it (a 45° half-tile), and diagonal rivers are made this way. | C | GG-WS; iM; G8-RV |
| You cannot place water near trees, rocks, buildings, bridges or inclines. The gap is 1 tile from a tree or house. | C | NP-ID; GG-WS |
| River mouths are fixed. You cannot create, move or remove one. Water cannot touch the beach. | C | iM; GG-WS; NP-ID |
| River vs pond: water counts as a river if it is connected to a waterfall or a river mouth, or is long and thin. Otherwise it is a pond. | C | G8-RV; iM |
| Fish spawn only in at least 3×3 tiles of water. | C | G8-RV; G8-WF |
| A 1-tile-wide channel can be dug. No source states a minimum width, and 1-tile water spawns no fish. | U | GG-WS ("doesn't state a minimum") |
| A waterfall forms where water is dug at a cliff edge from the upper level. You cannot make one from below. It needs cliffs on both sides. | C | NP-ID; G8-WF |
| A waterfall needs a cliff of at least 2×3 (for a 1-tile fall). It must be at least 1 tile from a cliff corner, and it cannot be on a curved (rounded) cliff edge. | C | G8-WF; iM |
| Two-level cascades work (tier 3 → 2 → 1). A three-level fall is impossible. To remove a waterfall's cliff, fill the waterfall in first. | C | G8-WF; NP-ID |
| No documented cap on the number of waterfalls. | U | none found |

## 4. Paths

| Fact | Tag | Source |
|---|---|---|
| Free paths: Grass (works as an eraser) and Dirt. 2,000 Miles each: Stone, Brick, Dark dirt, Arched tile, Sand, Terra-cotta, Wooden. Custom Design path: 2,300 Miles. | C | NP-ID; G8-TF; https://nookipedia.com/wiki/Nook_Stop |
| You must stand on grass to lay a path. The Custom Design path works anywhere. | C | NP-ID |
| Soft paths (dirt, dark dirt, sand, grass) still allow dig spots and flowers. Hard paths (stone, brick, arched, terra-cotta, wooden, custom) block digging, planting and rock spawning. | C | NP-ID; iM |
| Corners round (45°) on the edge of a perpendicular path. Custom designs don't round. | C | NP-ID; iM |
| Items can be placed on paths. Whether paths block weeds is undocumented. | U | https://nookipedia.com/wiki/Weeds (silent) |

## 5. Inclines and bridges

| Fact | Tag | Source |
|---|---|---|
| Incline footprint is 2×4: 2×1 on the cliff top plus 2×3 on the ground. | C | https://nookipedia.com/wiki/Incline ; G8-IN; HID src `construction.ts` (`stairs… Size(2,4)`) |
| Inclines are orthogonal only, never diagonal. They need at least 1 free tile all around, so two inclines cannot sit side by side. The entry or exit cannot face water. | C (Game8) | G8-IN |
| Inclines are built from Resident Services (after it is upgraded) and cannot be made with Island Designer. You cannot move one; demolishing costs 10,000 Bells. | C | https://nookipedia.com/wiki/Incline ; G8-TF |
| Incline styles (Bells): Natural ramp 98,000; Blue plank and White plank 128,000; Log and Stone staircase 168,000; Brick 198,000; Blue steel and Red steel 228,000. | C | https://nookipedia.com/wiki/Incline |
| Bridges are always 4 tiles wide, even the log bridge. They span water 3–5 tiles wide. Each bank needs a free 4×1 strip, and the banks must be parallel. | C | G8-BR; HID src (bridge spans 3/4/5 × width 4) |
| Diagonal bridges are allowed when both banks are parallel diagonals. | C | G8-BR; https://www.gamerevolution.com/guides/642684-how-do-i-make-an-animal-crossing-diagonal-bridge ; HID src (`bridgeIconTLBR/TRBL`) |
| Bridges cannot be built next to each other (at least 1 tile apart) or near another river or a cliff. | C (Game8) | G8-BR |
| Bridge styles (Bells): Log 98,000; Suspension 129,800; Stone and Wooden 168,000; Brick 198,000; Iron, Red zen and Zen 228,000. Demolishing costs 10,000. | C | https://nookipedia.com/wiki/Bridge |
| Caps: 8 bridges and 8 inclines, counted separately. The 2.0 Pro Construction License (3,000 Miles, Nook Stop) raises each cap to 10. | C | https://nookipedia.com/wiki/Bridge ; https://nookipedia.com/wiki/Incline ; https://nookipedia.com/wiki/Nook_Stop ; https://www.gfinityesports.com/article/max-bridges-inclines-on-island-version-2 |
| Villagers only go where bridges and inclines connect. Areas reachable only by vaulting pole or ladder are never visited. | C | https://nookipedia.com/wiki/Incline ; https://nookipedia.com/wiki/Bridge |

## 6. Common mistakes and constraints

- **Inclines are scarce.** Each raised area needs one (2×4 plus a 1-tile margin), or villagers never go there. **C**: https://happyislanddesigner.com/blog/terraforming-tips ; G8-IN
- **Plan bridge sites before you shape the river.** You need a straight or 45° stretch 3–5 wide with parallel banks, 4 tiles of free bank on each side, and no cliff or second channel nearby. Lay paths before you place the bridge, or the path cannot reach its edge. **C**: G8-BR; iM
- **Leave room for walking.** Keep 1 tile between a cliff base and water if you want to walk there. There is also a 1-tile buffer between trees and new cliffs or water. **U** for walking (it follows from the tile grid; no explicit rule found). **C** for the tree buffer: GG-CL; GG-WS
- **Clear everything first.** You cannot terraform under furniture, dropped items, flowers, trees or buildings. Move buildings at Resident Services. **C**: iM; G8-TF
- **The 4th tier is decor only.** You can't climb it, put items on it or reach it by incline, so a 3-level waterfall is impossible. **C**: G8-TF; G8-WF
- **HID is not a validator.** It draws 3 land levels and 4 path colours and enforces no gaps. **C**: HID src `layerDefinition.ts`, `colors.ts`
