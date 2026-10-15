# ACNH (ver 2.0): how outdoor furniture placement works

Tags: **C** = CONFIRMED (a cited source says it). **U** = UNSURE (common player knowledge or an inference that no source here states). Reddit and r/ACQR could not be reached: the proxy blocks reddit.com and the search tool refused it. Game8 says version 3.0 and the Switch 2 Edition are now out ([G8-cust](https://game8.co/games/Animal-Crossing-New-Horizons/archives/285831)). Any 3.0 changes to placement have not been checked.

Key sources:
[N-Furn](https://nookipedia.com/wiki/Furniture) · [N-Env](https://nookipedia.com/wiki/Environment_rating) · [N-Cargo](https://nookipedia.com/wiki/Special:CargoTables/nh_furniture) (each item's data; I pulled it with `Special:CargoExport`) · [N-Design](https://nookipedia.com/wiki/Design) · [N-Fence](https://nookipedia.com/wiki/Fence) · [N-2.0](https://nookipedia.com/wiki/Animal_Crossing:_New_Horizons/Update_history/2.0) · [N-IDCP](https://nookipedia.com/wiki/Island_Designer_Construction_Permit) · [G8-glitch](https://game8.co/games/Animal-Crossing-New-Horizons/archives/333945)

## 1. Which item types can go outdoors

| Category | Outdoors? | Source |
|---|---|---|
| Housewares (floor furniture) | Yes. They **cannot be stacked**, except the amp, Bunny Day planter box, floor sign, katana and trash bags | C [N-Furn](https://nookipedia.com/wiki/Furniture) |
| Miscellaneous | Yes, on the ground or **on top of furniture that has a surface** | C [N-Furn](https://nookipedia.com/wiki/Furniture) |
| Wall-mounted | **No, not on the ground.** Outside, the only wall item you can use is a door plaque or wreath on the player's own house door, and it gives no rating points | C [N-Env](https://nookipedia.com/wiki/Environment_rating), [N-Furn](https://nookipedia.com/wiki/Furniture) |
| Rugs | **No**, only inside the player's house | C [N-Rug](https://nookipedia.com/wiki/Rug) |
| Ceiling decor | No. Ceiling items hang from a ceiling, need the Pro Decorating License, and are indoor only | C [N-Furn](https://nookipedia.com/wiki/Furniture), [N-2.0](https://nookipedia.com/wiki/Animal_Crossing:_New_Horizons/Update_history/2.0) |
| Gyroids, fossils, bugs, fish | Yes, they can be placed like furniture | C [N-Furn](https://nookipedia.com/wiki/Furniture) |
| Artwork | Statues are housewares, so yes. Paintings are wall-mounted, so no | U (follows from the category rules above) |
| Models (e.g. ship models) | Miscellaneous, so yes | U (follows from the category rules) |
| Tools | Can only be dropped, not placed. Exception: **ladder set-up kits**, which you place against a cliff and can set on a diagonal corner | C [N-Ladder](https://nookipedia.com/wiki/Ladder_set-up_kit) |

- The "outdoor" field in the item data is **not a placement permission**. It marks items labelled "outdoor furniture" (368 housewares, 57 miscellaneous and 3 wall items), which earn **+0.5 development points**. The simple panel has outdoor=0 and still goes outside. C [N-Env](https://nookipedia.com/wiki/Environment_rating), [N-Cargo](https://nookipedia.com/wiki/Special:CargoTables/nh_furniture)
- Items lying on the ground in their dropped form (not placed) count as trash. Furniture that carries a custom design **cannot be dropped**, but it can still be placed. C [N-Env](https://nookipedia.com/wiki/Environment_rating), [N-Furn](https://nookipedia.com/wiki/Furniture)

## 2. Grid, half tiles, rotation and surfaces

- Footprints run from **1×0.5 up to 3×3** tiles. Furniture "can be pushed in half-tile increments". C [N-Furn](https://nookipedia.com/wiki/Furniture)
- **Outdoors you have no decorating mode.** You place items from your pockets or move them by pushing and pulling them. C [mtmmo](https://www.mtmmo.com/news/495--acnh-table-glitch--how-to-place-items-more-precisely-on-the-table)
- An item placed from your pockets lands on the full tile in front of you. Pushing or pulling can leave it at a half-tile offset; Game8's glitch steps tell you to "leave half a space" between items outdoors. U, supported by [G8-glitch](https://game8.co/games/Animal-Crossing-New-Horizons/archives/333945)
- **Rotation:** grab the item (hold A while facing it) and push the stick sideways. It turns in 4 directions, and this works outdoors. C [Twinfinite](https://twinfinite.net/guides/animal-crossing-new-horizons-rotate-furniture-items/), [Fandom-ACNH](https://acnh.fandom.com/wiki/Town_Decoration?oldid=203)
- **Half-depth items (1×0.5 or 2×0.5)**, taken from the item data: simple panel, short simple panel, steel fence, the furniture "fence", hedge standee, grass standee, wood, bamboo, rope, kiddie, frozen, curtain and LEGO® partitions, safety railing, jail bars, clothesline, clothesline pole, climbing wall, artful screen, low screen, wooden bookshelf, throwback dino screen and bamboo stopblock. C [N-Cargo](https://nookipedia.com/wiki/Special:CargoTables/nh_furniture), [N-SP](https://nookipedia.com/wiki/Item:Simple_panel_(New_Horizons))
  - Can two half-depth items sit back to back on one outdoor tile? **U.** No source found.
- **Tables outdoors:** miscellaneous items do go on surface furniture outdoors. On a 2×2 table **you cannot centre an item without a glitch**. The glitch: push a small flat item against a diagonal cliff edge, climb down the ladder onto it, walk inside the table, then place the item. Game8 says the glitch was still unpatched as of version 2.0.5. C [G8-glitch](https://game8.co/games/Animal-Crossing-New-Horizons/archives/333945)
- Since 2.0, players can walk through gaps between tightly packed furniture. C [N-2.0](https://nookipedia.com/wiki/Animal_Crossing:_New_Horizons/Update_history/2.0)

## 3. Where items cannot go

| Place | Rule | Tag |
|---|---|---|
| Resident Services plaza | You can't place furniture there. The game sometimes places its own fixed items | C [N-Plaza](https://nookipedia.com/wiki/Plaza) |
| Beach sand | Allowed | C (Fandom quote, "including the beach", seen only in a search snippet); [mtmmo builds on the beach](https://www.mtmmo.com/news/524--top-7-simple-panel-buildings-in-acnh-fall-2021--dream-addresses-for-simple-panel-buildings-designs) |
| Next to buildings and rivers | Allowed | C [ACWorld](https://animalcrossingworld.com/2019/09/7-more-new-things-we-missed-in-the-animal-crossing-new-horizons-nintendo-direct-trailer-analysis/) |
| Water, bridges, inclines | Not allowed | U |
| Big beach rock formations, river mouths | Island Designer can't edit them. Furniture there is probably also blocked | C for Island Designer [N-IDCP](https://nookipedia.com/wiki/Island_Designer_Construction_Permit); U for furniture |
| Tile in front of a building's door | Blocked | U |
| Cliff top edge | Items can sit on the edge tile. A multi-tile item can't cover two heights or hang over the edge | U |
| Tiles with flowers or trees | Items can't go on those tiles. Tiles next to a tree are fine | U |
| Paths (any kind) | Allowed | U (common knowledge) |
| Near new cliffs or water | You **cannot build a cliff** next to trees, rocks, buildings, bridges, inclines or furniture. You can't make water next to trees, rocks, buildings, bridges or inclines | C [N-IDCP](https://nookipedia.com/wiki/Island_Designer_Construction_Permit) |

- The Island Designer cleanup service sends placed furniture to the recycle box. C [N-IDCP](https://nookipedia.com/wiki/Island_Designer_Construction_Permit)

## 4. Fences

- To build a fence, equip it from your pockets like a tool. It goes in front of you, **at right angles to the way you face**. Fences next to each other join up automatically, but **never diagonally**. Two fences facing different ways make a corner. You craft them in **stacks of 10**. C [N-Fence](https://nookipedia.com/wiki/Fence)
- There are 30 fence types: corral, vertical-board, country, spiky, barbed-wire, log-wall, log, simple wooden, lattice, large lattice, imperial, brick, stone, iron-and-stone, block, zen, rope, iron, wedding, park, corrugated iron, straw, hedge, bamboo lattice, green bamboo, bamboo-slats, mermaid, spooky, frozen and Bunny Day. C [N-Fence](https://nookipedia.com/wiki/Fence)
- Version 2.0 added 9 fences. **Custom Fencing in a Flash** costs 2,500 Nook Miles and teaches the large lattice and park fence recipes. It shows up only after the customization workshop and after you have crafted 2 fence types. C [N-CFF](https://nookipedia.com/wiki/Item:Custom_Fencing_in_a_Flash_(New_Horizons))
- **Fences you can recolour:** corrugated iron, frozen, iron, large lattice, lattice, park, simple wooden, vertical-board, wedding and zen. C [N-2.0](https://nookipedia.com/wiki/Animal_Crossing:_New_Horizons/Update_history/2.0)
- **Island rating:** each fence gives **0.2 development points**, and a 5-star rating needs a variety of fences. C [N-Env](https://nookipedia.com/wiki/Environment_rating), [N-Fence](https://nookipedia.com/wiki/Fence)
- Fences along cliff edges or on sand: allowed. U
- The "fence" (2×0.5) and "steel fence" are **furniture**, not real fences. The "fence" furniture takes a custom design on its sign. C [N-Cargo](https://nookipedia.com/wiki/Special:CargoTables/nh_furniture)

## 5. Custom designs outdoors

- **Ground:** you can lay designs on the ground through the Custom Designs app. With the custom design path permit you can lay them **anywhere**, while the other path types need a grass tile. "Hard" paths and designs stop digging, flower growth and rock spawns. C [N-IDCP](https://nookipedia.com/wiki/Island_Designer_Construction_Permit), [N-Design](https://nookipedia.com/wiki/Design), [G8-CD](https://game8.co/games/Animal-Crossing-New-Horizons/archives/285797)
- Designs go only on flat walkable ground. They can't go on cliff faces or water, and pro designs can't go on the ground. U
- **Slots:** 90 regular and 90 pro designs as of 1.9.0 (Nookipedia). Game8 says the Pro Editor+ adds 50 of each, giving 200 slots. The two counts conflict. C, with conflict: [N-Design](https://nookipedia.com/wiki/Design), [G8-CD](https://game8.co/games/Animal-Crossing-New-Horizons/archives/285797)
- **Face-cutout standees, umbrellas, uchiwa fans and handheld flags** are pro-design "variety goods" added in 1.9.0. They need the **Custom Design Pro Editor+** (2,000 Nook Miles). Players use standees outdoors as fake doors, walls and shop fronts. C [N-Design](https://nookipedia.com/wiki/Design), [G8-CD](https://game8.co/games/Animal-Crossing-New-Horizons/archives/285797), [G8-standee](https://game8.co/games/Animal-Crossing-New-Horizons/archives/323435)
  - How a standee is placed in the world: U.
  - Umbrellas are held in the hand, not placed.
- The **island flag** design is changed through Isabelle. Transparent pixels show as white. C [N-Flag](https://nookipedia.com/wiki/Flag), [N-Design](https://nookipedia.com/wiki/Design)
- **"Customizable with custom designs"** is the `pattern_custom` field in the item data (226 items). You apply the design at a **DIY workbench** with "Customize something", or Cyrus does it. Editing the design later updates the furniture too. C [G8-cust](https://game8.co/games/Animal-Crossing-New-Horizons/archives/285831), [N-Design](https://nookipedia.com/wiki/Design)
- **Outdoor items that accept a design** (and the part it goes on): simple panel and short simple panel (panel), stall (curtain), wooden box (label), torii (framed item), minicar (sticker), yacht (logo), storage shed (door decoration), outdoor bench, outdoor table, outdoor folding chair, beach chairs with parasol, hammock, clothesline, vertical banner, plain wooden shop sign, standing shop sign, wooden field sign, poster stand, festival lantern, safety barrier, storefront, castle wall, castle tower, street lamp with banners, utility wagon, retro gas pump, retro transportation stop, drink machine, fence (furniture) and curtain partition. C [N-Cargo](https://nookipedia.com/wiki/Special:CargoTables/nh_furniture)
- **Outdoor items that do NOT accept a design:** outdoor kitchen, ironwood kitchenette, tiki torch, hedge and grass standees, and the other partitions. C [N-Cargo](https://nookipedia.com/wiki/Special:CargoTables/nh_furniture)

## 6. Tricks builders use

- **Fake buildings from simple panels:** set panels side by side and put something behind them for height and depth. For roofs, use the imperial fence or an imperial bed. C [mtmmo](https://www.mtmmo.com/news/524--top-7-simple-panel-buildings-in-acnh-fall-2021--dream-addresses-for-simple-panel-buildings-designs)
- **Walls from partitions:** the 0.5-depth items above make thin walls. Use hedge and grass standees as green walls, and face-cutout standees as doors. C [G8-standee](https://game8.co/games/Animal-Crossing-New-Horizons/archives/323435), [N-Cargo](https://nookipedia.com/wiki/Special:CargoTables/nh_furniture)
- **Depth and layering:** place small miscellaneous items on top of large pieces, and mix trees of different growth stages. C [mtmmo build tips](https://www.mtmmo.com/news/784--acnh-build-tips-for-island-decorating-2022-summer--autumn--top-15-best-island-designing-ideas)
- **Camera:** the view is fixed looking north, so tall things in front hide whatever sits directly behind them, including buildings, cliffs and tall panels. Builders hide the backs and edges of items this way. Every building's door faces the camera. U, plus C that buildings can't be rotated: [GameRevolution](https://www.gamerevolution.com/?p=648662)
- **Duplicate penalty:** each extra copy of the **same item** beyond 6 within an 8×8 area costs development points: −0.5 each, or −0.75 from 11 copies. Customization variants still count as the same item. C [N-Env](https://nookipedia.com/wiki/Environment_rating)
- **Item limit:** no fixed cap on outdoor items was found. Lots of items, plants and trees cause frame-rate drops, and Game Revolution recommends cutting down on them. C for lag [GameRevolution](https://www.gamerevolution.com/?p=654485); U that no cap exists
- **Rating points per placed item:** 1 point, +1 if it costs at least 2,000 Bells, +1 more if it costs 20,000 Bells, +0.5 for "outdoor" items and +0.75 for items 3 or more tiles wide. DIY furniture adds 0.25, or 1 if 3 or more tiles wide, to the nature score instead. C [N-Env](https://nookipedia.com/wiki/Environment_rating)
